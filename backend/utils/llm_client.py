"""
Multi-Provider LLM Client for GAIA
Supports Gemini, OpenAI GPT-4o, and Claude with load balancing to distribute costs.
"""

import asyncio
import hashlib
import json
import time
import random
from typing import Any, Dict, List, Optional, Type, TypeVar
from datetime import datetime
from enum import Enum

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from pydantic import BaseModel
import structlog
import httpx

from config import get_settings

logger = structlog.get_logger()
settings = get_settings()

T = TypeVar("T", bound=BaseModel)


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    GEMINI = "gemini"
    OPENAI = "openai"
    CLAUDE = "claude"


class RateLimiter:
    """Simple token bucket rate limiter for async operations."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.tokens = requests_per_minute
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Acquire a token, waiting if necessary."""
        async with self._lock:
            now = time.monotonic()
            time_passed = now - self.last_refill
            self.tokens = min(
                self.requests_per_minute,
                self.tokens + time_passed * (self.requests_per_minute / 60)
            )
            self.last_refill = now

            if self.tokens < 1:
                wait_time = (1 - self.tokens) * (60 / self.requests_per_minute)
                await asyncio.sleep(wait_time)
                self.tokens = 1

            self.tokens -= 1


class ResponseCache:
    """Simple TTL cache for LLM responses."""

    def __init__(self, ttl_seconds: int = 3600):
        self.ttl = ttl_seconds
        self._cache: Dict[str, tuple] = {}
        self._lock = asyncio.Lock()

    def _generate_key(self, prompt: str, system_prompt: str, model: str) -> str:
        content = f"{model}:{system_prompt}:{prompt}"
        return hashlib.sha256(content.encode()).hexdigest()

    async def get(self, prompt: str, system_prompt: str, model: str) -> Optional[Any]:
        key = self._generate_key(prompt, system_prompt, model)
        async with self._lock:
            if key in self._cache:
                value, timestamp = self._cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
                del self._cache[key]
            return None

    async def set(self, prompt: str, system_prompt: str, model: str, value: Any):
        key = self._generate_key(prompt, system_prompt, model)
        async with self._lock:
            self._cache[key] = (value, time.time())
            if len(self._cache) > 1000:
                await self._cleanup()

    async def _cleanup(self):
        now = time.time()
        expired = [k for k, (_, ts) in self._cache.items() if now - ts >= self.ttl]
        for key in expired:
            del self._cache[key]


class OpenAIClient:
    """OpenAI GPT-4o client."""

    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Generate text using OpenAI API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]


