"""
Impact Agent - SDG Impact Quantification
Maps investments to UN Sustainable Development Goals (SDG) outcomes and quantifies
measurable impact metrics per dollar invested.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import asyncio
import random
import hashlib
from collections import defaultdict

from .base_agent import (
    BaseAgent,
    AgentReport,
    Finding,
    Evidence,
    EvidenceType,
    ConfidenceLevel,
)


@dataclass
class SDGMetrics:
    """Metrics for a specific SDG goal."""
    goal_number: int
    goal_name: str
    alignment_score: float  # 0.0 to 1.0
    contribution_level: str  # negative, neutral, low, medium, high
    primary_indicators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImpactMetric:
    """Quantified impact metric."""
    metric_name: str
    value: float
    unit: str
    per_million_usd: float
    confidence: float
    calculation_method: str
    data_sources: List[str] = field(default_factory=list)


@dataclass
class ImpactPathway:
    """Pathway from investment to impact."""
    investment_area: str
    sdg_goals: List[int]
    intermediate_outcomes: List[str]
    final_outcomes: List[str]
    theory_of_change: str
    assumptions: List[str] = field(default_factory=list)


class ImpactAgent(BaseAgent):
    """
    SDG Impact Quantification Agent

    Capabilities:
    - Map investments to UN SDG outcomes (all 17 goals)
    - Quantify impact per dollar invested
    - Calculate metrics:
      - Lives improved per $1M
      - CO2 avoided per $1M
      - Jobs created per $1M
      - Water saved per $1M
      - Clean energy generated per $1M
      - And many more
    - Generate comprehensive impact reports
    - Track impact over time
    - Compare impact across investments
    """

    def __init__(
        self,
        name: str = "ImpactQuantifier",
        timeout_seconds: int = 90,
        max_retries: int = 3,
        enable_debug: bool = False,
    ):
        super().__init__(
            name=name,
            agent_type="sdg_impact_quantification",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            enable_debug=enable_debug,
        )

        # SDG goals mapping
        self.sdg_goals = self._initialize_sdg_goals()

        # Impact calculation models (simulated coefficients)
        self.impact_models = self._initialize_impact_models()

        # Sectoral impact multipliers
        self.sector_multipliers = {
            "renewable_energy": 1.8,
            "clean_water": 2.1,
            "education": 1.5,
            "healthcare": 1.7,
            "sustainable_agriculture": 1.6,
            "affordable_housing": 1.4,
            "clean_transportation": 1.5,
            "waste_management": 1.3,
            "financial_inclusion": 1.6,
            "technology_access": 1.7,
        }

    def _initialize_sdg_goals(self) -> Dict[int, Dict[str, Any]]:
        """Initialize SDG goals mapping."""
        return {
            1: {
                "name": "No Poverty",
                "indicators": ["poverty_rate", "income_below_poverty_line", "social_protection_coverage"],
                "primary_metrics": ["lives_improved", "income_increase"],
            },
            2: {
                "name": "Zero Hunger",
                "indicators": ["prevalence_of_undernourishment", "food_security", "agricultural_productivity"],
                "primary_metrics": ["people_fed", "nutrition_improved"],
            },
            3: {
                "name": "Good Health and Well-being",
                "indicators": ["mortality_rate", "disease_incidence", "healthcare_access"],
                "primary_metrics": ["lives_saved", "healthcare_access_improved"],
            },
            4: {
                "name": "Quality Education",
                "indicators": ["literacy_rate", "school_enrollment", "education_quality"],
                "primary_metrics": ["students_educated", "literacy_rate_increase"],
            },
            5: {
                "name": "Gender Equality",
                "indicators": ["gender_wage_gap", "women_in_leadership", "gender_based_violence"],
                "primary_metrics": ["women_empowered", "wage_gap_reduction"],
            },
            6: {
                "name": "Clean Water and Sanitation",
                "indicators": ["water_access", "sanitation_access", "water_quality"],
                "primary_metrics": ["liters_clean_water", "people_with_sanitation"],
            },
            7: {
                "name": "Affordable and Clean Energy",
                "indicators": ["renewable_energy_share", "energy_access", "energy_efficiency"],
                "primary_metrics": ["mwh_clean_energy", "co2_avoided"],
            },
            8: {
                "name": "Decent Work and Economic Growth",
                "indicators": ["unemployment_rate", "gdp_growth", "labor_rights"],
                "primary_metrics": ["jobs_created", "gdp_contribution"],
            },
            9: {
                "name": "Industry, Innovation and Infrastructure",
                "indicators": ["infrastructure_investment", "innovation_index", "industrialization"],
                "primary_metrics": ["infrastructure_built", "innovation_projects"],
            },
            10: {
                "name": "Reduced Inequalities",
                "indicators": ["income_inequality", "social_inclusion", "discrimination"],
                "primary_metrics": ["inequality_reduction", "inclusive_policies"],
            },
            11: {
                "name": "Sustainable Cities and Communities",
                "indicators": ["urban_planning", "air_quality", "public_transport_access"],
                "primary_metrics": ["sustainable_housing_units", "air_quality_improvement"],
            },
            12: {
                "name": "Responsible Consumption and Production",
                "indicators": ["waste_generation", "recycling_rate", "sustainable_production"],
                "primary_metrics": ["waste_reduced_tons", "circular_economy_score"],
            },
            13: {
                "name": "Climate Action",
                "indicators": ["ghg_emissions", "climate_adaptation", "climate_finance"],
                "primary_metrics": ["co2_avoided_tons", "climate_resilience"],
            },
            14: {
                "name": "Life Below Water",
                "indicators": ["ocean_health", "marine_protected_areas", "sustainable_fishing"],
                "primary_metrics": ["marine_area_protected_km2", "fish_stocks_recovered"],
            },
            15: {
                "name": "Life on Land",
                "indicators": ["forest_coverage", "biodiversity", "land_degradation"],
                "primary_metrics": ["hectares_restored", "species_protected"],
            },
            16: {
                "name": "Peace, Justice and Strong Institutions",
                "indicators": ["violence_rate", "corruption_index", "rule_of_law"],
                "primary_metrics": ["institutions_strengthened", "corruption_reduction"],
            },
            17: {
                "name": "Partnerships for the Goals",
                "indicators": ["development_assistance", "international_cooperation", "technology_transfer"],
                "primary_metrics": ["partnerships_formed", "capacity_building"],
            },
        }

    def _initialize_impact_models(self) -> Dict[str, Dict[str, float]]:
        """Initialize impact calculation models (coefficients per $1M)."""
        return {
            "lives_improved": {
                "base_coefficient": 250.0,
                "variance": 0.3,
                "sector_dependent": True,
            },
            "co2_avoided_tons": {
                "base_coefficient": 1800.0,
                "variance": 0.4,
                "sector_dependent": True,
            },
            "jobs_created": {
                "base_coefficient": 42.0,
                "variance": 0.25,
                "sector_dependent": True,
            },
            "clean_water_liters": {
                "base_coefficient": 5_000_000.0,
                "variance": 0.35,
                "sector_dependent": True,
            },
            "clean_energy_mwh": {
                "base_coefficient": 2200.0,
                "variance": 0.3,
                "sector_dependent": True,
            },
            "students_educated": {
                "base_coefficient": 180.0,
                "variance": 0.2,
                "sector_dependent": True,
            },
            "healthcare_access_people": {
                "base_coefficient": 320.0,
                "variance": 0.28,
                "sector_dependent": True,
            },
            "waste_reduced_tons": {
                "base_coefficient": 850.0,
                "variance": 0.32,
                "sector_dependent": True,
            },
            "forest_hectares_restored": {
                "base_coefficient": 65.0,
                "variance": 0.4,
                "sector_dependent": True,
            },
            "housing_units_created": {
                "base_coefficient": 12.0,
                "variance": 0.25,
                "sector_dependent": True,
            },
        }

    async def analyze(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentReport:
        """
        Perform SDG impact quantification analysis.

        Args:
            target_entity: Company, project, or investment to analyze
            context: Additional context (investment amount, sector, etc.)

        Returns:
            AgentReport with impact findings
        """
        self.logger.info(
            "starting_impact_analysis",
            agent=self.name,
            target=target_entity,
        )

        report = AgentReport(
            agent_name=self.name,
            agent_type=self.agent_type,
            target_entity=target_entity,
        )

        try:
            # Collect impact data
            evidence = await self.collect_data(target_entity, context)

            # Map to SDG goals
            sdg_mapping = await self._map_to_sdg_goals(
                target_entity, evidence, context
            )

            # Quantify impact metrics
            impact_metrics = await self._quantify_impact_metrics(
                target_entity, evidence, context, sdg_mapping
            )

            # Generate impact pathways
            impact_pathways = await self._generate_impact_pathways(
                target_entity, evidence, context, sdg_mapping
            )

            # Create findings
            findings = self._create_impact_findings(
                target_entity,
                sdg_mapping,
                impact_metrics,
                impact_pathways,
                evidence,
            )

            for finding in findings:
                report.add_finding(finding)

            # Add impact metadata
            report.metadata["sdg_alignment"] = sdg_mapping
            report.metadata["impact_metrics"] = [
                {
                    "name": m.metric_name,
                    "value": m.value,
                    "unit": m.unit,
                    "per_million_usd": m.per_million_usd,
                }
                for m in impact_metrics
            ]
            report.metadata["impact_pathways"] = [
                {
                    "investment_area": p.investment_area,
                    "sdg_goals": p.sdg_goals,
                    "theory_of_change": p.theory_of_change,
                }
                for p in impact_pathways
            ]

            self.logger.info(
                "impact_analysis_complete",
                agent=self.name,
                target=target_entity,
                sdg_goals_aligned=len(sdg_mapping),
                impact_metrics_count=len(impact_metrics),
            )

        except Exception as e:
            self.logger.error(
                "impact_analysis_error",
                agent=self.name,
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
        """Collect impact-related data."""
        evidence_list = []

        await asyncio.sleep(0.1)  # Simulate data collection

        # Company sustainability reports
        evidence_list.append(Evidence(
            type=EvidenceType.DOCUMENT,
            source="Corporate Sustainability Report",
            description=f"Sustainability and impact data for {target_entity}",
            data={
                "sdg_goals_reported": random.randint(5, 12),
                "impact_metrics_disclosed": random.randint(8, 25),
                "third_party_verified": random.choice([True, False]),
            },
            confidence=0.85,
        ))

        # External impact assessments
        evidence_list.append(Evidence(
            type=EvidenceType.CERTIFICATION,
            source="Third-Party Impact Assessment",
            description="Independent impact verification",
            data={
                "assessment_score": random.uniform(65, 95),
                "methodology": "IRIS+ Metrics",
                "assessment_date": datetime.utcnow().isoformat(),
            },
            confidence=0.92,
        ))

        # Operational data
        evidence_list.append(Evidence(
            type=EvidenceType.API_RESPONSE,
            source="Operational Impact Database",
            description="Real-time operational impact metrics",
            data={
                "beneficiaries_reached": random.randint(10000, 500000),
                "geographic_coverage": random.randint(5, 50),
                "program_duration_years": random.uniform(1, 10),
            },
            confidence=0.88,
        ))

        # Sector benchmarks
        evidence_list.append(Evidence(
            type=EvidenceType.API_RESPONSE,
            source="Impact Benchmarking Database",
            description="Sector-specific impact benchmarks",
            data={
                "sector": context.get("sector", "mixed") if context else "mixed",
                "peer_comparison": random.choice(["above_average", "average", "below_average"]),
                "benchmark_year": 2024,
            },
            confidence=0.81,
        ))

        return evidence_list

    def calculate_confidence(
        self,
        evidence: List[Evidence],
        context: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Calculate confidence score for impact assessment."""
        if not evidence:
            return 0.0

        # Prioritize third-party verified evidence
        total_confidence = 0.0
        total_weight = 0.0

        for e in evidence:
            weight = 1.0
            if e.type == EvidenceType.CERTIFICATION:
                weight = 1.2
            elif e.data.get("third_party_verified"):
                weight = 1.1

            total_confidence += e.confidence * weight
            total_weight += weight

        return min(1.0, total_confidence / total_weight if total_weight > 0 else 0.0)

    async def _map_to_sdg_goals(
        self,
        target_entity: str,
        evidence: List[Evidence],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[SDGMetrics]:
        """Map entity activities to SDG goals."""
        sdg_metrics = []

        # Use entity hash for deterministic results
        seed = int(hashlib.md5(target_entity.encode()).hexdigest()[:8], 16)
        random.seed(seed)

        # Determine number of aligned SDGs (typically 3-8)
        num_sdgs = random.randint(3, 8)
        aligned_sdgs = random.sample(range(1, 18), num_sdgs)

        for sdg_num in aligned_sdgs:
            sdg_info = self.sdg_goals[sdg_num]

            # Calculate alignment score
            base_alignment = random.uniform(0.5, 0.95)

            # Adjust based on evidence
            if evidence:
                avg_evidence_confidence = sum(e.confidence for e in evidence) / len(evidence)
                alignment_score = (base_alignment + avg_evidence_confidence) / 2
            else:
                alignment_score = base_alignment

            # Determine contribution level
            if alignment_score >= 0.8:
                contribution_level = "high"
            elif alignment_score >= 0.6:
                contribution_level = "medium"
            elif alignment_score >= 0.4:
                contribution_level = "low"
            else:
                contribution_level = "neutral"

            sdg_metrics.append(SDGMetrics(
                goal_number=sdg_num,
                goal_name=sdg_info["name"],
                alignment_score=alignment_score,
                contribution_level=contribution_level,
                primary_indicators=sdg_info["indicators"][:2],
                metadata={"primary_metrics": sdg_info["primary_metrics"]},
            ))

        random.seed()  # Reset seed
        return sdg_metrics

    async def _quantify_impact_metrics(
        self,
        target_entity: str,
        evidence: List[Evidence],
        context: Optional[Dict[str, Any]] = None,
        sdg_mapping: Optional[List[SDGMetrics]] = None,
    ) -> List[ImpactMetric]:
        """Quantify specific impact metrics per $1M invested."""
        impact_metrics = []

        # Default investment amount
        investment_amount_million = 1.0
        if context and "investment_amount" in context:
            investment_amount_million = context["investment_amount"] / 1_000_000

        # Get sector multiplier
        sector = context.get("sector", "mixed") if context else "mixed"
        sector_multiplier = self.sector_multipliers.get(sector, 1.0)

        # Use entity hash for deterministic randomness
        seed = int(hashlib.md5(target_entity.encode()).hexdigest()[:8], 16)
        random.seed(seed)

        # Calculate key metrics
        for metric_name, model in self.impact_models.items():
            base_value = model["base_coefficient"]
            variance = model["variance"]

            # Apply sector multiplier if applicable
            if model.get("sector_dependent", False):
                base_value *= sector_multiplier

            # Add variance
            actual_value = base_value * random.uniform(1 - variance, 1 + variance)

            # Scale by investment amount
            total_value = actual_value * investment_amount_million

            impact_metrics.append(ImpactMetric(
                metric_name=metric_name,
                value=total_value,
                unit=self._get_metric_unit(metric_name),
                per_million_usd=actual_value,
                confidence=random.uniform(0.65, 0.92),
                calculation_method="Sector-adjusted impact modeling",
                data_sources=["Impact Database", "Sector Benchmarks"],
            ))

        random.seed()  # Reset seed
        return impact_metrics

    async def _generate_impact_pathways(
        self,
        target_entity: str,
        evidence: List[Evidence],
        context: Optional[Dict[str, Any]] = None,
        sdg_mapping: Optional[List[SDGMetrics]] = None,
    ) -> List[ImpactPathway]:
        """Generate impact pathways (theory of change)."""
        pathways = []

        if not sdg_mapping:
            return pathways

        # Group SDGs by theme
        environmental_sdgs = [sdg for sdg in sdg_mapping if sdg.goal_number in [6, 7, 12, 13, 14, 15]]
        social_sdgs = [sdg for sdg in sdg_mapping if sdg.goal_number in [1, 2, 3, 4, 5, 10]]
        economic_sdgs = [sdg for sdg in sdg_mapping if sdg.goal_number in [8, 9, 11]]
        governance_sdgs = [sdg for sdg in sdg_mapping if sdg.goal_number in [16, 17]]

        # Create pathway for each theme with aligned SDGs
        if environmental_sdgs:
            pathways.append(ImpactPathway(
                investment_area="Environmental Sustainability",
                sdg_goals=[sdg.goal_number for sdg in environmental_sdgs],
                intermediate_outcomes=[
                    "Reduced resource consumption",
                    "Improved environmental practices",
                    "Enhanced ecosystem services",
                ],
                final_outcomes=[
                    "Climate impact mitigation",
                    "Biodiversity preservation",
                    "Sustainable resource management",
                ],
                theory_of_change="Investment drives adoption of sustainable practices, leading to measurable environmental improvements",
                assumptions=["Technology adoption", "Regulatory support", "Market demand"],
            ))

        if social_sdgs:
            pathways.append(ImpactPathway(
                investment_area="Social Development",
                sdg_goals=[sdg.goal_number for sdg in social_sdgs],
                intermediate_outcomes=[
                    "Increased access to services",
                    "Enhanced capabilities",
                    "Improved quality of life",
                ],
                final_outcomes=[
                    "Poverty reduction",
                    "Health improvement",
                    "Educational advancement",
                ],
                theory_of_change="Investment expands access and quality of essential services, improving human development outcomes",
                assumptions=["Community engagement", "Service delivery capacity", "Behavioral change"],
            ))

        if economic_sdgs:
            pathways.append(ImpactPathway(
                investment_area="Economic Development",
                sdg_goals=[sdg.goal_number for sdg in economic_sdgs],
                intermediate_outcomes=[
                    "Job creation",
                    "Income generation",
                    "Market development",
                ],
                final_outcomes=[
                    "Economic growth",
                    "Reduced unemployment",
                    "Improved livelihoods",
                ],
                theory_of_change="Investment stimulates economic activity, creating employment and income opportunities",
                assumptions=["Market conditions", "Skills availability", "Infrastructure access"],
            ))

        return pathways

    def _create_impact_findings(
        self,
        target_entity: str,
        sdg_mapping: List[SDGMetrics],
        impact_metrics: List[ImpactMetric],
        impact_pathways: List[ImpactPathway],
        evidence: List[Evidence],
    ) -> List[Finding]:
        """Create findings from impact analysis."""
        findings = []

        # Finding 1: SDG Alignment
        high_alignment_sdgs = [
            sdg for sdg in sdg_mapping
            if sdg.contribution_level in ["high", "medium"]
        ]

        if high_alignment_sdgs:
            finding = Finding(
                agent_name=self.name,
                finding_type="sdg_alignment",
                severity="INFO",
                title=f"Strong Alignment with {len(high_alignment_sdgs)} SDG Goals",
                description=f"{target_entity} demonstrates significant contribution to {len(high_alignment_sdgs)} UN Sustainable Development Goals",
                confidence_score=0.82,
                metadata={
                    "aligned_sdgs": [
                        {
                            "number": sdg.goal_number,
                            "name": sdg.goal_name,
                            "alignment_score": sdg.alignment_score,
                            "contribution_level": sdg.contribution_level,
                        }
                        for sdg in high_alignment_sdgs
                    ],
                },
            )

            for e in evidence[:2]:
                finding.add_evidence(e)

            findings.append(finding)

        # Finding 2: Quantified Impact Metrics
        top_metrics = sorted(impact_metrics, key=lambda m: m.confidence, reverse=True)[:5]

        if top_metrics:
            finding = Finding(
                agent_name=self.name,
                finding_type="impact_quantification",
                severity="INFO",
                title="Quantified Impact Metrics",
                description=f"Calculated {len(impact_metrics)} measurable impact indicators per $1M invested",
                confidence_score=0.78,
                metadata={
                    "top_metrics": [
                        {
                            "name": m.metric_name,
                            "value": round(m.value, 2),
                            "unit": m.unit,
                            "per_million_usd": round(m.per_million_usd, 2),
                        }
                        for m in top_metrics
                    ],
                },
            )

            finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="Impact Modeling Engine",
                description="Quantitative impact calculations",
                data={"metrics_calculated": len(impact_metrics)},
                confidence=0.79,
            ))

            findings.append(finding)

        # Finding 3: Impact Pathways
        if impact_pathways:
            finding = Finding(
                agent_name=self.name,
                finding_type="impact_pathway",
                severity="INFO",
                title="Impact Pathways Identified",
                description=f"Mapped {len(impact_pathways)} clear pathways from investment to impact",
                confidence_score=0.75,
                metadata={
                    "pathways": [
                        {
                            "area": p.investment_area,
                            "sdg_goals": p.sdg_goals,
                            "theory_of_change": p.theory_of_change,
                        }
                        for p in impact_pathways
                    ],
                },
            )

            findings.append(finding)

        return findings

    def _get_metric_unit(self, metric_name: str) -> str:
        """Get the unit for a metric."""
        unit_map = {
            "lives_improved": "people",
            "co2_avoided_tons": "metric tons CO2e",
            "jobs_created": "FTE jobs",
            "clean_water_liters": "liters",
            "clean_energy_mwh": "MWh",
            "students_educated": "students",
            "healthcare_access_people": "people",
            "waste_reduced_tons": "metric tons",
            "forest_hectares_restored": "hectares",
            "housing_units_created": "housing units",
        }
        return unit_map.get(metric_name, "units")

    def generate_impact_report(
        self,
        report: AgentReport,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive impact report.

        Args:
            report: Agent report to generate from

        Returns:
            Formatted impact report
        """
        impact_report = {
            "entity": report.target_entity,
            "analysis_date": report.timestamp.isoformat(),
            "overall_impact_score": 100 - report.overall_risk_score,  # Convert risk to impact
            "sdg_alignment": report.metadata.get("sdg_alignment", []),
            "impact_metrics": report.metadata.get("impact_metrics", []),
            "impact_pathways": report.metadata.get("impact_pathways", []),
            "key_findings": [f.title for f in report.findings],
            "confidence_level": self._get_overall_confidence(report),
        }

        return impact_report

    def _get_overall_confidence(self, report: AgentReport) -> str:
        """Get overall confidence level."""
        if not report.findings:
            return "low"

        avg_confidence = sum(f.confidence_score for f in report.findings) / len(report.findings)

        if avg_confidence >= 0.8:
            return "very_high"
        elif avg_confidence >= 0.6:
            return "high"
        elif avg_confidence >= 0.4:
            return "medium"
        else:
            return "low"
