"""
Veritas Agent - Supply Chain Verification
Analyzes supply chain transparency, certifications, and ethical sourcing
using LLM-powered analysis and SEC filings data.
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
from utils.data_sources import SECEdgarClient, get_sec_client


@dataclass
class SupplierRisk:
    """Supplier risk assessment."""
    name: str
    country: str
    risk_level: str
    risk_factors: List[str]
    tier: int = 1


class VeritasAgent(BaseAgent):
    """
    Veritas Agent - Supply Chain Verification

    Uses Gemini LLM and SEC filings to analyze supply chain
    transparency and ethical sourcing practices.

    Capabilities:
    - Supply chain transparency assessment
    - Certification verification analysis
    - Conflict minerals and ethical sourcing
    - Forced labor and human rights risk detection
    - Supplier tier visibility analysis
    """

    def __init__(
        self,
        name: str = "Veritas",
        timeout_seconds: int = 120,
        max_retries: int = 3,
        enable_debug: bool = False,
        llm_client: GeminiClient = None,
        sec_client: SECEdgarClient = None,
    ):
        super().__init__(
            name=name,
            agent_type="supply_chain_verification",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            enable_debug=enable_debug,
        )

        self.llm_client = llm_client or get_gemini_client()
        self.sec_client = sec_client or get_sec_client()
        self.system_prompt = get_system_prompt("veritas")

        # High-risk countries for supply chain issues
        self.high_risk_countries = [
            "China", "Myanmar", "Bangladesh", "Vietnam", "India",
            "Indonesia", "Thailand", "Malaysia", "Philippines",
            "DRC", "Congo", "Ethiopia", "Eritrea"
        ]

    async def analyze(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentReport:
        """Perform comprehensive supply chain analysis."""
        report = AgentReport(
            agent_name=self.name,
            agent_type=self.agent_type,
            target_entity=target_entity,
        )

        try:
            ticker = context.get("ticker", target_entity) if context else target_entity
            industry = context.get("industry", "Unknown") if context else "Unknown"

            self.logger.info("veritas_analysis_start", target=target_entity)

            # Try to get SEC filings
            filings_data = await self._fetch_sec_data(ticker)

            # Parallel analysis
            analysis_tasks = [
                self._analyze_supply_chain_transparency(target_entity, industry, filings_data),
                self._analyze_certifications(target_entity, industry),
                self._analyze_conflict_minerals(target_entity, industry),
                self._analyze_human_rights_risk(target_entity, industry),
                self._analyze_supplier_geography(target_entity, industry),
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
            self.logger.error("veritas_analysis_error", error=str(e))
            report.errors.append(f"Analysis error: {str(e)}")

        return report

    async def collect_data(self, target_entity: str, context: Optional[Dict[str, Any]] = None) -> List[Evidence]:
        """Collect supply chain data."""
        evidence_list = []
        try:
            ticker = context.get("ticker", target_entity) if context else target_entity
            filings = await self.sec_client.get_recent_filings(ticker=ticker, filing_types=["10-K"], limit=2)
            for filing in filings:
                evidence = Evidence(
                    type=EvidenceType.DOCUMENT,
                    source=f"SEC EDGAR - {filing.filing_type}",
                    description=f"{filing.filing_type} filing",
                    data={"url": filing.document_url},
                    timestamp=filing.filing_date,
                    confidence=0.90,
                )
                evidence_list.append(evidence)
        except Exception as e:
            self.logger.error("data_collection_error", error=str(e))
        return evidence_list

    def calculate_confidence(self, evidence: List[Evidence], context: Optional[Dict[str, Any]] = None) -> float:
        if not evidence:
            return 0.0
        return min(1.0, sum(e.confidence for e in evidence) / len(evidence) + 0.1)

    async def _fetch_sec_data(self, ticker: str) -> Optional[str]:
        """Fetch SEC filing data."""
        try:
            filings = await self.sec_client.get_recent_filings(ticker=ticker, filing_types=["10-K"], limit=1)
            if filings:
                return await self.sec_client.get_filing_content(filings[0], max_chars=20000)
        except Exception:
            pass
        return None

    async def _analyze_supply_chain_transparency(self, target_entity: str, industry: str, filings_data: Optional[str]) -> Finding:
        """Analyze supply chain transparency."""
        finding = Finding(agent_name=self.name, finding_type="supply_chain_transparency", title="Supply Chain Transparency")

        try:
            prompt = f"""Analyze supply chain transparency for {target_entity} in {industry} industry.

Assess: supplier disclosure levels, audit programs, traceability systems, and disclosure quality.
Rate: CRITICAL (opaque), HIGH (minimal), MEDIUM (partial), LOW (good transparency)."""

            result = await self.llm_client.generate_text(prompt=prompt, system_prompt=self.system_prompt, temperature=0.3)

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Transparency Analysis (LLM)",
                description="Supply chain transparency assessment",
                data={"analysis": result},
                confidence=0.75,
            ))

            result_lower = result.lower()
            if "opaque" in result_lower or "no disclosure" in result_lower:
                finding.severity = "CRITICAL"
                finding.description = f"Critical transparency issues for {target_entity}."
            elif "limited" in result_lower:
                finding.severity = "HIGH"
                finding.description = f"Limited supply chain transparency for {target_entity}."
            elif "partial" in result_lower:
                finding.severity = "MEDIUM"
                finding.description = f"Partial transparency for {target_entity}."
            else:
                finding.severity = "LOW"
                finding.description = f"Good supply chain transparency for {target_entity}."

            finding.confidence_score = 0.75

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _analyze_certifications(self, target_entity: str, industry: str) -> Finding:
        """Analyze certifications."""
        finding = Finding(agent_name=self.name, finding_type="certifications", title="Certification Analysis")

        try:
            prompt = f"""Analyze supply chain certifications for {target_entity} ({industry}).
