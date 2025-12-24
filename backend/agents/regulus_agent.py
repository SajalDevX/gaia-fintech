"""
Regulus Agent - Regulatory Compliance Intelligence
Monitors global regulations, predicts regulatory actions,
and tracks enforcement patterns using LLM-powered analysis.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from .base_agent import (
    BaseAgent,
    AgentReport,
    Finding,
    Evidence,
    EvidenceType,
)
from .prompts import get_system_prompt
from utils.llm_client import GeminiClient, get_gemini_client
from utils.data_sources import SECEdgarClient, get_sec_client, NewsAPIClient, get_news_client


@dataclass
class RegulatorySignal:
    """Political and regulatory signals."""
    signal_type: str
    jurisdiction: str
    topic: str
    likelihood: float
    impact: str
    timeline: str
    description: str


class RegulusAgent(BaseAgent):
    """
    Regulatory Compliance Agent - Regulus

    Uses Gemini LLM and real data sources to analyze regulatory compliance.

    Capabilities:
    - Monitor regulations across jurisdictions
    - Predict regulatory actions using LLM analysis
    - Track enforcement patterns and trends
    - Calculate comprehensive compliance scores
    - Analyze political signals for regulatory changes
    """

    def __init__(
        self,
        name: str = "Regulus",
        timeout_seconds: int = 120,
        max_retries: int = 3,
        enable_debug: bool = False,
        llm_client: GeminiClient = None,
        sec_client: SECEdgarClient = None,
        news_client: NewsAPIClient = None,
    ):
        super().__init__(
            name=name,
            agent_type="regulatory_compliance",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            enable_debug=enable_debug,
        )

        self.llm_client = llm_client or get_gemini_client()
        self.sec_client = sec_client or get_sec_client()
        self.news_client = news_client or get_news_client()
        self.system_prompt = get_system_prompt("regulus")

        # Regulatory topics to monitor
        self.regulatory_topics = [
            "environmental_compliance",
            "labor_standards",
            "data_privacy",
            "financial_reporting",
            "product_safety",
            "anti_corruption",
            "tax_compliance",
            "trade_sanctions",
            "antitrust",
            "supply_chain_transparency",
        ]

    async def analyze(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentReport:
        """Perform comprehensive regulatory compliance analysis."""
        report = AgentReport(
            agent_name=self.name,
            agent_type=self.agent_type,
            target_entity=target_entity,
        )

        try:
            ticker = context.get("ticker", target_entity) if context else target_entity
            industry = context.get("industry", "Unknown") if context else "Unknown"

            self.logger.info("regulus_analysis_start", target=target_entity)

            # Fetch real data in parallel
            sec_data, news_data = await asyncio.gather(
                self._fetch_sec_filings(ticker),
                self._fetch_regulatory_news(target_entity),
                return_exceptions=True
            )

            # Handle exceptions
            sec_filings = sec_data if not isinstance(sec_data, Exception) else None
            news_articles = news_data if not isinstance(news_data, Exception) else []

            # Parallel LLM analysis
            analysis_tasks = [
                self._analyze_compliance_status(target_entity, industry, sec_filings),
                self._analyze_enforcement_history(target_entity, industry, news_articles),
                self._predict_regulatory_changes(target_entity, industry),
                self._analyze_jurisdiction_risks(target_entity, industry),
                self._analyze_political_signals(target_entity, industry),
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
                "sec_filings_analyzed": len(sec_filings) if sec_filings else 0,
                "news_articles_analyzed": len(news_articles),
                "analysis_timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            self.logger.error("regulus_analysis_error", error=str(e))
            report.errors.append(f"Analysis error: {str(e)}")

        return report

    async def collect_data(self, target_entity: str, context: Optional[Dict[str, Any]] = None) -> List[Evidence]:
        """Collect regulatory data."""
        evidence_list = []
        try:
            ticker = context.get("ticker", target_entity) if context else target_entity

            # Get SEC filings
            filings = await self.sec_client.get_recent_filings(
                ticker=ticker,
                filing_types=["10-K", "8-K", "DEF 14A"],
                limit=5
            )
            for filing in filings:
                evidence = Evidence(
                    type=EvidenceType.PUBLIC_RECORD,
                    source=f"SEC EDGAR - {filing.filing_type}",
                    description=f"{filing.filing_type} regulatory filing",
                    data={"url": filing.document_url},
                    timestamp=filing.filing_date,
                    confidence=0.92,
                )
                evidence_list.append(evidence)

            # Get regulatory news
            articles = await self.news_client.search_news(
                query=f"{target_entity} regulation compliance",
                max_results=10
            )
            for article in articles[:5]:
                evidence = Evidence(
                    type=EvidenceType.NEWS_ARTICLE,
                    source=article.source,
                    description=article.title,
                    data={"url": article.url, "summary": article.description},
                    timestamp=article.published_at,
                    confidence=0.75,
                )
                evidence_list.append(evidence)

        except Exception as e:
            self.logger.error("data_collection_error", error=str(e))
        return evidence_list

    def calculate_confidence(self, evidence: List[Evidence], context: Optional[Dict[str, Any]] = None) -> float:
        if not evidence:
            return 0.0
        type_weights = {
            EvidenceType.PUBLIC_RECORD: 1.0,
            EvidenceType.API_RESPONSE: 0.9,
            EvidenceType.NEWS_ARTICLE: 0.75,
        }
        total_confidence = 0.0
        total_weight = 0.0
        for e in evidence:
            weight = type_weights.get(e.type, 0.5)
            total_confidence += e.confidence * weight
            total_weight += weight
        return min(1.0, total_confidence / total_weight if total_weight > 0 else 0.0)

    async def _fetch_sec_filings(self, ticker: str) -> Optional[List[Any]]:
        """Fetch SEC filings."""
        try:
            filings = await self.sec_client.get_recent_filings(
                ticker=ticker,
                filing_types=["10-K", "8-K"],
                limit=3
            )
            return filings
        except Exception:
            return None

    async def _fetch_regulatory_news(self, target_entity: str) -> List[Any]:
        """Fetch regulatory news."""
        try:
            articles = await self.news_client.search_news(
                query=f"{target_entity} regulation violation fine penalty",
                max_results=15
            )
            return articles
        except Exception:
            return []

    async def _analyze_compliance_status(
        self, target_entity: str, industry: str, sec_filings: Optional[List[Any]]
    ) -> Finding:
        """Analyze current compliance status."""
        finding = Finding(
            agent_name=self.name,
            finding_type="compliance_status",
            title="Regulatory Compliance Status"
        )

        try:
            filing_context = ""
            if sec_filings:
                filing_context = f"Recent SEC filings found: {len(sec_filings)} filings available."

            prompt = f"""Analyze the regulatory compliance status for {target_entity} in {industry} industry.

