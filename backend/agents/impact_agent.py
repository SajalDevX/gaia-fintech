"""
Impact Agent - SDG Impact Quantification
Maps investments to UN Sustainable Development Goals (SDG) outcomes and quantifies
measurable impact metrics using LLM-powered analysis.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
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
from utils.data_sources import AlphaVantageClient, get_alpha_vantage_client


@dataclass
class SDGMetrics:
    """Metrics for a specific SDG goal."""
    goal_number: int
    goal_name: str
    alignment_score: float
    contribution_level: str
    primary_indicators: List[str] = field(default_factory=list)


@dataclass
class ImpactMetric:
    """Quantified impact metric."""
    metric_name: str
    value: float
    unit: str
    per_million_usd: float
    confidence: float


class ImpactAgent(BaseAgent):
    """
    SDG Impact Quantification Agent

    Uses Gemini LLM to analyze and quantify SDG impact.

    Capabilities:
    - Map investments to UN SDG outcomes (all 17 goals)
    - Quantify impact per dollar invested using LLM analysis
    - Generate comprehensive impact reports
    - Detect impact washing
    """

    def __init__(
        self,
        name: str = "ImpactQuantifier",
        timeout_seconds: int = 120,
        max_retries: int = 3,
        enable_debug: bool = False,
        llm_client: GeminiClient = None,
        finance_client: AlphaVantageClient = None,
    ):
        super().__init__(
            name=name,
            agent_type="sdg_impact_quantification",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            enable_debug=enable_debug,
        )

        self.llm_client = llm_client or get_gemini_client()
        self.finance_client = finance_client or get_alpha_vantage_client()
        self.system_prompt = get_system_prompt("impact")

        # SDG goals mapping
        self.sdg_goals = {
            1: "No Poverty",
            2: "Zero Hunger",
            3: "Good Health and Well-being",
            4: "Quality Education",
            5: "Gender Equality",
            6: "Clean Water and Sanitation",
            7: "Affordable and Clean Energy",
            8: "Decent Work and Economic Growth",
            9: "Industry, Innovation and Infrastructure",
            10: "Reduced Inequalities",
            11: "Sustainable Cities and Communities",
            12: "Responsible Consumption and Production",
            13: "Climate Action",
            14: "Life Below Water",
            15: "Life on Land",
            16: "Peace, Justice and Strong Institutions",
            17: "Partnerships for the Goals",
        }

    async def analyze(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentReport:
        """Perform SDG impact quantification analysis."""
        report = AgentReport(
            agent_name=self.name,
            agent_type=self.agent_type,
            target_entity=target_entity,
        )

        try:
            ticker = context.get("ticker", target_entity) if context else target_entity
            industry = context.get("industry", "Unknown") if context else "Unknown"

            self.logger.info("impact_analysis_start", target=target_entity)

            # Fetch company data
            company_data = await self._fetch_company_data(ticker)

            # Parallel LLM analysis
            analysis_tasks = [
                self._analyze_sdg_alignment(target_entity, industry, company_data),
                self._quantify_environmental_impact(target_entity, industry),
                self._quantify_social_impact(target_entity, industry),
                self._analyze_impact_pathways(target_entity, industry),
                self._detect_impact_washing(target_entity, industry),
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
            }

        except Exception as e:
            self.logger.error("impact_analysis_error", error=str(e))
            report.errors.append(f"Analysis error: {str(e)}")

        return report

    async def collect_data(self, target_entity: str, context: Optional[Dict[str, Any]] = None) -> List[Evidence]:
        """Collect impact-related data."""
        evidence_list = []
        try:
            ticker = context.get("ticker", target_entity) if context else target_entity

            # Get company overview
            overview = await self.finance_client.get_company_overview(ticker)
            if overview:
                evidence = Evidence(
                    type=EvidenceType.API_RESPONSE,
                    source="Alpha Vantage",
                    description="Company financial overview",
                    data=overview,
                    confidence=0.85,
                )
                evidence_list.append(evidence)

        except Exception as e:
            self.logger.error("data_collection_error", error=str(e))
        return evidence_list

    def calculate_confidence(self, evidence: List[Evidence], context: Optional[Dict[str, Any]] = None) -> float:
        if not evidence:
            return 0.0
        return min(1.0, sum(e.confidence for e in evidence) / len(evidence) + 0.1)

    async def _fetch_company_data(self, ticker: str) -> Optional[Dict]:
        """Fetch company financial data."""
        try:
            overview = await self.finance_client.get_company_overview(ticker)
            return overview
        except Exception:
            return None

    async def _analyze_sdg_alignment(
        self, target_entity: str, industry: str, company_data: Optional[Dict]
    ) -> Finding:
        """Analyze SDG alignment."""
        finding = Finding(
            agent_name=self.name,
            finding_type="sdg_alignment",
            title="SDG Goal Alignment Analysis"
        )

        try:
            company_context = ""
            if company_data:
                # CompanyFinancials is a dataclass, access attributes directly
                company_context = f"Company description: {company_data.description or 'N/A'}"
                company_context += f"\nSector: {company_data.sector or 'N/A'}"

            prompt = f"""Analyze {target_entity}'s alignment with UN Sustainable Development Goals.