Look for: ISO 9001, ISO 14001, SA8000, Fair Trade, FSC, RSPO, RMI membership.
Rate certification coverage."""

            result = await self.llm_client.generate_text(prompt=prompt, system_prompt=self.system_prompt, temperature=0.3)

            finding.add_evidence(Evidence(
                type=EvidenceType.CERTIFICATION,
                source="Certification Analysis (LLM)",
                description="Certification assessment",
                data={"analysis": result},
                confidence=0.72,
            ))

            cert_count = sum(1 for cert in ["iso", "sa8000", "fair trade", "fsc", "rmi"] if cert in result.lower())

            if cert_count >= 3:
                finding.severity = "LOW"
                finding.description = f"Strong certification coverage for {target_entity}."
            elif cert_count >= 1:
                finding.severity = "MEDIUM"
                finding.description = f"Moderate certification coverage for {target_entity}."
            else:
                finding.severity = "HIGH"
                finding.description = f"Limited certifications for {target_entity}."

            finding.confidence_score = 0.72

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _analyze_conflict_minerals(self, target_entity: str, industry: str) -> Finding:
        """Analyze conflict minerals."""
        finding = Finding(agent_name=self.name, finding_type="conflict_minerals", title="Conflict Minerals Analysis")

        try:
            high_exposure = any(ind in industry.lower() for ind in ["electronics", "technology", "automotive", "semiconductor"])

            prompt = f"""Analyze conflict minerals (3TG) sourcing for {target_entity} ({industry}).
High exposure: {high_exposure}. Check SEC SD filings, RMI membership, smelter due diligence."""

            result = await self.llm_client.generate_text(prompt=prompt, system_prompt=self.system_prompt, temperature=0.3)

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Conflict Minerals Analysis (LLM)",
                description="3TG assessment",
                data={"analysis": result},
                confidence=0.70,
            ))

            if not high_exposure:
                finding.severity = "LOW"
                finding.description = f"Low conflict minerals exposure for {target_entity}."
            elif "conflict-free" in result.lower() or "rmi" in result.lower():
                finding.severity = "LOW"
                finding.description = f"Good conflict minerals management for {target_entity}."
            else:
                finding.severity = "MEDIUM"
                finding.description = f"Moderate conflict minerals risk for {target_entity}."

            finding.confidence_score = 0.70

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _analyze_human_rights_risk(self, target_entity: str, industry: str) -> Finding:
        """Analyze human rights risks."""
        finding = Finding(agent_name=self.name, finding_type="human_rights", title="Human Rights Risk Assessment")

        try:
            high_risk = any(ind in industry.lower() for ind in ["apparel", "textile", "agriculture", "electronics"])

            prompt = f"""Analyze human rights and forced labor risks for {target_entity} ({industry}).
High-risk industry: {high_risk}. Check for allegations, Modern Slavery Act, Xinjiang exposure, audits."""

            result = await self.llm_client.generate_text(prompt=prompt, system_prompt=self.system_prompt, temperature=0.3)

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Human Rights Analysis (LLM)",
                description="Forced labor assessment",
                data={"analysis": result},
                confidence=0.72,
            ))

            result_lower = result.lower()
            if any(term in result_lower for term in ["forced labor", "child labor", "xinjiang"]):
                finding.severity = "CRITICAL"
                finding.description = f"Critical human rights concerns for {target_entity}."
            elif high_risk:
                finding.severity = "MEDIUM"
                finding.description = f"Elevated human rights risk for {target_entity} in {industry}."
            else:
                finding.severity = "LOW"
                finding.description = f"Low human rights risk for {target_entity}."

            finding.confidence_score = 0.72

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding

    async def _analyze_supplier_geography(self, target_entity: str, industry: str) -> Finding:
        """Analyze supplier geography."""
        finding = Finding(agent_name=self.name, finding_type="supplier_geography", title="Geographic Risk Analysis")

        try:
            prompt = f"""Analyze supplier geographic distribution for {target_entity} ({industry}).
Assess concentration risk, high-risk country exposure, geopolitical risks.
High-risk countries: {', '.join(self.high_risk_countries[:8])}"""

            result = await self.llm_client.generate_text(prompt=prompt, system_prompt=self.system_prompt, temperature=0.3)

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Geographic Analysis (LLM)",
                description="Supplier geography assessment",
                data={"analysis": result},
                confidence=0.70,
            ))

            high_risk_count = sum(1 for c in self.high_risk_countries if c.lower() in result.lower())

            if high_risk_count >= 3:
                finding.severity = "HIGH"
                finding.description = f"High geographic risk for {target_entity}."
            elif high_risk_count >= 1:
                finding.severity = "MEDIUM"
                finding.description = f"Moderate geographic risk for {target_entity}."
            else:
                finding.severity = "LOW"
                finding.description = f"Diversified supply chain for {target_entity}."

            finding.confidence_score = 0.70

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze: {str(e)}"

        return finding