class ClaudeClient:
    """Anthropic Claude client."""

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-20241022"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1/messages"

    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Generate text using Claude API."""
        async with httpx.AsyncClient(timeout=120.0) as client:
            body = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }
            if system_prompt:
                body["system"] = system_prompt

            response = await client.post(
                self.base_url,
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01",
                },
                json=body,
            )
            response.raise_for_status()
            data = response.json()
            return data["content"][0]["text"]


class GeminiClient:
    """Google Gemini client."""

    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model_name = model or settings.GEMINI_MODEL
        self.pro_model_name = settings.GEMINI_PRO_MODEL

        if api_key:
            genai.configure(api_key=api_key)

        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

    def _get_model(self, use_pro: bool = False) -> genai.GenerativeModel:
        model_name = self.pro_model_name if use_pro else self.model_name
        return genai.GenerativeModel(
            model_name=model_name,
            safety_settings=self.safety_settings,
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        use_pro: bool = False,
    ) -> str:
        """Generate text using Gemini API."""
        model = self._get_model(use_pro=use_pro)

        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        response = await asyncio.to_thread(
            model.generate_content,
            full_prompt,
            generation_config=generation_config,
        )
        return response.text


class MultiProviderLLMClient:
    """
    Multi-provider LLM client with load balancing.

    Distributes requests across Gemini, OpenAI, and Claude to:
    - Reduce costs by using cheaper models when possible
    - Avoid rate limits by spreading load
    - Improve reliability through fallback
    """

    def __init__(
        self,
        gemini_key: str = None,
        openai_key: str = None,
        claude_key: str = None,
        strategy: str = "round_robin",  # round_robin, random, weighted
        cache_ttl: int = None,
    ):
        self.providers: Dict[LLMProvider, Any] = {}
        self.provider_list: List[LLMProvider] = []
        self._current_index = 0
        self._lock = asyncio.Lock()

        # LLM call limiting
        self._call_count = 0
        self._max_calls = getattr(settings, 'MAX_LLM_CALLS_PER_ANALYSIS', 10)
        self._call_limit_enabled = True

        # Initialize available providers
        gemini_key = gemini_key or settings.GOOGLE_GEMINI_API_KEY
        openai_key = openai_key or getattr(settings, 'OPENAI_API_KEY', None)
        claude_key = claude_key or getattr(settings, 'ANTHROPIC_API_KEY', None)

        if gemini_key:
            self.providers[LLMProvider.GEMINI] = GeminiClient(api_key=gemini_key)
            self.provider_list.append(LLMProvider.GEMINI)
            logger.info("llm_provider_initialized", provider="Gemini")

        if openai_key:
            self.providers[LLMProvider.OPENAI] = OpenAIClient(api_key=openai_key)
            self.provider_list.append(LLMProvider.OPENAI)
            logger.info("llm_provider_initialized", provider="OpenAI")

        if claude_key:
            self.providers[LLMProvider.CLAUDE] = ClaudeClient(api_key=claude_key)
            self.provider_list.append(LLMProvider.CLAUDE)
            logger.info("llm_provider_initialized", provider="Claude")

        if not self.provider_list:
            logger.warning("no_llm_providers", message="No LLM API keys configured!")

        self.strategy = strategy
        self.cache = ResponseCache(cache_ttl or settings.GEMINI_CACHE_TTL)
        self.rate_limiters = {p: RateLimiter(60) for p in self.provider_list}
        self.max_retries = settings.GEMINI_MAX_RETRIES
        self.retry_delay = settings.GEMINI_RETRY_DELAY

        # Provider weights for weighted strategy (lower cost = higher weight)
        self.weights = {
            LLMProvider.GEMINI: 0.5,   # Cheapest
            LLMProvider.CLAUDE: 0.3,   # Haiku is cheap
            LLMProvider.OPENAI: 0.2,   # GPT-4o is more expensive
        }

    def reset_call_count(self):
        """Reset the LLM call counter. Call this at the start of each analysis."""
        self._call_count = 0
        logger.info("llm_call_count_reset")

    def get_call_count(self) -> int:
        """Get the current LLM call count."""
        return self._call_count

    def is_call_limit_reached(self) -> bool:
        """Check if the call limit has been reached."""
        return self._call_limit_enabled and self._call_count >= self._max_calls

    def set_call_limit(self, limit: int):
        """Set the maximum number of LLM calls allowed."""
        self._max_calls = limit

    async def _get_next_provider(self) -> LLMProvider:
        """Get next provider based on strategy."""
        if not self.provider_list:
            raise ValueError("No LLM providers available")

        async with self._lock:
            if self.strategy == "round_robin":
                provider = self.provider_list[self._current_index % len(self.provider_list)]
                self._current_index += 1
                return provider
            elif self.strategy == "random":
                return random.choice(self.provider_list)
            elif self.strategy == "weighted":
                # Weighted random selection
                available_weights = {
                    p: self.weights.get(p, 0.33)
                    for p in self.provider_list
                }
                total = sum(available_weights.values())
                r = random.uniform(0, total)
                cumulative = 0
                for provider, weight in available_weights.items():
                    cumulative += weight
                    if r <= cumulative:
                        return provider
                return self.provider_list[0]
            else:
                return self.provider_list[0]

    async def _call_provider(
        self,
        provider: LLMProvider,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Call a specific provider."""
        client = self.providers[provider]

        # Rate limit
        if provider in self.rate_limiters:
            await self.rate_limiters[provider].acquire()

        return await client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    async def generate_text(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        use_pro: bool = False,
        use_cache: bool = True,
        preferred_provider: LLMProvider = None,
    ) -> str:
        """
        Generate text using load-balanced providers.

        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            use_pro: Use pro/better model variant
            use_cache: Whether to use caching
            preferred_provider: Force a specific provider

        Returns:
            Generated text response
        """
        # Check call limit
        if self.is_call_limit_reached():
            logger.warning(
                "llm_call_limit_reached",
                count=self._call_count,
                limit=self._max_calls
            )
            return "[Analysis limit reached - using cached/default response]"

        # Check cache
        cache_key = f"multi:{prompt[:100]}"
        if use_cache:
            cached = await self.cache.get(cache_key, system_prompt or "", "multi")
            if cached:
                return cached

        # Try providers with fallback
        errors = []
        providers_to_try = []

        if preferred_provider and preferred_provider in self.providers:
            providers_to_try.append(preferred_provider)
        else:
            # Add primary provider
            primary = await self._get_next_provider()
            providers_to_try.append(primary)

        # Add fallbacks (all other providers)
        for p in self.provider_list:
            if p not in providers_to_try:
                providers_to_try.append(p)

        for provider in providers_to_try:
            try:
                logger.info("llm_attempt", provider=provider.value, prompt_len=len(prompt))

                result = await self._call_provider(
                    provider=provider,
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                # Increment call counter
                self._call_count += 1

                # Cache result
                if use_cache:
                    await self.cache.set(cache_key, system_prompt or "", "multi", result)

                logger.info(
                    "llm_success",
                    provider=provider.value,
                    response_len=len(result),
                    call_count=self._call_count,
                    call_limit=self._max_calls,
                )
                return result

            except Exception as e:
                error_msg = f"{provider.value}: {str(e)}"
                errors.append(error_msg)
                logger.warning("llm_provider_failed", provider=provider.value, error=str(e))
                continue

        # All providers failed
        raise RuntimeError(f"All LLM providers failed: {'; '.join(errors)}")

    async def generate_structured(
        self,
        prompt: str,
        system_prompt: str,
        output_schema: Type[T],
        temperature: float = 0.3,
        use_pro: bool = False,
        use_cache: bool = True,
    ) -> T:
        """Generate structured output conforming to a Pydantic model."""
        schema_json = json.dumps(output_schema.model_json_schema(), indent=2)

        structured_prompt = f"""{prompt}

You MUST respond with a valid JSON object that conforms to this schema:
```json
{schema_json}
```

Respond ONLY with the JSON object, no additional text or markdown formatting."""

        enhanced_system_prompt = f"""{system_prompt}

IMPORTANT: You must respond with valid JSON only. No explanations, no markdown code blocks, just the raw JSON object."""

        raw_response = await self.generate_text(
            prompt=structured_prompt,
            system_prompt=enhanced_system_prompt,
            temperature=temperature,
            use_pro=use_pro,
            use_cache=use_cache,
        )

        # Parse JSON response
        try:
            json_str = raw_response.strip()
            if json_str.startswith("```"):
                lines = json_str.split("\n")
                json_str = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

            data = json.loads(json_str)
            return output_schema.model_validate(data)

        except json.JSONDecodeError as e:
            logger.error("llm_json_parse_error", error=str(e), response=raw_response[:200])
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")

    async def analyze_with_search(
        self,
        query: str,
        context: str = None,
        use_pro: bool = False,
    ) -> Dict[str, Any]:
        """Analyze a topic using LLM knowledge."""
        system_prompt = """You are a research analyst with comprehensive knowledge.
Analyze the given query and provide detailed, factual information.
Include specific data points, dates, and sources where known."""

        analysis_prompt = f"""Research and analyze the following:

Query: {query}
{f"Additional Context: {context}" if context else ""}

Provide a comprehensive analysis including:
1. Key findings and facts
2. Relevant data points and statistics
3. Recent developments (if known)
4. Potential concerns or risks"""

        response = await self.generate_text(
            prompt=analysis_prompt,
            system_prompt=system_prompt,
            use_pro=use_pro,
            temperature=0.5,
        )

        return {
            "query": query,
            "analysis": response,
            "timestamp": datetime.utcnow().isoformat(),
        }


# Singleton instances
_gemini_client: Optional[GeminiClient] = None
_multi_client: Optional[MultiProviderLLMClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create the Gemini client instance (for backward compatibility)."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient(api_key=settings.GOOGLE_GEMINI_API_KEY)
    return _gemini_client


def get_multi_llm_client(
    gemini_key: str = None,
    openai_key: str = None,
    claude_key: str = None,
) -> MultiProviderLLMClient:
    """Get or create the multi-provider LLM client."""
    global _multi_client
    if _multi_client is None:
        _multi_client = MultiProviderLLMClient(
            gemini_key=gemini_key,
            openai_key=openai_key,
            claude_key=claude_key,
            strategy="round_robin",
        )
    return _multi_client


# Alias for easy migration
def get_llm_client() -> MultiProviderLLMClient:
    """Get the default LLM client (multi-provider)."""
    return get_multi_llm_client()