{filing_context}

Assess:
1. Overall compliance posture
2. Key regulatory frameworks they must comply with
3. Potential compliance gaps based on industry
4. Risk of regulatory violations

Rate compliance risk: CRITICAL (major violations), HIGH (significant gaps), MEDIUM (some concerns), LOW (good compliance)."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Compliance Analysis (LLM)",
                description="Regulatory compliance assessment",
                data={"analysis": result},
                confidence=0.78,
            ))

            result_lower = result.lower()
            if "major violation" in result_lower or "non-compliant" in result_lower:
                finding.severity = "CRITICAL"
                finding.description = f"Critical compliance issues identified for {target_entity}."
            elif "significant" in result_lower or "gaps" in result_lower:
                finding.severity = "HIGH"
                finding.description = f"Significant compliance gaps for {target_entity}."
            elif "minor" in result_lower or "some concerns" in result_lower:
                finding.severity = "MEDIUM"
                finding.description = f"Some compliance concerns for {target_entity}."
            else:
                finding.severity = "LOW"
                finding.description = f"Good regulatory compliance for {target_entity}."

            finding.confidence_score = 0.78

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _analyze_enforcement_history(
        self, target_entity: str, industry: str, news_articles: List[Any]
    ) -> Finding:
        """Analyze enforcement history."""
        finding = Finding(
            agent_name=self.name,
            finding_type="enforcement_history",
            title="Enforcement Actions Analysis"
        )

        try:
            news_context = ""
            if news_articles:
                headlines = [a.title for a in news_articles[:10]]
                news_context = f"Recent news headlines:\n" + "\n".join(f"- {h}" for h in headlines)

            prompt = f"""Analyze the regulatory enforcement history for {target_entity} ({industry}).

{news_context}

Assess:
1. Past enforcement actions, fines, or penalties
2. Frequency and severity of violations
3. Patterns in regulatory issues
4. Company response to enforcement actions

Rate enforcement risk: CRITICAL, HIGH, MEDIUM, or LOW."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Enforcement Analysis (LLM)",
                description="Enforcement history assessment",
                data={"analysis": result, "articles_analyzed": len(news_articles)},
                confidence=0.75,
            ))

            result_lower = result.lower()
            if "multiple" in result_lower and ("fine" in result_lower or "penalty" in result_lower):
                finding.severity = "HIGH"
                finding.description = f"Multiple enforcement actions found for {target_entity}."
            elif "fine" in result_lower or "penalty" in result_lower or "violation" in result_lower:
                finding.severity = "MEDIUM"
                finding.description = f"Some enforcement actions found for {target_entity}."
            else:
                finding.severity = "LOW"
                finding.description = f"Clean enforcement record for {target_entity}."

            finding.confidence_score = 0.75

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _predict_regulatory_changes(self, target_entity: str, industry: str) -> Finding:
        """Predict upcoming regulatory changes."""
        finding = Finding(
            agent_name=self.name,
            finding_type="regulatory_prediction",
            title="Regulatory Change Predictions"
        )

        try:
            prompt = f"""Predict upcoming regulatory changes that may affect {target_entity} ({industry}).

