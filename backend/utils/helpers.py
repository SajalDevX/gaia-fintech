"""
GAIA Helper Utilities
Common utility functions used across the application
"""

import asyncio
import hashlib
import json
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar
from functools import wraps
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("gaia")

T = TypeVar('T')


def generate_id(prefix: str = "") -> str:
    """Generate a unique identifier with optional prefix."""
    unique_id = str(uuid.uuid4())[:8]
    return f"{prefix}_{unique_id}" if prefix else unique_id


def generate_hash(data: Any) -> str:
    """Generate SHA-256 hash of data."""
    if isinstance(data, dict):
        data = json.dumps(data, sort_keys=True, default=str)
    elif not isinstance(data, str):
        data = str(data)
    return hashlib.sha256(data.encode()).hexdigest()


def timestamp_to_iso(timestamp: float) -> str:
    """Convert Unix timestamp to ISO format string."""
    return datetime.fromtimestamp(timestamp).isoformat()


def iso_to_timestamp(iso_string: str) -> float:
    """Convert ISO format string to Unix timestamp."""
    return datetime.fromisoformat(iso_string).timestamp()


def calculate_confidence(
    base_confidence: float,
    evidence_count: int,
    source_reliability: float = 0.8,
    corroboration_bonus: float = 0.05
) -> float:
    """
    Calculate adjusted confidence score based on evidence.

    Args:
        base_confidence: Initial confidence (0-1)
        evidence_count: Number of evidence pieces
        source_reliability: Reliability of primary source (0-1)
        corroboration_bonus: Bonus per corroborating evidence

    Returns:
        Adjusted confidence score (0-1)
    """
    # Apply source reliability
    adjusted = base_confidence * source_reliability

    # Add corroboration bonus (diminishing returns)
    for i in range(min(evidence_count - 1, 5)):
        adjusted += corroboration_bonus * (0.8 ** i)

    return min(0.99, adjusted)


def normalize_score(
    value: float,
    min_val: float = 0,
    max_val: float = 100,
    target_min: float = 0,
    target_max: float = 100
) -> float:
    """Normalize a value to a target range."""
    if max_val == min_val:
        return target_min

    normalized = (value - min_val) / (max_val - min_val)
    return target_min + normalized * (target_max - target_min)


def weighted_average(
    values: List[float],
    weights: Optional[List[float]] = None
) -> float:
    """Calculate weighted average of values."""
    if not values:
        return 0.0

    if weights is None:
        weights = [1.0] * len(values)

    if len(values) != len(weights):
        raise ValueError("Values and weights must have same length")

    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0

    return sum(v * w for v, w in zip(values, weights)) / total_weight


def merge_findings(findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple agent findings into a consolidated view."""
    if not findings:
        return {}

    merged = {
        "sources": [],
        "evidence": [],
        "scores": {},
        "issues": [],
        "timestamp": datetime.now().isoformat()
    }

    for finding in findings:
        # Collect sources
        if "source" in finding:
            merged["sources"].append(finding["source"])

        # Collect evidence
        if "evidence" in finding:
            if isinstance(finding["evidence"], list):
                merged["evidence"].extend(finding["evidence"])
            else:
                merged["evidence"].append(finding["evidence"])

        # Merge scores (average if duplicate keys)
        if "scores" in finding:
            for key, value in finding["scores"].items():
                if key in merged["scores"]:
                    merged["scores"][key] = (merged["scores"][key] + value) / 2
                else:
                    merged["scores"][key] = value

        # Collect issues
        if "issues" in finding:
            merged["issues"].extend(finding["issues"])

    # Deduplicate issues
    seen = set()
    unique_issues = []
    for issue in merged["issues"]:
        issue_key = json.dumps(issue, sort_keys=True)
        if issue_key not in seen:
            seen.add(issue_key)
            unique_issues.append(issue)
    merged["issues"] = unique_issues

    return merged


def async_retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Decorator for retrying async functions with exponential backoff."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}"
                    )
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff

            raise last_exception

        return wrapper
    return decorator


def rate_limiter(calls: int, period: float):
    """Simple rate limiter decorator."""
    timestamps: List[float] = []

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            nonlocal timestamps
            now = time.time()

            # Remove old timestamps
            timestamps = [t for t in timestamps if now - t < period]

            if len(timestamps) >= calls:
                sleep_time = period - (now - timestamps[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            timestamps.append(time.time())
            return await func(*args, **kwargs)

        return wrapper
    return decorator


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string."""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥"}
    symbol = symbols.get(currency, currency + " ")

    if amount >= 1_000_000_000_000:
        return f"{symbol}{amount / 1_000_000_000_000:.2f}T"
    elif amount >= 1_000_000_000:
        return f"{symbol}{amount / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"{symbol}{amount / 1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"{symbol}{amount / 1_000:.2f}K"
    else:
        return f"{symbol}{amount:.2f}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage string."""
    return f"{value:.{decimals}f}%"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_company_name(name: str) -> str:
    """Clean and standardize company name."""
    # Remove common suffixes
    suffixes = [
        " Inc.", " Inc", " Corp.", " Corp", " Corporation",
        " Ltd.", " Ltd", " Limited", " LLC", " L.L.C.",
        " PLC", " plc", " S.A.", " SA", " AG", " N.V.",
        " Co.", " Co", " Company", " Group"
    ]

    cleaned = name.strip()
    for suffix in suffixes:
        if cleaned.endswith(suffix):
            cleaned = cleaned[:-len(suffix)]

    return cleaned.strip()


def extract_ticker(text: str) -> Optional[str]:
    """Extract stock ticker from text."""
    import re

    # Match patterns like $AAPL or AAPL: or (AAPL)
    patterns = [
        r'\$([A-Z]{1,5})',
        r'\(([A-Z]{1,5})\)',
        r'([A-Z]{1,5}):',
        r'\b([A-Z]{2,5})\b'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    return None


class Timer:
    """Context manager for timing code blocks."""

    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time: float = 0
        self.end_time: float = 0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, *args):
        self.end_time = time.time()
        logger.info(f"{self.name} completed in {self.elapsed:.3f}s")

    @property
    def elapsed(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time


class EventEmitter:
    """Simple async event emitter for agent communication."""

    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def on(self, event: str, callback: Callable):
        """Register event listener."""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)

    def off(self, event: str, callback: Callable):
        """Remove event listener."""
        if event in self._listeners:
            self._listeners[event].remove(callback)

    async def emit(self, event: str, *args, **kwargs):
        """Emit event to all listeners."""
        if event in self._listeners:
            for callback in self._listeners[event]:
                if asyncio.iscoroutinefunction(callback):
                    await callback(*args, **kwargs)
                else:
                    callback(*args, **kwargs)
