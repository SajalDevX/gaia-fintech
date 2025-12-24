"""
NEXUS Agent - Financial Inclusion Intelligence

New Economy eXpansion & Underserved Services Agent

Uses Gemini LLM to analyze financial inclusion impact on underserved populations.
Addresses SDG 1 (No Poverty), SDG 5 (Gender Equality), SDG 8 (Decent Work),
SDG 9 (Industry/Innovation), SDG 10 (Reduced Inequalities).
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from .base_agent import (
    BaseAgent,
    AgentReport,
    Finding,
    Evidence,
    EvidenceType,
)
from .prompts import get_system_prompt
from utils.llm_client import GeminiClient, get_gemini_client
from utils.data_sources import NewsAPIClient, get_news_client


@dataclass
class InclusionMetrics:
    """Financial inclusion metrics."""
    access_score: float = 50.0
    credit_score: float = 50.0
    gender_score: float = 50.0
    geographic_score: float = 50.0
    vulnerable_score: float = 50.0
    affordability_score: float = 50.0
    overall_score: float = 50.0


@dataclass
class InclusionWashingIndicator:
    """Indicator of potential inclusion washing."""
    indicator_name: str
    description: str
    severity: str
    evidence: str
    recommendation: str


class NexusAgent(BaseAgent):
    """
    NEXUS Agent: Financial Inclusion Intelligence

    Uses Gemini LLM to analyze company's impact on financial inclusion.

    Key Capabilities:
    1. Access Analysis - Who can reach financial services?
    2. Credit Analysis - Who can borrow at fair terms?
    3. Gender Analysis - Are women equally served?
    4. Geographic Analysis - Are rural/remote areas covered?
    5. Vulnerable Population Analysis - Are the most vulnerable protected?
    6. Affordability Analysis - Can low-income people afford services?
    7. Inclusion Washing Detection - Are claims authentic?
    """

    def __init__(
        self,
        name: str = "NEXUS",
        timeout_seconds: int = 120,
        max_retries: int = 3,
        enable_debug: bool = False,
        llm_client: GeminiClient = None,
        news_client: NewsAPIClient = None,
    ):
        super().__init__(
            name=name,
            agent_type="financial_inclusion",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            enable_debug=enable_debug,
        )

        self.llm_client = llm_client or get_gemini_client()
        self.news_client = news_client or get_news_client()
        self.system_prompt = get_system_prompt("nexus")

        # Weights for calculating overall inclusion score
        self.score_weights = {
            "access": 0.20,
            "credit": 0.20,
            "gender": 0.15,
            "geographic": 0.15,
            "vulnerable": 0.15,
            "affordability": 0.15
        }

    async def analyze(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentReport:
        """Perform comprehensive financial inclusion analysis."""
        report = AgentReport(
            agent_name=self.name,
            agent_type=self.agent_type,
            target_entity=target_entity,
        )

        try:
            ticker = context.get("ticker", target_entity) if context else target_entity
            industry = context.get("industry", "Unknown") if context else "Unknown"

            self.logger.info("nexus_analysis_start", target=target_entity)

            # Fetch news for context
            news_articles = await self._fetch_inclusion_news(target_entity)

            # Parallel LLM analysis
            analysis_tasks = [
                self._analyze_financial_access(target_entity, industry),
                self._analyze_credit_inclusion(target_entity, industry),
                self._analyze_gender_inclusion(target_entity, industry),
                self._analyze_geographic_reach(target_entity, industry),
                self._analyze_vulnerable_populations(target_entity, industry),
                self._analyze_affordability(target_entity, industry),
                self._detect_inclusion_washing(target_entity, industry, news_articles),
            ]

            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    report.errors.append(f"Task failed: {str(result)}")
                elif isinstance(result, Finding):
                    report.add_finding(result)

            report.metadata = {
                "ticker": ticker,
                "industry": industry,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "news_articles_analyzed": len(news_articles),
            }

        except Exception as e:
            self.logger.error("nexus_analysis_error", error=str(e))
            report.errors.append(f"Analysis error: {str(e)}")

        return report

    async def collect_data(self, target_entity: str, context: Optional[Dict[str, Any]] = None) -> List[Evidence]:
        """Collect financial inclusion data."""
        evidence_list = []
        try:
            articles = await self.news_client.search_news(
                query=f"{target_entity} financial inclusion underserved",
                max_results=10
            )
            for article in articles[:5]:
                evidence = Evidence(
                    type=EvidenceType.NEWS_ARTICLE,
                    source=article.source,
                    description=article.title,
                    data={"url": article.url},
                    timestamp=article.published_at,
                    confidence=0.70,
                )
                evidence_list.append(evidence)
        except Exception as e:
            self.logger.error("data_collection_error", error=str(e))
        return evidence_list

    def calculate_confidence(self, evidence: List[Evidence], context: Optional[Dict[str, Any]] = None) -> float:
        if not evidence:
            return 0.0
        return min(1.0, sum(e.confidence for e in evidence) / len(evidence) + 0.1)

    async def _fetch_inclusion_news(self, target_entity: str) -> List[Any]:
        """Fetch news about financial inclusion."""
        try:
            articles = await self.news_client.search_news(
                query=f"{target_entity} financial inclusion microfinance",
                max_results=10
            )
            return articles
        except Exception:
            return []

    async def _analyze_financial_access(self, target_entity: str, industry: str) -> Finding:
        """Analyze financial access metrics."""
        finding = Finding(
            agent_name=self.name,
            finding_type="financial_access",
            title="Financial Access Analysis"
        )

        try:
            prompt = f"""Analyze {target_entity}'s impact on financial access for underserved populations.