Industry: {industry}
{company_context}

For each relevant SDG (1-17), assess:
1. Alignment score (0-100)
2. Contribution level (negative, neutral, low, medium, high)
3. Key indicators of alignment
4. Primary positive contributions
5. Potential negative impacts

Focus on the 5-8 most relevant SDGs for this company.
Provide specific, evidence-based assessments."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="SDG Analysis (LLM)",
                description="SDG alignment assessment",
                data={"analysis": result},
                confidence=0.78,
            ))

            # Count positive SDG mentions
            result_lower = result.lower()
            high_count = result_lower.count("high")
            medium_count = result_lower.count("medium")

            if high_count >= 3:
                finding.severity = "LOW"  # Low risk = good alignment
                finding.description = f"Strong SDG alignment for {target_entity} with multiple high-impact areas."
            elif high_count >= 1 or medium_count >= 3:
                finding.severity = "INFO"
                finding.description = f"Moderate SDG alignment for {target_entity}."
            else:
                finding.severity = "MEDIUM"
                finding.description = f"Limited SDG alignment for {target_entity}."

            finding.confidence_score = 0.78

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _quantify_environmental_impact(self, target_entity: str, industry: str) -> Finding:
        """Quantify environmental impact metrics."""
        finding = Finding(
            agent_name=self.name,
            finding_type="environmental_impact",
            title="Environmental Impact Quantification"
        )

        try:
            prompt = f"""Quantify the environmental impact of {target_entity} ({industry}).

Estimate the following metrics per $1M invested (use industry benchmarks):
1. CO2 emissions avoided (tons)
2. Clean energy generated (MWh)
3. Water saved (liters)
4. Waste reduced (tons)
5. Hectares of forest/land protected

For each metric:
- Provide estimated value with range
- Confidence level (high/medium/low)
- Data sources used for estimation
- Comparison to industry average

Consider both positive contributions and negative externalities."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Environmental Impact (LLM)",
                description="Environmental impact quantification",
                data={"analysis": result},
                confidence=0.72,
            ))

            result_lower = result.lower()
            if "positive" in result_lower and "significant" in result_lower:
                finding.severity = "LOW"
                finding.description = f"Positive environmental impact from {target_entity}."
            elif "negative" in result_lower or "harm" in result_lower:
                finding.severity = "MEDIUM"
                finding.description = f"Mixed environmental impact from {target_entity}."
            else:
                finding.severity = "INFO"
                finding.description = f"Environmental impact assessed for {target_entity}."

            finding.confidence_score = 0.72

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to quantify: {str(e)}"

        return finding

    async def _quantify_social_impact(self, target_entity: str, industry: str) -> Finding:
        """Quantify social impact metrics."""
        finding = Finding(
            agent_name=self.name,
            finding_type="social_impact",
            title="Social Impact Quantification"
        )

        try:
            prompt = f"""Quantify the social impact of {target_entity} ({industry}).

Estimate the following metrics per $1M invested:
1. Lives improved/benefited
2. Jobs created (direct and indirect)
3. People with improved healthcare access
4. Students educated or trained
5. People with improved financial inclusion

For each metric:
- Provide estimated value with range
- Confidence level
- Methodology used
- Comparison to industry benchmarks

