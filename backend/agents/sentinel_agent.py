"""
Sentinel Agent - Environmental Monitoring
Analyzes environmental data, pollution, deforestation, and climate risks
using LLM-powered analysis and web grounding.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from .base_agent import (
    BaseAgent,
    AgentReport,
    Finding,
    Evidence,
    EvidenceType,
)
from .prompts import get_system_prompt, format_template
from utils.llm_client import GeminiClient, get_gemini_client
from models.llm_outputs import (
    EnvironmentalAnalysisResult,
    EnvironmentalFinding,
    DeforestationFinding,
    PollutionFinding,
    LLMFinding,
)


@dataclass
class EnvironmentalData:
    """Environmental data point."""
    metric_name: str
    value: float
    unit: str
    source: str
    timestamp: datetime
    location: Optional[str] = None
    confidence: float = 0.8


class SentinelAgent(BaseAgent):
    """
    Sentinel Agent - Environmental Monitoring

    Uses Gemini LLM for environmental analysis based on available data
    and knowledge about the company's environmental practices.

    Capabilities:
    - Environmental impact analysis using LLM
    - Deforestation and land use assessment
    - Pollution and emissions evaluation
    - Climate risk assessment
    - Biodiversity impact analysis
    - Facility and operations environmental footprint
    """

    def __init__(
        self,
        name: str = "Sentinel",
        timeout_seconds: int = 120,
        max_retries: int = 3,
        enable_debug: bool = False,
        llm_client: GeminiClient = None,
    ):
        super().__init__(
            name=name,
            agent_type="environmental_monitoring",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            enable_debug=enable_debug,
        )

        self.llm_client = llm_client or get_gemini_client()
        self.system_prompt = get_system_prompt("sentinel")

        # Environmental thresholds for severity assessment
        self.severity_thresholds = {
            "carbon_intensity_high": 500,  # kg CO2 per $1000 revenue
            "water_intensity_high": 100,  # m3 per $1000 revenue
            "waste_intensity_high": 50,  # kg per $1000 revenue
        }

    async def analyze(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentReport:
        """
        Perform comprehensive environmental analysis using LLM.

        Args:
            target_entity: Company or facility name
            context: Optional context including industry, location, etc.

        Returns:
            AgentReport with environmental findings
        """
        report = AgentReport(
            agent_name=self.name,
            agent_type=self.agent_type,
            target_entity=target_entity,
        )

        try:
            industry = context.get("industry", "Unknown") if context else "Unknown"
            location = context.get("location", "Global operations") if context else "Global operations"

            self.logger.info(
                "sentinel_analysis_start",
                target=target_entity,
                industry=industry,
            )

            # Parallel environmental analysis tasks
            analysis_tasks = [
                self._analyze_carbon_footprint(target_entity, industry, context),
                self._analyze_pollution(target_entity, industry, context),
                self._analyze_deforestation(target_entity, industry, context),
                self._analyze_water_management(target_entity, industry, context),
                self._analyze_biodiversity(target_entity, industry, context),
                self._analyze_climate_risk(target_entity, industry, context),
            ]

            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    self.logger.warning(
                        "environmental_task_failed",
                        error=str(result),
                    )
                    report.errors.append(f"Task failed: {str(result)}")
                elif isinstance(result, Finding):
                    report.add_finding(result)

            # Add metadata
            report.metadata = {
                "industry": industry,
                "location": location,
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "analysis_method": "LLM-based environmental assessment",
            }

        except Exception as e:
            self.logger.error(
                "sentinel_analysis_error",
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
        Collect environmental data using LLM analysis.

        Args:
            target_entity: Entity to collect data for
            context: Additional context

        Returns:
            List of Evidence objects
        """
        evidence_list = []

        try:
            # Use LLM to gather environmental information
            data_prompt = f"""Research and compile available environmental data for {target_entity}.

Look for:
1. Carbon emissions and climate commitments
2. Environmental certifications (ISO 14001, etc.)
3. Sustainability reports and disclosures
4. Environmental violations or fines
5. Renewable energy usage
6. Water and waste management practices

Provide specific data points with sources where known."""

            result = await self.llm_client.analyze_with_search(
                query=f"{target_entity} environmental sustainability emissions carbon footprint",
                context=data_prompt,
            )

            evidence = Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Environmental Research (LLM)",
                description=f"Environmental data compilation for {target_entity}",
                data={
                    "analysis": result.get("analysis", ""),
                    "query": result.get("query", ""),
                },
                timestamp=datetime.utcnow(),
                confidence=0.75,
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
        """Calculate confidence based on evidence quality."""
        if not evidence:
            return 0.0

        avg_confidence = sum(e.confidence for e in evidence) / len(evidence)

        # Bonus for multiple evidence sources
        unique_sources = len(set(e.source for e in evidence))
        source_bonus = min(0.2, unique_sources * 0.05)

        return min(1.0, avg_confidence + source_bonus)

    async def _analyze_carbon_footprint(
        self,
        target_entity: str,
        industry: str,
        context: Optional[Dict[str, Any]],
    ) -> Finding:
        """Analyze carbon footprint and emissions using LLM."""
        finding = Finding(
            agent_name=self.name,
            finding_type="carbon_emissions",
            title="Carbon Footprint Analysis",
        )

        try:
            carbon_prompt = f"""Analyze the carbon footprint and emissions profile of {target_entity}.

Industry: {industry}

Assess:
1. **Scope 1 Emissions** (direct emissions from owned sources)
2. **Scope 2 Emissions** (indirect from purchased energy)
3. **Scope 3 Emissions** (value chain emissions)
4. **Carbon reduction commitments** (net-zero targets, SBTi)
5. **Renewable energy adoption**
6. **Carbon intensity** compared to industry peers

Provide specific numbers if known, otherwise give qualitative assessment.
Rate severity: CRITICAL (major polluter), HIGH (above average), MEDIUM (average), LOW (below average), INFO (leader).
Include confidence score (0.0-1.0) based on data availability."""

            result = await self.llm_client.generate_text(
                prompt=carbon_prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
            )

            evidence = Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Carbon Footprint Analysis (LLM)",
                description="Comprehensive carbon emissions assessment",
                data={
                    "analysis": result,
                    "industry": industry,
                },
                confidence=0.75,
            )
            finding.add_evidence(evidence)

            # Parse severity from response (simplified - could use structured output)
            result_lower = result.lower()
            if "critical" in result_lower or "major polluter" in result_lower:
                finding.severity = "CRITICAL"
                finding.description = f"Critical carbon emissions concerns for {target_entity}. Significant climate risk."
            elif "high" in result_lower[:500] or "above average" in result_lower:
                finding.severity = "HIGH"
                finding.description = f"Above-average carbon footprint for {target_entity}. Improvement needed."
            elif "low" in result_lower[:500] or "below average" in result_lower or "leader" in result_lower:
                finding.severity = "LOW"
                finding.description = f"Below-average carbon footprint for {target_entity}. Good environmental performance."
            else:
                finding.severity = "MEDIUM"
                finding.description = f"Average carbon footprint for {target_entity} in {industry} industry."

            finding.confidence_score = 0.75

        except Exception as e:
            self.logger.error("carbon_analysis_error", error=str(e))
            finding.severity = "INFO"
            finding.description = f"Unable to analyze carbon footprint: {str(e)}"
            finding.confidence_score = 0.3

        return finding

    async def _analyze_pollution(
        self,
        target_entity: str,
        industry: str,
        context: Optional[Dict[str, Any]],
    ) -> Finding:
        """Analyze pollution and environmental contamination."""
        finding = Finding(
            agent_name=self.name,
            finding_type="pollution",
            title="Pollution and Contamination Assessment",
        )

        try:
            pollution_prompt = f"""Analyze pollution and environmental contamination risks for {target_entity}.

Industry: {industry}

Assess:
1. **Air Pollution** - emissions, particulates, toxic releases (TRI data if available)
2. **Water Pollution** - discharge, contamination incidents, water quality impacts
3. **Soil Contamination** - hazardous waste, remediation sites
4. **Regulatory Violations** - EPA fines, environmental penalties
5. **Community Impact** - proximity to vulnerable communities

Look for any reported environmental incidents, Superfund sites, or consent decrees.
Rate severity based on actual violations and potential harm."""

            result = await self.llm_client.generate_text(
                prompt=pollution_prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
            )

            evidence = Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Pollution Analysis (LLM)",
                description="Environmental pollution assessment",
                data={"analysis": result},
                confidence=0.72,
            )
            finding.add_evidence(evidence)

            # Assess severity
            result_lower = result.lower()
            violation_indicators = ["violation", "fine", "penalty", "contamination", "spill", "superfund"]
            violation_count = sum(1 for indicator in violation_indicators if indicator in result_lower)

            if violation_count >= 3 or "critical" in result_lower:
                finding.severity = "CRITICAL"
                finding.description = f"Significant pollution concerns for {target_entity}. Multiple violations or contamination issues identified."
            elif violation_count >= 2:
                finding.severity = "HIGH"
                finding.description = f"Elevated pollution risks for {target_entity}. Environmental incidents or violations noted."
            elif violation_count >= 1:
                finding.severity = "MEDIUM"
                finding.description = f"Some pollution concerns for {target_entity}. Minor issues identified."
            else:
                finding.severity = "LOW"
                finding.description = f"Low pollution risk for {target_entity}. No significant violations found."

            finding.confidence_score = 0.72

        except Exception as e:
            self.logger.error("pollution_analysis_error", error=str(e))
            finding.severity = "INFO"
            finding.description = f"Unable to analyze pollution: {str(e)}"

        return finding

    async def _analyze_deforestation(
        self,
        target_entity: str,
        industry: str,
        context: Optional[Dict[str, Any]],
    ) -> Finding:
        """Analyze deforestation and land use impacts."""
        finding = Finding(
            agent_name=self.name,
            finding_type="deforestation",
            title="Deforestation and Land Use Analysis",
        )

        try:
            # Industries with high deforestation risk
            high_risk_industries = [
                "agriculture", "palm oil", "soy", "cattle", "timber",
                "paper", "pulp", "rubber", "cocoa", "coffee", "mining"
            ]

            is_high_risk = any(ind in industry.lower() for ind in high_risk_industries)

            deforestation_prompt = f"""Analyze deforestation and land use impacts for {target_entity}.

Industry: {industry}
High-risk industry for deforestation: {is_high_risk}

Assess:
1. **Direct Land Use** - facility footprint, land conversion
2. **Supply Chain Deforestation** - commodity sourcing from high-risk regions
3. **Zero-Deforestation Commitments** - policies, deadlines, progress
4. **Certifications** - FSC, RSPO, Rainforest Alliance, etc.
5. **Monitoring Systems** - satellite monitoring, traceability
6. **High-Risk Sourcing Regions** - Amazon, Indonesia, Congo Basin exposure

Look for any deforestation allegations or controversies."""

            result = await self.llm_client.generate_text(
                prompt=deforestation_prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
            )

            evidence = Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Deforestation Analysis (LLM)",
                description="Land use and deforestation assessment",
                data={
                    "analysis": result,
                    "high_risk_industry": is_high_risk,
                },
                confidence=0.70,
            )
            finding.add_evidence(evidence)

            # Assess severity
            result_lower = result.lower()
            if "deforestation" in result_lower and ("linked" in result_lower or "associated" in result_lower or "caused" in result_lower):
                finding.severity = "CRITICAL"
                finding.description = f"Direct deforestation linkage identified for {target_entity}. Major environmental concern."
            elif is_high_risk and "no commitment" in result_lower:
                finding.severity = "HIGH"
                finding.description = f"High deforestation risk for {target_entity} in {industry} industry. No clear zero-deforestation commitment."
            elif is_high_risk:
                finding.severity = "MEDIUM"
                finding.description = f"Moderate deforestation risk for {target_entity}. Industry exposure requires monitoring."
            else:
                finding.severity = "LOW"
                finding.description = f"Low deforestation risk for {target_entity}. Not in high-risk industry."

            finding.confidence_score = 0.70

        except Exception as e:
            self.logger.error("deforestation_analysis_error", error=str(e))
            finding.severity = "INFO"
            finding.description = f"Unable to analyze deforestation: {str(e)}"

        return finding

    async def _analyze_water_management(
        self,
        target_entity: str,
        industry: str,
        context: Optional[Dict[str, Any]],
    ) -> Finding:
        """Analyze water usage and management."""
        finding = Finding(
            agent_name=self.name,
            finding_type="water_management",
            title="Water Management Assessment",
        )

        try:
            water_prompt = f"""Analyze water management practices for {target_entity}.

Industry: {industry}

Assess:
1. **Water Consumption** - total usage, intensity metrics
2. **Water Stress Exposure** - operations in water-scarce regions
3. **Water Recycling** - reuse rates, efficiency improvements
4. **Discharge Quality** - treatment, compliance with permits
5. **Water Stewardship** - community water programs, watershed protection
6. **CDP Water Security** - disclosure and ratings if available

Industries like beverage, agriculture, mining, and semiconductors are water-intensive."""

            result = await self.llm_client.generate_text(
                prompt=water_prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
            )

            evidence = Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Water Management Analysis (LLM)",
                description="Water usage and stewardship assessment",
                data={"analysis": result},
                confidence=0.72,
            )
            finding.add_evidence(evidence)

            # Water-intensive industries
            water_intensive = ["beverage", "agriculture", "mining", "semiconductor", "textile", "food"]
            is_water_intensive = any(ind in industry.lower() for ind in water_intensive)

            result_lower = result.lower()
            if "water stress" in result_lower and "high" in result_lower:
                finding.severity = "HIGH"
                finding.description = f"High water stress exposure for {target_entity}. Water scarcity risk."
            elif is_water_intensive and "poor" in result_lower:
                finding.severity = "HIGH"
                finding.description = f"Poor water management in water-intensive {industry} industry for {target_entity}."
            elif is_water_intensive:
                finding.severity = "MEDIUM"
                finding.description = f"Water management monitoring needed for {target_entity} in water-intensive industry."
            else:
                finding.severity = "LOW"
                finding.description = f"Adequate water management for {target_entity}."

            finding.confidence_score = 0.72

        except Exception as e:
            self.logger.error("water_analysis_error", error=str(e))
            finding.severity = "INFO"
            finding.description = f"Unable to analyze water management: {str(e)}"

        return finding

    async def _analyze_biodiversity(
        self,
        target_entity: str,
        industry: str,
        context: Optional[Dict[str, Any]],
    ) -> Finding:
        """Analyze biodiversity impact."""
        finding = Finding(
            agent_name=self.name,
            finding_type="biodiversity",
            title="Biodiversity Impact Assessment",
        )

        try:
            biodiversity_prompt = f"""Analyze biodiversity impact for {target_entity}.

Industry: {industry}

Assess:
1. **Habitat Impact** - operations near protected areas, critical habitats
2. **Species Impact** - effects on endangered or threatened species
3. **Biodiversity Policy** - commitments, no-go zones, offset programs
4. **TNFD Alignment** - Taskforce on Nature-related Financial Disclosures
5. **Supply Chain Biodiversity** - sourcing from biodiversity hotspots
6. **Restoration Programs** - habitat restoration, rewilding efforts

High-risk industries: mining, agriculture, infrastructure, real estate."""

            result = await self.llm_client.generate_text(
                prompt=biodiversity_prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
            )

            evidence = Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Biodiversity Analysis (LLM)",
                description="Biodiversity impact assessment",
                data={"analysis": result},
                confidence=0.68,
            )
            finding.add_evidence(evidence)

            result_lower = result.lower()
            if "endangered" in result_lower and ("harm" in result_lower or "threat" in result_lower):
                finding.severity = "CRITICAL"
                finding.description = f"Critical biodiversity impact for {target_entity}. Endangered species at risk."
            elif "protected area" in result_lower or "critical habitat" in result_lower:
                finding.severity = "HIGH"
                finding.description = f"Operations near protected areas or critical habitats for {target_entity}."
            elif any(ind in industry.lower() for ind in ["mining", "agriculture", "infrastructure"]):
                finding.severity = "MEDIUM"
                finding.description = f"Industry-related biodiversity risk for {target_entity}. Monitoring recommended."
            else:
                finding.severity = "LOW"
                finding.description = f"Low biodiversity impact identified for {target_entity}."

            finding.confidence_score = 0.68

        except Exception as e:
            self.logger.error("biodiversity_analysis_error", error=str(e))
            finding.severity = "INFO"
            finding.description = f"Unable to analyze biodiversity: {str(e)}"

        return finding

    async def _analyze_climate_risk(
        self,
        target_entity: str,
        industry: str,
        context: Optional[Dict[str, Any]],
    ) -> Finding:
        """Analyze climate-related risks and opportunities."""
        finding = Finding(
            agent_name=self.name,
            finding_type="climate_risk",
            title="Climate Risk Assessment",
        )

        try:
            climate_prompt = f"""Analyze climate-related risks and opportunities for {target_entity}.

Industry: {industry}

Assess using TCFD framework:
1. **Physical Risks**
   - Acute: extreme weather exposure (hurricanes, floods, wildfires)
   - Chronic: sea level rise, temperature changes, water scarcity

2. **Transition Risks**
   - Policy: carbon pricing, regulations
   - Technology: disruption from clean tech
   - Market: shifting consumer preferences
   - Reputation: stakeholder concerns

3. **Climate Opportunities**
   - Clean technology investments
   - New market opportunities
   - Resource efficiency gains

4. **Climate Governance**
   - Board oversight
   - Climate targets and progress
   - TCFD disclosure quality

Rate overall climate risk exposure."""

            result = await self.llm_client.generate_text(
                prompt=climate_prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
            )

            evidence = Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Climate Risk Analysis (LLM)",
                description="TCFD-aligned climate risk assessment",
                data={"analysis": result},
                confidence=0.75,
            )
            finding.add_evidence(evidence)

            # High transition risk industries
            high_transition_risk = ["oil", "gas", "coal", "automotive", "aviation", "shipping", "steel", "cement"]
            is_high_transition = any(ind in industry.lower() for ind in high_transition_risk)

            result_lower = result.lower()
            if is_high_transition and "no plan" in result_lower:
                finding.severity = "CRITICAL"
                finding.description = f"Critical climate transition risk for {target_entity}. High-carbon industry without clear transition plan."
            elif is_high_transition:
                finding.severity = "HIGH"
                finding.description = f"High climate transition risk for {target_entity} in {industry} industry."
            elif "physical risk" in result_lower and "high" in result_lower:
                finding.severity = "HIGH"
                finding.description = f"Significant physical climate risk exposure for {target_entity}."
            elif "opportunity" in result_lower and "leader" in result_lower:
                finding.severity = "LOW"
                finding.description = f"Well-positioned for climate transition. {target_entity} shows climate leadership."
            else:
                finding.severity = "MEDIUM"
                finding.description = f"Moderate climate risk for {target_entity}. Transition planning recommended."

            finding.confidence_score = 0.75

        except Exception as e:
            self.logger.error("climate_analysis_error", error=str(e))
            finding.severity = "INFO"
            finding.description = f"Unable to analyze climate risk: {str(e)}"

        return finding