Industry: {industry}

Assess:
1. Unbanked individuals reached (estimate per $1M invested)
2. New accounts opened for previously unbanked
3. Mobile money/digital wallet accessibility
4. Agent banking network reach
5. Last-mile service delivery

Rate access inclusion: EXCELLENT (90+), GOOD (70-89), MODERATE (50-69), POOR (<50).
Provide specific metrics where available."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Access Analysis (LLM)",
                description="Financial access assessment",
                data={"analysis": result},
                confidence=0.75,
            ))

            result_lower = result.lower()
            if "excellent" in result_lower or "strong" in result_lower:
                finding.severity = "LOW"
                finding.description = f"Strong financial access impact for {target_entity}."
            elif "good" in result_lower or "moderate" in result_lower:
                finding.severity = "INFO"
                finding.description = f"Moderate financial access impact for {target_entity}."
            else:
                finding.severity = "MEDIUM"
                finding.description = f"Limited financial access impact for {target_entity}."

            finding.confidence_score = 0.75

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _analyze_credit_inclusion(self, target_entity: str, industry: str) -> Finding:
        """Analyze credit inclusion metrics."""
        finding = Finding(
            agent_name=self.name,
            finding_type="credit_inclusion",
            title="Credit Inclusion Analysis"
        )

        try:
            prompt = f"""Analyze {target_entity}'s impact on credit inclusion for underserved populations.

Industry: {industry}

Assess:
1. Microloans disbursed (estimate per $1M)
2. First-time borrowers reached
3. SME loans to underserved entrepreneurs
4. Interest rate fairness vs market rates
5. Alternative credit scoring adoption
6. Loan approval rates for underserved
7. Portfolio quality (PAR30)

Rate credit inclusion: EXCELLENT, GOOD, MODERATE, or POOR.
Flag any predatory lending concerns."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Credit Analysis (LLM)",
                description="Credit inclusion assessment",
                data={"analysis": result},
                confidence=0.73,
            ))

            result_lower = result.lower()
            if "predatory" in result_lower or "exploitative" in result_lower:
                finding.severity = "HIGH"
                finding.description = f"Predatory lending concerns for {target_entity}."
            elif "excellent" in result_lower or "good" in result_lower:
                finding.severity = "LOW"
                finding.description = f"Good credit inclusion for {target_entity}."
            else:
                finding.severity = "INFO"
                finding.description = f"Credit inclusion assessed for {target_entity}."

            finding.confidence_score = 0.73

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _analyze_gender_inclusion(self, target_entity: str, industry: str) -> Finding:
        """Analyze gender-based financial inclusion."""
        finding = Finding(
            agent_name=self.name,
            finding_type="gender_inclusion",
            title="Gender Inclusion Analysis"
        )

        try:
            prompt = f"""Analyze {target_entity}'s gender-based financial inclusion (SDG 5).