Consider SDGs 1-5, 8, 10, and 16."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Social Impact (LLM)",
                description="Social impact quantification",
                data={"analysis": result},
                confidence=0.72,
            ))

            result_lower = result.lower()
            if "significant" in result_lower or "positive" in result_lower:
                finding.severity = "LOW"
                finding.description = f"Positive social impact from {target_entity}."
            else:
                finding.severity = "INFO"
                finding.description = f"Social impact assessed for {target_entity}."

            finding.confidence_score = 0.72

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to quantify: {str(e)}"

        return finding

    async def _analyze_impact_pathways(self, target_entity: str, industry: str) -> Finding:
        """Analyze impact pathways (theory of change)."""
        finding = Finding(
            agent_name=self.name,
            finding_type="impact_pathway",
            title="Impact Pathways Analysis"
        )

        try:
            prompt = f"""Analyze the impact pathways (theory of change) for {target_entity} ({industry}).

For each major business activity:
1. Input: What resources/investments are deployed?
2. Output: What direct products/services result?
3. Outcome: What intermediate changes occur?
4. Impact: What long-term societal/environmental changes result?

Identify:
- Clear causal chains from investment to impact
- Key assumptions in the theory of change
- Risks to impact realization
- Unintended consequences (positive and negative)

Map to specific SDG targets where applicable."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.4
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Impact Pathways (LLM)",
                description="Theory of change analysis",
                data={"analysis": result},
                confidence=0.70,
            ))

            finding.severity = "INFO"
            finding.description = f"Impact pathways mapped for {target_entity}."
            finding.confidence_score = 0.70

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _detect_impact_washing(self, target_entity: str, industry: str) -> Finding:
        """Detect potential impact washing."""
        finding = Finding(
            agent_name=self.name,
            finding_type="impact_washing",
            title="Impact Washing Detection"
        )

        try:
            prompt = f"""Analyze {target_entity} ({industry}) for potential "impact washing" - exaggerated or misleading claims about positive social/environmental impact.

Check for:
1. Vague or unverifiable impact claims
2. Cherry-picked metrics that hide negative impacts
3. Misleading comparisons or baselines
4. Lack of third-party verification
5. Impact claims disconnected from core business
6. Hidden trade-offs (e.g., claiming carbon neutrality while increasing emissions)

Rate impact washing risk: CRITICAL, HIGH, MEDIUM, or LOW.
Provide specific examples of concerning claims if found."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Impact Washing Detection (LLM)",
                description="Impact authenticity assessment",
                data={"analysis": result},
                confidence=0.75,
            ))

            result_lower = result.lower()
            if "critical" in result_lower or "high risk" in result_lower:
                finding.severity = "HIGH"
                finding.description = f"High impact washing risk for {target_entity}."
            elif "medium" in result_lower or "some concerns" in result_lower:
                finding.severity = "MEDIUM"
                finding.description = f"Moderate impact washing concerns for {target_entity}."
            else:
                finding.severity = "LOW"
                finding.description = f"Low impact washing risk for {target_entity}."

            finding.confidence_score = 0.75

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to assess: {str(e)}"

        return finding

    def generate_impact_report(self, report: AgentReport) -> Dict[str, Any]:
        """Generate comprehensive impact report."""
        if not report.findings:
            return {
                "entity": report.target_entity,
                "overall_impact_score": 50.0,
                "confidence_level": "low",
            }

        # Calculate impact score from findings
        severity_scores = {"LOW": 80, "INFO": 60, "MEDIUM": 40, "HIGH": 20, "CRITICAL": 0}
        total_score = sum(severity_scores.get(f.severity, 50) for f in report.findings)
        avg_score = total_score / len(report.findings)

        avg_confidence = sum(f.confidence_score for f in report.findings) / len(report.findings)

        if avg_confidence >= 0.8:
            confidence_level = "very_high"
        elif avg_confidence >= 0.6:
            confidence_level = "high"
        elif avg_confidence >= 0.4:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        return {
            "entity": report.target_entity,
            "analysis_date": report.timestamp.isoformat(),
            "overall_impact_score": avg_score,
            "key_findings": [f.title for f in report.findings],
            "confidence_level": confidence_level,
        }