Consider:
1. Pending legislation and proposed rules
2. Industry-specific regulatory trends
3. Global regulatory harmonization
4. Emerging regulatory areas (AI, ESG, data privacy, climate)

For each prediction, assess:
- Likelihood (high/medium/low)
- Timeline (immediate/near-term/medium-term)
- Impact on company (high/medium/low)

Focus on the most likely and impactful changes."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.4
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Regulatory Prediction (LLM)",
                description="Regulatory change forecast",
                data={"analysis": result},
                confidence=0.70,
            ))

            result_lower = result.lower()
            if "high impact" in result_lower and "high likelihood" in result_lower:
                finding.severity = "MEDIUM"
                finding.description = f"Significant regulatory changes predicted for {target_entity}."
            else:
                finding.severity = "INFO"
                finding.description = f"Regulatory outlook for {target_entity}."

            finding.confidence_score = 0.70

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to predict: {str(e)}"

        return finding

    async def _analyze_jurisdiction_risks(self, target_entity: str, industry: str) -> Finding:
        """Analyze jurisdiction-specific risks."""
        finding = Finding(
            agent_name=self.name,
            finding_type="jurisdiction_risk",
            title="Jurisdiction Risk Analysis"
        )

        try:
            prompt = f"""Analyze jurisdiction-specific regulatory risks for {target_entity} ({industry}).

Assess risks in key jurisdictions:
1. United States (SEC, EPA, FTC, DOJ)
2. European Union (GDPR, CSRD, EU Taxonomy)
3. United Kingdom (FCA, Environment Agency)
4. China (CSRC, environmental regulations)
5. Other relevant jurisdictions

For each:
- Regulatory stringency level
- Recent enforcement trends
- Specific compliance requirements
- Cross-border compliance challenges

Rate overall jurisdiction risk: CRITICAL, HIGH, MEDIUM, LOW."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Jurisdiction Analysis (LLM)",
                description="Multi-jurisdiction risk assessment",
                data={"analysis": result},
                confidence=0.72,
            ))

            result_lower = result.lower()
            if "critical" in result_lower or "high risk" in result_lower:
                finding.severity = "HIGH"
                finding.description = f"High jurisdiction risks for {target_entity}."
            elif "medium" in result_lower or "moderate" in result_lower:
                finding.severity = "MEDIUM"
                finding.description = f"Moderate jurisdiction risks for {target_entity}."
            else:
                finding.severity = "LOW"
                finding.description = f"Manageable jurisdiction risks for {target_entity}."

            finding.confidence_score = 0.72

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _analyze_political_signals(self, target_entity: str, industry: str) -> Finding:
        """Analyze political signals for regulatory changes."""
        finding = Finding(
            agent_name=self.name,
            finding_type="political_signals",
            title="Political & Legislative Signals"
        )

        try:
            prompt = f"""Analyze political and legislative signals affecting {target_entity} ({industry}).

Consider:
1. Current administration's regulatory priorities
2. Pending legislation relevant to the industry
3. Political climate around ESG and sustainability
4. Lobbying activities and industry associations
5. Election impacts on regulatory direction

Identify key signals that may affect regulatory environment.
Rate political/regulatory risk: HIGH, MEDIUM, or LOW."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.4
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Political Analysis (LLM)",
                description="Political signals assessment",
                data={"analysis": result},
                confidence=0.68,
            ))

            finding.severity = "INFO"
            finding.description = f"Political and legislative signals analyzed for {target_entity}."
            finding.confidence_score = 0.68

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    def calculate_compliance_score(self, report: AgentReport) -> Dict[str, Any]:
        """Calculate comprehensive compliance score."""
        if not report.findings:
            return {
                "compliance_score": 75.0,
                "grade": "B",
                "risk_level": "moderate",
            }

        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for finding in report.findings:
            severity_counts[finding.severity] += 1

        base_score = 100.0
        base_score -= severity_counts["CRITICAL"] * 20
        base_score -= severity_counts["HIGH"] * 10
        base_score -= severity_counts["MEDIUM"] * 5
        base_score -= severity_counts["LOW"] * 2

        compliance_score = max(0.0, min(100.0, base_score))

        if compliance_score >= 90:
            grade = "A"
        elif compliance_score >= 80:
            grade = "B"
        elif compliance_score >= 70:
            grade = "C"
        elif compliance_score >= 60:
            grade = "D"
        else:
            grade = "F"

        if compliance_score >= 80:
            risk_level = "low"
        elif compliance_score >= 60:
            risk_level = "moderate"
        elif compliance_score >= 40:
            risk_level = "high"
        else:
            risk_level = "critical"

        return {
            "compliance_score": compliance_score,
            "grade": grade,
            "risk_level": risk_level,
            "severity_distribution": severity_counts,
            "total_findings": len(report.findings),
        }