Industry: {industry}

Assess:
1. Women account holders (% and per $1M)
2. Women entrepreneurs funded
3. Female-headed household loans
4. Gender parity index (0-1, where 1 is parity)
5. Women in company leadership
6. Women-specific product offerings
7. Maternity-friendly loan terms

Rate gender inclusion: EXCELLENT, GOOD, MODERATE, or POOR.
Identify any gender gaps or discrimination patterns."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Gender Analysis (LLM)",
                description="Gender inclusion assessment",
                data={"analysis": result},
                confidence=0.72,
            ))

            result_lower = result.lower()
            if "discrimination" in result_lower or "gap" in result_lower:
                finding.severity = "MEDIUM"
                finding.description = f"Gender inclusion gaps identified for {target_entity}."
            elif "excellent" in result_lower or "parity" in result_lower:
                finding.severity = "LOW"
                finding.description = f"Strong gender inclusion for {target_entity}."
            else:
                finding.severity = "INFO"
                finding.description = f"Gender inclusion assessed for {target_entity}."

            finding.confidence_score = 0.72

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _analyze_geographic_reach(self, target_entity: str, industry: str) -> Finding:
        """Analyze geographic financial inclusion."""
        finding = Finding(
            agent_name=self.name,
            finding_type="geographic_inclusion",
            title="Geographic Reach Analysis"
        )

        try:
            prompt = f"""Analyze {target_entity}'s geographic financial inclusion reach.

Industry: {industry}

Assess:
1. Rural population coverage (%)
2. Remote/last-mile communities reached
3. Urban slum coverage
4. Agent network distribution
5. Digital infrastructure reach
6. Remittance corridors served
7. Travel time reduction for users

Rate geographic inclusion: EXCELLENT, GOOD, MODERATE, or POOR.
Identify underserved regions."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Geographic Analysis (LLM)",
                description="Geographic reach assessment",
                data={"analysis": result},
                confidence=0.70,
            ))

            result_lower = result.lower()
            if "limited" in result_lower or "poor" in result_lower:
                finding.severity = "MEDIUM"
                finding.description = f"Limited geographic reach for {target_entity}."
            elif "excellent" in result_lower or "extensive" in result_lower:
                finding.severity = "LOW"
                finding.description = f"Strong geographic inclusion for {target_entity}."
            else:
                finding.severity = "INFO"
                finding.description = f"Geographic reach assessed for {target_entity}."

            finding.confidence_score = 0.70

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _analyze_vulnerable_populations(self, target_entity: str, industry: str) -> Finding:
        """Analyze services for vulnerable populations."""
        finding = Finding(
            agent_name=self.name,
            finding_type="vulnerable_populations",
            title="Vulnerable Population Services"
        )

        try:
            prompt = f"""Analyze {target_entity}'s services for vulnerable populations.

Industry: {industry}

Assess services for:
1. Refugees and displaced persons
2. People with disabilities (accessibility)
3. Youth (financial literacy, starter products)
4. Elderly (pension services, accessibility)
5. Gig/informal workers
6. Smallholder farmers

For each:
- Specific products/services offered
- Number reached (if available)
- Accessibility features
- Pricing fairness

