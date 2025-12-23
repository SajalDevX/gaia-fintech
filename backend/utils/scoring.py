"""
GAIA Scoring Engine
ESG scoring, SDG impact calculation, and risk assessment
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import math


class RiskLevel(Enum):
    """Risk level classifications."""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ESGScore:
    """ESG score breakdown."""
    environmental: float  # 0-100
    social: float  # 0-100
    governance: float  # 0-100

    @property
    def overall(self) -> float:
        """Calculate weighted overall ESG score."""
        # Weighted: E=40%, S=30%, G=30%
        return (self.environmental * 0.4 +
                self.social * 0.3 +
                self.governance * 0.3)

    @property
    def grade(self) -> str:
        """Get letter grade for ESG score."""
        score = self.overall
        if score >= 90:
            return "AAA"
        elif score >= 80:
            return "AA"
        elif score >= 70:
            return "A"
        elif score >= 60:
            return "BBB"
        elif score >= 50:
            return "BB"
        elif score >= 40:
            return "B"
        elif score >= 30:
            return "CCC"
        elif score >= 20:
            return "CC"
        elif score >= 10:
            return "C"
        else:
            return "D"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "environmental": round(self.environmental, 2),
            "social": round(self.social, 2),
            "governance": round(self.governance, 2),
            "overall": round(self.overall, 2),
            "grade": self.grade
        }


@dataclass
class SDGImpact:
    """SDG impact metrics."""
    goal_number: int
    goal_name: str
    contribution_score: float  # 0-100
    impact_description: str
    metrics: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "goal_number": self.goal_number,
            "goal_name": self.goal_name,
            "contribution_score": round(self.contribution_score, 2),
            "impact_description": self.impact_description,
            "metrics": self.metrics
        }


class ScoringEngine:
    """
    GAIA Scoring Engine for ESG and SDG calculations.
    """

    # SDG goal definitions
    SDG_GOALS = {
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
        17: "Partnerships for the Goals"
    }

    # Industry-specific SDG relevance weights
    INDUSTRY_SDG_WEIGHTS = {
        "energy": {7: 1.0, 13: 1.0, 9: 0.8, 12: 0.7, 11: 0.5},
        "manufacturing": {9: 1.0, 12: 1.0, 8: 0.8, 13: 0.7, 6: 0.5},
        "technology": {9: 1.0, 4: 0.8, 8: 0.7, 10: 0.6, 17: 0.5},
        "finance": {1: 0.8, 8: 1.0, 10: 0.9, 16: 0.7, 17: 0.6},
        "healthcare": {3: 1.0, 1: 0.7, 10: 0.6, 5: 0.5, 17: 0.4},
        "agriculture": {2: 1.0, 15: 0.9, 6: 0.8, 12: 0.7, 13: 0.6},
        "retail": {12: 1.0, 8: 0.8, 5: 0.6, 10: 0.5, 1: 0.4},
        "default": {8: 0.7, 12: 0.7, 13: 0.6, 16: 0.5, 17: 0.4}
    }

    def __init__(self):
        self.weights = {
            "environmental": {
                "carbon_emissions": 0.25,
                "renewable_energy": 0.20,
                "water_usage": 0.15,
                "waste_management": 0.15,
                "biodiversity": 0.10,
                "pollution": 0.15
            },
            "social": {
                "labor_practices": 0.25,
                "health_safety": 0.20,
                "diversity_inclusion": 0.15,
                "community_impact": 0.15,
                "human_rights": 0.15,
                "product_safety": 0.10
            },
            "governance": {
                "board_independence": 0.20,
                "executive_compensation": 0.15,
                "shareholder_rights": 0.15,
                "transparency": 0.20,
                "ethics_compliance": 0.20,
                "risk_management": 0.10
            }
        }

    def calculate_esg_score(
        self,
        environmental_factors: Dict[str, float],
        social_factors: Dict[str, float],
        governance_factors: Dict[str, float]
    ) -> ESGScore:
        """
        Calculate comprehensive ESG score from factor inputs.

        Args:
            environmental_factors: Dict of factor name to score (0-100)
            social_factors: Dict of factor name to score (0-100)
            governance_factors: Dict of factor name to score (0-100)

        Returns:
            ESGScore with all components
        """
        e_score = self._calculate_weighted_score(
            environmental_factors,
            self.weights["environmental"]
        )
        s_score = self._calculate_weighted_score(
            social_factors,
            self.weights["social"]
        )
        g_score = self._calculate_weighted_score(
            governance_factors,
            self.weights["governance"]
        )

        return ESGScore(
            environmental=e_score,
            social=s_score,
            governance=g_score
        )

    def _calculate_weighted_score(
        self,
        factors: Dict[str, float],
        weights: Dict[str, float]
    ) -> float:
        """Calculate weighted score from factors."""
        total_weight = 0
        weighted_sum = 0

        for factor, weight in weights.items():
            if factor in factors:
                weighted_sum += factors[factor] * weight
                total_weight += weight

        if total_weight == 0:
            return 50.0  # Default neutral score

        return weighted_sum / total_weight

    def calculate_sdg_impact(
        self,
        company_data: Dict[str, Any],
        industry: str = "default"
    ) -> List[SDGImpact]:
        """
        Calculate SDG impact scores for a company.

        Args:
            company_data: Company metrics and characteristics
            industry: Industry classification

        Returns:
            List of SDGImpact for relevant goals
        """
        impacts = []
        industry_weights = self.INDUSTRY_SDG_WEIGHTS.get(
            industry.lower(),
            self.INDUSTRY_SDG_WEIGHTS["default"]
        )

        for goal_num, goal_name in self.SDG_GOALS.items():
            relevance = industry_weights.get(goal_num, 0.3)

            # Calculate contribution score based on company data
            base_score = self._calculate_goal_contribution(
                goal_num,
                company_data
            )
            contribution = base_score * relevance

            # Generate impact metrics
            metrics = self._generate_impact_metrics(
                goal_num,
                company_data,
                contribution
            )

            if contribution > 10:  # Only include relevant goals
                impacts.append(SDGImpact(
                    goal_number=goal_num,
                    goal_name=goal_name,
                    contribution_score=min(100, contribution),
                    impact_description=self._generate_impact_description(
                        goal_num,
                        contribution,
                        metrics
                    ),
                    metrics=metrics
                ))

        return sorted(impacts, key=lambda x: x.contribution_score, reverse=True)

    def _calculate_goal_contribution(
        self,
        goal_num: int,
        company_data: Dict[str, Any]
    ) -> float:
        """Calculate contribution score for a specific SDG goal."""
        esg = company_data.get("esg_scores", {})

        # Map goals to relevant ESG factors
        goal_factor_mapping = {
            1: ["community_impact", "labor_practices"],
            2: ["biodiversity", "community_impact"],
            3: ["health_safety", "product_safety"],
            4: ["community_impact", "diversity_inclusion"],
            5: ["diversity_inclusion", "labor_practices"],
            6: ["water_usage", "pollution"],
            7: ["renewable_energy", "carbon_emissions"],
            8: ["labor_practices", "ethics_compliance"],
            9: ["transparency", "risk_management"],
            10: ["diversity_inclusion", "community_impact"],
            11: ["waste_management", "community_impact"],
            12: ["waste_management", "pollution"],
            13: ["carbon_emissions", "renewable_energy"],
            14: ["water_usage", "biodiversity"],
            15: ["biodiversity", "waste_management"],
            16: ["ethics_compliance", "transparency"],
            17: ["transparency", "shareholder_rights"]
        }

        factors = goal_factor_mapping.get(goal_num, [])
        if not factors:
            return 50.0

        scores = []
        for factor in factors:
            for category in ["environmental", "social", "governance"]:
                if factor in esg.get(category, {}):
                    scores.append(esg[category][factor])

        return sum(scores) / len(scores) if scores else 50.0

    def _generate_impact_metrics(
        self,
        goal_num: int,
        company_data: Dict[str, Any],
        contribution: float
    ) -> Dict[str, Any]:
        """Generate specific impact metrics for a goal."""
        investment = company_data.get("market_cap", 1000000000)

        # Base metrics per $1M invested (scaled by contribution)
        base_metrics = {
            1: {"poverty_reduction": 100, "unit": "people lifted"},
            2: {"meals_provided": 10000, "unit": "meals"},
            3: {"healthcare_access": 500, "unit": "people served"},
            4: {"education_hours": 50000, "unit": "hours"},
            5: {"women_empowered": 200, "unit": "women"},
            6: {"water_access": 1000, "unit": "people"},
            7: {"clean_energy_mwh": 500, "unit": "MWh"},
            8: {"jobs_created": 50, "unit": "jobs"},
            9: {"innovations": 10, "unit": "patents"},
            10: {"inequality_reduction": 15, "unit": "percent"},
            11: {"sustainable_buildings": 5, "unit": "buildings"},
            12: {"waste_diverted_tons": 100, "unit": "tons"},
            13: {"co2_avoided_tons": 500, "unit": "tons CO2"},
            14: {"ocean_protected_km2": 10, "unit": "km²"},
            15: {"land_restored_hectares": 50, "unit": "hectares"},
            16: {"governance_improvements": 20, "unit": "policies"},
            17: {"partnerships": 15, "unit": "partnerships"}
        }

        metric_info = base_metrics.get(goal_num, {"impact": 100, "unit": "units"})
        scale = (contribution / 100) * (investment / 1000000)

        metric_key = list(metric_info.keys())[0]
        if metric_key == "unit":
            metric_key = list(metric_info.keys())[1] if len(metric_info) > 1 else "impact"

        return {
            "per_million_invested": metric_info.get(metric_key, 100),
            "projected_annual_impact": round(scale * metric_info.get(metric_key, 100)),
            "unit": metric_info.get("unit", "units"),
            "confidence": round(min(95, 60 + contribution * 0.35), 1)
        }

    def _generate_impact_description(
        self,
        goal_num: int,
        contribution: float,
        metrics: Dict[str, Any]
    ) -> str:
        """Generate human-readable impact description."""
        impact_value = metrics.get("projected_annual_impact", 0)
        unit = metrics.get("unit", "units")

        descriptions = {
            1: f"Projected to help {impact_value:,} {unit} annually through inclusive economic practices",
            2: f"Contributing to food security with {impact_value:,} {unit} supported annually",
            3: f"Improving health outcomes for {impact_value:,} {unit}",
            4: f"Enabling {impact_value:,} {unit} of educational opportunity",
            5: f"Empowering {impact_value:,} {unit} through gender equality initiatives",
            6: f"Providing clean water access to {impact_value:,} {unit}",
            7: f"Generating {impact_value:,} {unit} of renewable energy annually",
            8: f"Creating {impact_value:,} {unit} with fair labor practices",
            9: f"Driving innovation with {impact_value:,} {unit}",
            10: f"Reducing inequality by {impact_value:,} {unit}",
            11: f"Building {impact_value:,} {unit} with sustainable design",
            12: f"Diverting {impact_value:,} {unit} from landfills annually",
            13: f"Avoiding {impact_value:,} {unit} of greenhouse gas emissions",
            14: f"Protecting {impact_value:,} {unit} of ocean ecosystem",
            15: f"Restoring {impact_value:,} {unit} of natural habitat",
            16: f"Implementing {impact_value:,} {unit} for better governance",
            17: f"Fostering {impact_value:,} {unit} for sustainable development"
        }

        return descriptions.get(goal_num, f"Contributing {impact_value:,} {unit} to sustainable development")

    def calculate_greenwashing_risk(
        self,
        reported_scores: Dict[str, float],
        verified_scores: Dict[str, float],
        discrepancies: List[Dict[str, Any]]
    ) -> Tuple[float, RiskLevel, List[str]]:
        """
        Calculate greenwashing risk based on reported vs verified data.

        Args:
            reported_scores: Self-reported ESG scores
            verified_scores: Agent-verified ESG scores
            discrepancies: List of identified discrepancies

        Returns:
            Tuple of (risk_score, risk_level, evidence_list)
        """
        # Calculate score discrepancy
        score_gaps = []
        for key in reported_scores:
            if key in verified_scores:
                gap = reported_scores[key] - verified_scores[key]
                if gap > 0:  # Only count over-reporting
                    score_gaps.append(gap)

        avg_gap = sum(score_gaps) / len(score_gaps) if score_gaps else 0

        # Factor in number of discrepancies
        discrepancy_factor = min(50, len(discrepancies) * 10)

        # Calculate severity of discrepancies
        severity_scores = []
        for d in discrepancies:
            severity = d.get("severity", "low")
            if severity == "critical":
                severity_scores.append(40)
            elif severity == "high":
                severity_scores.append(25)
            elif severity == "medium":
                severity_scores.append(15)
            else:
                severity_scores.append(5)

        avg_severity = sum(severity_scores) / len(severity_scores) if severity_scores else 0

        # Combined risk score
        risk_score = min(100, avg_gap + discrepancy_factor + avg_severity)

        # Determine risk level
        if risk_score >= 80:
            risk_level = RiskLevel.CRITICAL
        elif risk_score >= 60:
            risk_level = RiskLevel.HIGH
        elif risk_score >= 40:
            risk_level = RiskLevel.MODERATE
        elif risk_score >= 20:
            risk_level = RiskLevel.LOW
        else:
            risk_level = RiskLevel.MINIMAL

        # Generate evidence list
        evidence = []
        if avg_gap > 20:
            evidence.append(f"Significant ESG score inflation detected: {avg_gap:.1f} point average overstatement")
        if len(discrepancies) > 3:
            evidence.append(f"Multiple verification failures: {len(discrepancies)} discrepancies identified")
        for d in discrepancies:
            if d.get("severity") in ["critical", "high"]:
                evidence.append(f"{d.get('type', 'Issue')}: {d.get('description', 'No details')}")

        return risk_score, risk_level, evidence

    def generate_investment_recommendation(
        self,
        esg_score: ESGScore,
        sdg_impacts: List[SDGImpact],
        greenwashing_risk: float,
        risk_level: RiskLevel
    ) -> Dict[str, Any]:
        """Generate investment recommendation based on all factors."""
        # Calculate composite score
        sdg_avg = sum(i.contribution_score for i in sdg_impacts) / len(sdg_impacts) if sdg_impacts else 50

        # Penalize for greenwashing risk
        risk_penalty = greenwashing_risk * 0.5

        composite_score = (
            esg_score.overall * 0.4 +
            sdg_avg * 0.3 +
            (100 - risk_penalty) * 0.3
        )

        # Determine recommendation
        if risk_level == RiskLevel.CRITICAL:
            recommendation = "AVOID"
            confidence = 95
            rationale = "Critical greenwashing risk detected. Significant discrepancies between reported and verified sustainability data."
        elif risk_level == RiskLevel.HIGH:
            recommendation = "CAUTION"
            confidence = 85
            rationale = "High greenwashing risk. Consider additional due diligence before investment."
        elif composite_score >= 75:
            recommendation = "STRONG BUY"
            confidence = 80 + (composite_score - 75)
            rationale = "Strong sustainability profile with verified positive impact."
        elif composite_score >= 60:
            recommendation = "BUY"
            confidence = 70 + (composite_score - 60)
            rationale = "Good sustainability metrics with acceptable risk profile."
        elif composite_score >= 45:
            recommendation = "HOLD"
            confidence = 60
            rationale = "Average sustainability performance. Monitor for improvements."
        else:
            recommendation = "UNDERWEIGHT"
            confidence = 55
            rationale = "Below-average sustainability metrics. Consider alternatives."

        return {
            "recommendation": recommendation,
            "confidence": min(99, round(confidence, 1)),
            "composite_score": round(composite_score, 2),
            "rationale": rationale,
            "esg_grade": esg_score.grade,
            "top_sdg_impacts": [
                {"goal": i.goal_number, "score": round(i.contribution_score, 1)}
                for i in sdg_impacts[:5]
            ],
            "risk_level": risk_level.value,
            "greenwashing_risk_score": round(greenwashing_risk, 1)
        }


# Singleton instance
_scoring_engine: ScoringEngine | None = None


def get_scoring_engine() -> ScoringEngine:
    """Get or create the scoring engine instance."""
    global _scoring_engine
    if _scoring_engine is None:
        _scoring_engine = ScoringEngine()
    return _scoring_engine
