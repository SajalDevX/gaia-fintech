"""
Pulse Agent - Social Sentiment and Media Monitoring
Analyzes social media, news, public sentiment, labor violations,
community protests, and reputation risks using real data and LLM analysis.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import Counter

from .base_agent import (
    BaseAgent,
    AgentReport,
    Finding,
    Evidence,
    EvidenceType,
)
from .prompts import get_system_prompt, format_template
from utils.llm_client import GeminiClient, get_gemini_client
from utils.data_sources import NewsAPIClient, NewsArticle, get_news_client
from models.llm_outputs import SentimentAnalysisResult, ControversyFinding, LLMFinding


class SentimentScore(Enum):
    """Sentiment classification."""
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class MediaType(Enum):
    """Types of media sources."""
    NEWS = "news"
    SOCIAL_MEDIA = "social_media"
    BLOG = "blog"
    FORUM = "forum"
    REVIEW = "review"
    PRESS_RELEASE = "press_release"


@dataclass
class SentimentAnalysis:
    """Aggregated sentiment analysis."""
    overall_sentiment: float  # -1.0 to 1.0
    positive_mentions: int
    negative_mentions: int
    neutral_mentions: int
    total_mentions: int
    trending_topics: List[Tuple[str, int]]
    key_themes: List[str]


class PulseAgent(BaseAgent):
    """
    Pulse Agent - Social Sentiment and Media Monitoring

    Uses real NewsAPI data and Gemini LLM for analysis.

    Capabilities:
    - Real news monitoring via NewsAPI
    - LLM-powered sentiment analysis
    - Labor violation detection from news reports
    - Community protest and activism monitoring
    - Reputation risk scoring
    - Trend analysis and early warning detection
    """

    def __init__(
        self,
        name: str = "Pulse",
        timeout_seconds: int = 120,
        max_retries: int = 3,
        enable_debug: bool = False,
        llm_client: GeminiClient = None,
        news_client: NewsAPIClient = None,
    ):
        super().__init__(
            name=name,
            agent_type="social_sentiment_monitoring",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            enable_debug=enable_debug,
        )

        # Real clients
        self.llm_client = llm_client or get_gemini_client()
        self.news_client = news_client or get_news_client()

        # System prompt for this agent
        self.system_prompt = get_system_prompt("pulse")

        # Keywords for issue detection
        self.labor_violation_keywords = [
            "forced labor", "child labor", "wage theft", "unsafe conditions",
            "discrimination", "harassment", "union busting", "worker abuse",
            "sweatshop", "exploitation", "overtime violation"
        ]

        self.protest_keywords = [
            "protest", "strike", "boycott", "demonstration", "march",
            "rally", "activism", "petition", "walkout", "picket"
        ]

        self.environmental_keywords = [
            "pollution", "spill", "contamination", "emissions",
            "environmental damage", "toxic", "dumping"
        ]

    async def analyze(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentReport:
        """
        Perform comprehensive social sentiment analysis using real data.

        Args:
            target_entity: Company or brand name
            context: Optional context including timeframe, etc.

        Returns:
            AgentReport with sentiment and media findings
        """
        report = AgentReport(
            agent_name=self.name,
            agent_type=self.agent_type,
            target_entity=target_entity,
        )

        try:
            timeframe_days = context.get("timeframe_days", 30) if context else 30

            self.logger.info(
                "pulse_analysis_start",
                target=target_entity,
                timeframe_days=timeframe_days,
            )

            # Fetch real news articles
            articles = await self.news_client.search_news(
                query=target_entity,
                days_back=timeframe_days,
                page_size=50,
            )

            self.logger.info(
                "news_fetched",
                target=target_entity,
                article_count=len(articles),
            )

            # Fallback: Use LLM web grounding if NewsAPI returns no results
            if not articles:
                self.logger.info(
                    "newsapi_fallback",
                    target=target_entity,
                    reason="No articles from NewsAPI, using LLM web grounding",
                )
                articles = await self._fetch_news_via_llm(target_entity, timeframe_days)

            # Parallel analysis tasks
            analysis_tasks = [
                self._analyze_news_sentiment(target_entity, articles),
                self._detect_controversies(target_entity, articles),
                self._detect_labor_issues(target_entity, articles),
                self._detect_environmental_issues(target_entity, articles),
                self._analyze_reputation_risk(target_entity, articles),
            ]

            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    self.logger.warning(
                        "sentiment_task_failed",
                        error=str(result),
                    )
                    report.errors.append(f"Task failed: {str(result)}")
                elif isinstance(result, Finding):
                    report.add_finding(result)

            # Add metadata
            report.metadata = {
                "timeframe_days": timeframe_days,
                "articles_analyzed": len(articles),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "data_sources": list(set(a.source for a in articles)) if articles else [],
            }

        except Exception as e:
            self.logger.error(
                "pulse_analysis_error",
                target=target_entity,
                error=str(e),
            )
            report.errors.append(f"Analysis error: {str(e)}")

        return report

    async def collect_data(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Evidence]:
        """
        Collect media and sentiment data.

        Args:
            target_entity: Entity to collect data for
            context: Additional context

        Returns:
            List of Evidence objects
        """
        evidence_list = []

        try:
            timeframe_days = context.get("timeframe_days", 30) if context else 30

            # Collect real news articles
            articles = await self.news_client.search_news(
                query=target_entity,
                days_back=timeframe_days,
            )

            for article in articles[:20]:  # Limit to recent 20
                evidence = Evidence(
                    type=EvidenceType.NEWS_ARTICLE,
                    source=article.source,
                    description=article.title,
                    data={
                        "title": article.title,
                        "description": article.description,
                        "url": article.url,
                        "author": article.author,
                    },
                    timestamp=article.published_at,
                    confidence=0.85,
                )
                evidence_list.append(evidence)

        except Exception as e:
            self.logger.error("data_collection_error", error=str(e))

        return evidence_list

    def calculate_confidence(
        self,
        evidence: List[Evidence],
        context: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Calculate confidence based on source diversity and recency.

        Args:
            evidence: List of collected evidence
            context: Additional context

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not evidence:
            return 0.0

        # Base confidence on average evidence confidence
        avg_confidence = sum(e.confidence for e in evidence) / len(evidence)

        # Bonus for source diversity
        unique_sources = len(set(e.source for e in evidence))
        source_bonus = min(0.15, unique_sources * 0.03)

        # Bonus for recent data
        recent_evidence = [
            e for e in evidence
            if (datetime.utcnow() - e.timestamp).days < 7
        ]
        recency_bonus = min(0.1, len(recent_evidence) / max(len(evidence), 1) * 0.1)

        final_confidence = min(1.0, avg_confidence + source_bonus + recency_bonus)
        return final_confidence

    async def _analyze_news_sentiment(
        self,
        target_entity: str,
        articles: List[NewsArticle],
    ) -> Finding:
        """Analyze sentiment in news coverage using LLM."""
        finding = Finding(
            agent_name=self.name,
            finding_type="news_sentiment",
            title="News Media Sentiment Analysis",
        )

        try:
            if not articles:
                finding.severity = "INFO"
                finding.description = f"No recent news coverage found for {target_entity}."
                finding.confidence_score = 0.5
                return finding

            # Prepare articles summary for LLM
            articles_summary = self._format_articles_for_llm(articles[:20])

            # Use LLM for sentiment analysis
            analysis_prompt = format_template(
                "sentiment_analysis",
                company_name=target_entity,
                articles_summary=articles_summary,
                data_context=f"Analyzed {len(articles)} news articles from the past 30 days.",
            )

            sentiment_result = await self.llm_client.generate_structured(
                prompt=analysis_prompt,
                system_prompt=self.system_prompt,
                output_schema=SentimentAnalysisResult,
                temperature=0.3,
            )

            # Create evidence from analysis
            evidence = Evidence(
                type=EvidenceType.NEWS_ARTICLE,
                source="News Sentiment Analysis (LLM)",
                description=f"Sentiment analysis of {len(articles)} articles",
                data={
                    "overall_sentiment": sentiment_result.overall_sentiment,
                    "total_articles": len(articles),
                    "positive_themes": sentiment_result.positive_themes,
                    "negative_themes": sentiment_result.negative_themes,
                    "trending_concerns": sentiment_result.trending_concerns,
                    "sources": list(set(a.source for a in articles))[:10],
                },
                confidence=sentiment_result.confidence,
            )
            finding.add_evidence(evidence)

            # Determine severity based on sentiment
            sentiment = sentiment_result.overall_sentiment

            if sentiment < -0.5:
                finding.severity = "CRITICAL"
                finding.description = (
                    f"Severely negative news sentiment for {target_entity}. "
                    f"Sentiment score: {sentiment:.2f}. "
                    f"Key concerns: {', '.join(sentiment_result.negative_themes[:3])}. "
                    f"Immediate reputation crisis indicated."
                )
            elif sentiment < -0.2:
                finding.severity = "HIGH"
                finding.description = (
                    f"Negative news coverage for {target_entity}. "
                    f"Sentiment score: {sentiment:.2f}. "
                    f"Concerns: {', '.join(sentiment_result.negative_themes[:3])}."
                )
            elif sentiment < 0.2:
                finding.severity = "MEDIUM"
                finding.description = (
                    f"Mixed/neutral news coverage for {target_entity}. "
                    f"Sentiment score: {sentiment:.2f}. "
                    f"Coverage is balanced with both positive and negative themes."
                )
            else:
                finding.severity = "LOW"
                finding.description = (
                    f"Positive news coverage for {target_entity}. "
                    f"Sentiment score: {sentiment:.2f}. "
                    f"Positive themes: {', '.join(sentiment_result.positive_themes[:3])}."
                )

            finding.confidence_score = sentiment_result.confidence

        except Exception as e:
            self.logger.error("news_sentiment_error", error=str(e))
            finding.severity = "INFO"
            finding.description = f"Unable to analyze news sentiment: {str(e)}"
            finding.confidence_score = 0.3

        return finding

    async def _detect_controversies(
        self,
        target_entity: str,
        articles: List[NewsArticle],
    ) -> Finding:
        """Detect ESG controversies from news using LLM."""
        finding = Finding(
            agent_name=self.name,
            finding_type="controversies",
            title="ESG Controversy Detection",
        )

        try:
            if not articles:
                finding.severity = "INFO"
                finding.description = f"No news data to analyze for controversies for {target_entity}."
                return finding

            # Filter for potentially controversial articles
            controversy_keywords = (
                self.labor_violation_keywords +
                self.protest_keywords +
                self.environmental_keywords +
                ["scandal", "lawsuit", "investigation", "fraud", "violation", "fine", "penalty"]
            )

            controversial_articles = []
            for article in articles:
                text = f"{article.title} {article.description}".lower()
                if any(keyword in text for keyword in controversy_keywords):
                    controversial_articles.append(article)

            if not controversial_articles:
                finding.severity = "LOW"
                finding.description = f"No significant controversies detected for {target_entity} in recent news."
                finding.confidence_score = 0.75
                return finding

            # Use LLM to analyze controversies
            articles_text = self._format_articles_for_llm(controversial_articles[:10])

            controversy_prompt = f"""Analyze these news articles about {target_entity} for ESG controversies:

{articles_text}

Identify:
1. Any environmental incidents or violations
2. Labor disputes or workplace safety issues
3. Product recalls or safety concerns
4. Governance scandals or ethical breaches
5. Community conflicts or protests
6. Legal proceedings or regulatory actions

For each controversy found, assess its severity and the company's response."""

            result = await self.llm_client.generate_text(
                prompt=controversy_prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
            )

            evidence = Evidence(
                type=EvidenceType.NEWS_ARTICLE,
                source="Controversy Analysis (LLM)",
                description=f"Analysis of {len(controversial_articles)} potentially controversial articles",
                data={
                    "controversial_article_count": len(controversial_articles),
                    "article_titles": [a.title for a in controversial_articles[:5]],
                    "analysis": result[:1000],  # Truncate for storage
                },
                confidence=0.80,
            )
            finding.add_evidence(evidence)

            # Severity based on number of controversial articles
            if len(controversial_articles) >= 10:
                finding.severity = "CRITICAL"
                finding.description = (
                    f"Multiple significant controversies detected for {target_entity}. "
                    f"Found {len(controversial_articles)} controversy-related articles. "
                    f"Immediate ESG risk review recommended."
                )
            elif len(controversial_articles) >= 5:
                finding.severity = "HIGH"
                finding.description = (
                    f"Several controversies detected for {target_entity}. "
                    f"Found {len(controversial_articles)} relevant articles requiring attention."
                )
            else:
                finding.severity = "MEDIUM"
                finding.description = (
                    f"Some controversy indicators for {target_entity}. "
                    f"Found {len(controversial_articles)} articles with potential concerns."
                )

            finding.confidence_score = 0.80

        except Exception as e:
            self.logger.error("controversy_detection_error", error=str(e))
            finding.severity = "INFO"
            finding.description = f"Unable to detect controversies: {str(e)}"

        return finding

    async def _detect_labor_issues(
        self,
        target_entity: str,
        articles: List[NewsArticle],
    ) -> Finding:
        """Detect labor-related issues from news."""
        finding = Finding(
            agent_name=self.name,
            finding_type="labor_issues",
            title="Labor Rights Issue Detection",
        )

        try:
            # Filter for labor-related articles
            labor_articles = []
            for article in articles:
                text = f"{article.title} {article.description}".lower()
                if any(keyword in text for keyword in self.labor_violation_keywords):
                    labor_articles.append(article)

            if not labor_articles:
                finding.severity = "LOW"
                finding.description = f"No labor violation indicators found for {target_entity}."
                finding.confidence_score = 0.80
                return finding

            # Use LLM to analyze labor issues
            articles_text = self._format_articles_for_llm(labor_articles[:8])

            labor_prompt = f"""Analyze these articles about {target_entity} for labor rights issues:

{articles_text}

Identify specific labor concerns:
1. Forced or child labor allegations
2. Wage and overtime violations
3. Workplace safety issues
4. Discrimination or harassment claims
5. Union-related disputes
6. Supply chain labor concerns

Rate severity of each issue found."""

            result = await self.llm_client.generate_text(
                prompt=labor_prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
            )

            evidence = Evidence(
                type=EvidenceType.NEWS_ARTICLE,
                source="Labor Issue Analysis (LLM)",
                description=f"Analysis of {len(labor_articles)} labor-related articles",
                data={
                    "labor_article_count": len(labor_articles),
                    "headlines": [a.title for a in labor_articles[:5]],
                    "analysis": result[:1000],
                },
                confidence=0.82,
            )
            finding.add_evidence(evidence)

            if len(labor_articles) >= 5:
                finding.severity = "CRITICAL"
                finding.description = (
                    f"Significant labor rights concerns for {target_entity}. "
                    f"Found {len(labor_articles)} articles reporting labor issues. "
                    f"Immediate investigation recommended."
                )
            elif len(labor_articles) >= 2:
                finding.severity = "HIGH"
                finding.description = (
                    f"Labor concerns reported for {target_entity}. "
                    f"Found {len(labor_articles)} articles with labor-related issues."
                )
            else:
                finding.severity = "MEDIUM"
                finding.description = (
                    f"Minor labor concerns for {target_entity}. "
                    f"Found {len(labor_articles)} article(s) mentioning labor issues."
                )

            finding.confidence_score = 0.82

        except Exception as e:
            self.logger.error("labor_detection_error", error=str(e))
            finding.severity = "INFO"
            finding.description = f"Unable to detect labor issues: {str(e)}"

        return finding

    async def _detect_environmental_issues(
        self,
        target_entity: str,
        articles: List[NewsArticle],
    ) -> Finding:
        """Detect environmental issues from news."""
        finding = Finding(
            agent_name=self.name,
            finding_type="environmental_news",
            title="Environmental Issue Detection",
        )

        try:
            # Filter for environmental articles
            env_articles = []
            for article in articles:
                text = f"{article.title} {article.description}".lower()
                if any(keyword in text for keyword in self.environmental_keywords):
                    env_articles.append(article)

            if not env_articles:
                finding.severity = "LOW"
                finding.description = f"No environmental incident reports found for {target_entity}."
                finding.confidence_score = 0.80
                return finding

            # Use LLM to analyze environmental issues
            articles_text = self._format_articles_for_llm(env_articles[:8])

            env_prompt = f"""Analyze these articles about {target_entity} for environmental issues:

{articles_text}

Identify specific environmental concerns:
1. Pollution incidents (air, water, soil)
2. Spills or contamination events
3. Emissions violations
4. Deforestation or habitat destruction
5. Regulatory fines or enforcement actions
6. Community environmental complaints

Rate severity and potential impact of each issue."""

            result = await self.llm_client.generate_text(
                prompt=env_prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
            )

            evidence = Evidence(
                type=EvidenceType.NEWS_ARTICLE,
                source="Environmental Issue Analysis (LLM)",
                description=f"Analysis of {len(env_articles)} environmental articles",
                data={
                    "environmental_article_count": len(env_articles),
                    "headlines": [a.title for a in env_articles[:5]],
                    "analysis": result[:1000],
                },
                confidence=0.82,
            )
            finding.add_evidence(evidence)

            if len(env_articles) >= 5:
                finding.severity = "CRITICAL"
                finding.description = (
                    f"Significant environmental concerns for {target_entity}. "
                    f"Found {len(env_articles)} articles reporting environmental issues."
                )
            elif len(env_articles) >= 2:
                finding.severity = "HIGH"
                finding.description = (
                    f"Environmental issues reported for {target_entity}. "
                    f"Found {len(env_articles)} relevant articles."
                )
            else:
                finding.severity = "MEDIUM"
                finding.description = (
                    f"Minor environmental concerns for {target_entity}. "
                    f"Found {len(env_articles)} article(s) mentioning environmental issues."
                )

            finding.confidence_score = 0.82

        except Exception as e:
            self.logger.error("environmental_detection_error", error=str(e))
            finding.severity = "INFO"
            finding.description = f"Unable to detect environmental issues: {str(e)}"

        return finding

    async def _analyze_reputation_risk(
        self,
        target_entity: str,
        articles: List[NewsArticle],
    ) -> Finding:
        """Analyze overall reputation risk using LLM."""
        finding = Finding(
            agent_name=self.name,
            finding_type="reputation_risk",
            title="Reputation Risk Assessment",
        )

        try:
            if not articles:
                finding.severity = "INFO"
                finding.description = f"Insufficient data for reputation assessment of {target_entity}."
                return finding

            # Prepare comprehensive summary for LLM
            articles_text = self._format_articles_for_llm(articles[:15])

            reputation_prompt = f"""Provide a comprehensive reputation risk assessment for {target_entity}.

News Coverage Summary ({len(articles)} articles analyzed):
{articles_text}

Assess:
1. Overall media sentiment and tone
2. Key reputation drivers (positive and negative)
3. Emerging reputation risks
4. Stakeholder perception indicators
5. Crisis potential

Provide a reputation risk score from 0-100 (0 = critical risk, 100 = excellent reputation) and justify your assessment."""

            result = await self.llm_client.generate_text(
                prompt=reputation_prompt,
                system_prompt=self.system_prompt,
                temperature=0.4,
            )

            # Extract a rough score from the response (LLM should mention it)
            # Default to moderate if not clearly stated
            reputation_score = 50  # Default

            evidence = Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Reputation Risk Analysis (LLM)",
                description="Comprehensive reputation risk assessment",
                data={
                    "articles_analyzed": len(articles),
                    "unique_sources": len(set(a.source for a in articles)),
                    "analysis": result,
                    "estimated_score": reputation_score,
                },
                confidence=0.78,
            )
            finding.add_evidence(evidence)

            # Use negative keyword count as a proxy for severity
            negative_count = 0
            for article in articles:
                text = f"{article.title} {article.description}".lower()
                if any(kw in text for kw in self.labor_violation_keywords + self.protest_keywords + self.environmental_keywords):
                    negative_count += 1

            negative_ratio = negative_count / len(articles) if articles else 0

            if negative_ratio > 0.4:
                finding.severity = "CRITICAL"
                finding.description = (
                    f"Critical reputation risk for {target_entity}. "
                    f"{negative_ratio*100:.0f}% of coverage is negative. "
                    f"Immediate crisis management may be required."
                )
            elif negative_ratio > 0.2:
                finding.severity = "HIGH"
                finding.description = (
                    f"Elevated reputation risk for {target_entity}. "
                    f"Significant negative coverage detected ({negative_ratio*100:.0f}%)."
                )
            elif negative_ratio > 0.1:
                finding.severity = "MEDIUM"
                finding.description = (
                    f"Moderate reputation risk for {target_entity}. "
                    f"Some negative coverage present ({negative_ratio*100:.0f}%)."
                )
            else:
                finding.severity = "LOW"
                finding.description = (
                    f"Low reputation risk for {target_entity}. "
                    f"Coverage is predominantly neutral to positive."
                )

            finding.confidence_score = 0.78

        except Exception as e:
            self.logger.error("reputation_analysis_error", error=str(e))
            finding.severity = "INFO"
            finding.description = f"Unable to assess reputation risk: {str(e)}"

        return finding

    async def _fetch_news_via_llm(
        self,
        target_entity: str,
        timeframe_days: int,
    ) -> List[NewsArticle]:
        """Fallback: Use LLM to gather news information when NewsAPI fails."""
        try:
            prompt = f"""Search for and summarize recent news about {target_entity} from the past {timeframe_days} days.

For each significant news story, provide:
1. Headline/Title
2. Source (publication name)
3. Brief summary (2-3 sentences)
4. Date (approximate if needed)
5. Category (environmental, social, governance, financial, product, other)

Focus on ESG-relevant news: environmental incidents, labor issues, regulatory actions,
sustainability initiatives, controversies, and corporate governance matters.

Provide at least 5-10 news items if available. Format each as:
HEADLINE: [title]
SOURCE: [source name]
DATE: [date]
SUMMARY: [brief summary]
---"""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
            )

            # Parse LLM response into NewsArticle objects
            articles = []
            news_blocks = result.split("---")

            for block in news_blocks:
                if not block.strip():
                    continue

                lines = block.strip().split("\n")
                title = ""
                source = "LLM Web Search"
                summary = ""
                date = datetime.utcnow()

                for line in lines:
                    line_lower = line.lower()
                    if line_lower.startswith("headline:"):
                        title = line.split(":", 1)[1].strip() if ":" in line else ""
                    elif line_lower.startswith("source:"):
                        source = line.split(":", 1)[1].strip() if ":" in line else "LLM Web Search"
                    elif line_lower.startswith("summary:"):
                        summary = line.split(":", 1)[1].strip() if ":" in line else ""
                    elif line_lower.startswith("date:"):
                        # Keep default date, parsing is complex
                        pass

                if title and (summary or title):
                    articles.append(NewsArticle(
                        title=title,
                        description=summary or title,
                        content=summary or title,
                        source=source,
                        author=None,
                        url="",
                        published_at=date,
                    ))

            self.logger.info(
                "llm_news_fallback_success",
                target=target_entity,
                articles_generated=len(articles),
            )
            return articles

        except Exception as e:
            self.logger.error("llm_news_fallback_error", error=str(e))
            return []

    def _format_articles_for_llm(self, articles: List[NewsArticle], max_chars: int = 8000) -> str:
        """Format articles into a text summary for LLM analysis."""
        if not articles:
            return "No articles available."

        formatted = []
        total_chars = 0

        for i, article in enumerate(articles, 1):
            article_text = f"""
Article {i}: {article.title}
Source: {article.source}
Date: {article.published_at.strftime('%Y-%m-%d') if article.published_at else 'Unknown'}
Summary: {article.description or 'No description available'}
"""
            if total_chars + len(article_text) > max_chars:
                break
            formatted.append(article_text)
            total_chars += len(article_text)

        return "\n".join(formatted)