Rate vulnerable population inclusion: EXCELLENT, GOOD, MODERATE, or POOR."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Vulnerable Population Analysis (LLM)",
                description="Vulnerable population assessment",
                data={"analysis": result},
                confidence=0.70,
            ))

            result_lower = result.lower()
            if "excellent" in result_lower or "strong" in result_lower:
                finding.severity = "LOW"
                finding.description = f"Good vulnerable population services for {target_entity}."
            elif "limited" in result_lower or "poor" in result_lower:
                finding.severity = "MEDIUM"
                finding.description = f"Limited vulnerable population services for {target_entity}."
            else:
                finding.severity = "INFO"
                finding.description = f"Vulnerable population services assessed for {target_entity}."

            finding.confidence_score = 0.70

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _analyze_affordability(self, target_entity: str, industry: str) -> Finding:
        """Analyze affordability of financial services."""
        finding = Finding(
            agent_name=self.name,
            finding_type="affordability",
            title="Affordability Analysis"
        )

        try:
            prompt = f"""Analyze the affordability of {target_entity}'s financial services.

Industry: {industry}

Assess:
1. Zero-balance account availability
2. Zero-fee basic account options
3. Average monthly fees vs local minimum wage
4. Transaction costs as % of transaction
5. Microloan effective annual rates
6. Flexible repayment options
7. Fee transparency
8. Local language availability

Rate affordability: EXCELLENT, GOOD, MODERATE, or POOR.
Flag any pricing that may burden low-income users."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Affordability Analysis (LLM)",
                description="Affordability assessment",
                data={"analysis": result},
                confidence=0.72,
            ))

            result_lower = result.lower()
            if "burden" in result_lower or "expensive" in result_lower or "poor" in result_lower:
                finding.severity = "MEDIUM"
                finding.description = f"Affordability concerns for {target_entity}."
            elif "excellent" in result_lower or "affordable" in result_lower:
                finding.severity = "LOW"
                finding.description = f"Good affordability for {target_entity}."
            else:
                finding.severity = "INFO"
                finding.description = f"Affordability assessed for {target_entity}."

            finding.confidence_score = 0.72

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _detect_inclusion_washing(
        self, target_entity: str, industry: str, news_articles: List[Any]
    ) -> Finding:
        """Detect potential inclusion washing."""
        finding = Finding(
            agent_name=self.name,
            finding_type="inclusion_washing",
            title="Inclusion Washing Detection"
        )

        try:
            news_context = ""
            if news_articles:
                headlines = [getattr(a, 'title', str(a)) for a in news_articles[:5]]
                news_context = f"Recent news:\n" + "\n".join(f"- {h}" for h in headlines)

            prompt = f"""Analyze {target_entity} ({industry}) for potential "inclusion washing" -
exaggerated or misleading claims about serving underserved populations.

{news_context}

Check for:
1. Impact inflation - claims far exceeding verifiable metrics
2. Cherry-picked geography - highlighting one success region
3. Token women's products - marketing without substance
4. Predatory pricing disguised as inclusion
5. Phantom financial literacy - marketing as education
6. Access point inflation - counting inactive service points

Rate inclusion washing risk: CRITICAL, HIGH, MEDIUM, or LOW.
Provide specific red flags if found."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Inclusion Washing Detection (LLM)",
                description="Inclusion authenticity assessment",
                data={"analysis": result},
                confidence=0.75,
            ))

            result_lower = result.lower()
            if "critical" in result_lower or "high risk" in result_lower:
                finding.severity = "HIGH"
                finding.description = f"High inclusion washing risk for {target_entity}."
            elif "medium" in result_lower or "moderate" in result_lower:
                finding.severity = "MEDIUM"
                finding.description = f"Moderate inclusion washing concerns for {target_entity}."
            else:
                finding.severity = "LOW"
                finding.description = f"Low inclusion washing risk for {target_entity}."

            finding.confidence_score = 0.75

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to assess: {str(e)}"

        return finding

    def calculate_inclusion_score(self, report: AgentReport) -> Dict[str, Any]:
        """Calculate overall financial inclusion score."""
        if not report.findings:
            return {
                "overall_score": 50.0,
                "grade": "C",
            }

        severity_scores = {"LOW": 85, "INFO": 65, "MEDIUM": 45, "HIGH": 25, "CRITICAL": 10}
        total_score = sum(severity_scores.get(f.severity, 50) for f in report.findings)
        avg_score = total_score / len(report.findings)

        if avg_score >= 90:
            grade = "A+"
        elif avg_score >= 85:
            grade = "A"
        elif avg_score >= 80:
            grade = "A-"
        elif avg_score >= 75:
            grade = "B+"
        elif avg_score >= 70:
            grade = "B"
        elif avg_score >= 65:
            grade = "B-"
        elif avg_score >= 60:
            grade = "C+"
        elif avg_score >= 55:
            grade = "C"
        elif avg_score >= 50:
            grade = "C-"
        else:
            grade = "D"

        return {
            "overall_score": avg_score,
            "grade": grade,
            "findings_count": len(report.findings),
        }
