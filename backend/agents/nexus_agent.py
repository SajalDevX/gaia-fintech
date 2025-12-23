"""
NEXUS Agent - Financial Inclusion Intelligence

New Economy eXpansion & Underserved Services Agent

Specialized AI agent for analyzing financial inclusion impact on underserved
populations. Addresses SDG 1 (No Poverty), SDG 5 (Gender Equality),
SDG 8 (Decent Work), SDG 9 (Industry/Innovation), SDG 10 (Reduced Inequalities).

Design Philosophy:
- Human-centered: Focus on real impact on people's lives
- Intersectional: Consider multiple dimensions of exclusion
- Evidence-based: Detect "inclusion washing" with same rigor as greenwashing
- Actionable: Provide concrete recommendations for improvement

Author: GAIA Project
"""

import asyncio
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from enum import Enum

from .base_agent import (
    BaseAgent,
    AgentReport,
    Finding,
    Evidence,
    EvidenceType,
    ConfidenceLevel,
)

from models.inclusion import (
    UnderservedSegment,
    InclusionChannel,
    InclusionRiskLevel,
    AccessMetrics,
    CreditMetrics,
    GenderInclusionMetrics,
    GeographicInclusionMetrics,
    VulnerablePopulationMetrics,
    AffordabilityMetrics,
    InclusionWashingIndicator,
    InclusionWashingAnalysis,
    FinancialInclusionScore,
    FinancialInclusionReport,
)


class InclusionDataSource(str, Enum):
    """Data sources for financial inclusion analysis"""
    MIX_MARKET = "mix_market"  # Microfinance Information Exchange
    CGAP = "cgap"  # Consultative Group to Assist the Poor
    WORLD_BANK_FINDEX = "world_bank_findex"  # Global Findex Database
    GSMA = "gsma"  # Mobile money data
    COMPANY_REPORTS = "company_reports"
    REGULATORY_FILINGS = "regulatory_filings"
    IMPACT_ASSESSMENTS = "impact_assessments"
    CUSTOMER_SURVEYS = "customer_surveys"
    THIRD_PARTY_AUDITS = "third_party_audits"


class NexusAgent(BaseAgent):
    """
    NEXUS Agent: Financial Inclusion Intelligence

    Analyzes company's impact on financial inclusion for underserved populations.
    Detects "inclusion washing" - false or exaggerated claims about serving
    the underserved.

    Key Capabilities:
    1. Access Analysis - Who can reach financial services?
    2. Credit Analysis - Who can borrow at fair terms?
    3. Gender Analysis - Are women equally served?
    4. Geographic Analysis - Are rural/remote areas covered?
    5. Vulnerable Population Analysis - Are the most vulnerable protected?
    6. Affordability Analysis - Can low-income people afford services?
    7. Inclusion Washing Detection - Are claims authentic?
    """

    def __init__(self, **kwargs):
        super().__init__(
            agent_id="nexus",
            name="NEXUS",
            description="Financial Inclusion Intelligence Agent",
            **kwargs
        )

        # Weights for calculating overall inclusion score
        self.score_weights = {
            "access": 0.20,
            "credit": 0.20,
            "gender": 0.15,
            "geographic": 0.15,
            "vulnerable": 0.15,
            "affordability": 0.15
        }

        # Industry benchmarks (would come from real data in production)
        self.industry_benchmarks = {
            "fintech": {"inclusion_score": 65.0, "access": 70.0, "gender": 55.0},
            "banking": {"inclusion_score": 45.0, "access": 50.0, "gender": 40.0},
            "microfinance": {"inclusion_score": 80.0, "access": 85.0, "gender": 75.0},
            "insurance": {"inclusion_score": 40.0, "access": 45.0, "gender": 38.0},
            "default": {"inclusion_score": 50.0, "access": 55.0, "gender": 45.0}
        }

        # Red flag patterns for inclusion washing
        self.inclusion_washing_patterns = [
            {
                "name": "Impact Inflation",
                "description": "Claims of impact far exceed verifiable metrics",
                "check": self._check_impact_inflation
            },
            {
                "name": "Cherry-Picked Geography",
                "description": "Highlighting single success region while ignoring failures",
                "check": self._check_cherry_picked_geography
            },
            {
                "name": "Token Women's Products",
                "description": "Marketing women-focused products without real design changes",
                "check": self._check_token_gender_products
            },
            {
                "name": "Predatory Pricing",
                "description": "High effective rates disguised as affordable credit",
                "check": self._check_predatory_pricing
            },
            {
                "name": "Phantom Financial Literacy",
                "description": "Counting marketing as financial education",
                "check": self._check_phantom_literacy
            },
            {
                "name": "Access Point Inflation",
                "description": "Counting inactive or inaccessible service points",
                "check": self._check_access_inflation
            }
        ]

    async def analyze(
        self,
        company_name: str,
        ticker: str,
        company_data: Optional[Dict] = None,
        **kwargs
    ) -> FinancialInclusionReport:
        """
        Perform comprehensive financial inclusion analysis.

        Args:
            company_name: Name of the company
            ticker: Stock ticker symbol
            company_data: Optional pre-fetched company data
            **kwargs: Additional analysis parameters

        Returns:
            FinancialInclusionReport with complete inclusion analysis
        """
        self.logger.info(f"Starting financial inclusion analysis for {company_name}")

        analysis_id = f"nexus_{ticker}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        # Gather data from multiple sources
        await self._emit_progress(10, "Gathering financial inclusion data...")
        inclusion_data = await self._gather_inclusion_data(company_name, ticker, company_data)

        # Analyze each dimension
        await self._emit_progress(20, "Analyzing access metrics...")
        access_metrics = await self._analyze_access(inclusion_data)

        await self._emit_progress(30, "Analyzing credit inclusion...")
        credit_metrics = await self._analyze_credit(inclusion_data)

        await self._emit_progress(40, "Analyzing gender inclusion...")
        gender_metrics = await self._analyze_gender_inclusion(inclusion_data)

        await self._emit_progress(50, "Analyzing geographic reach...")
        geographic_metrics = await self._analyze_geographic_inclusion(inclusion_data)

        await self._emit_progress(60, "Analyzing vulnerable population services...")
        vulnerable_metrics = await self._analyze_vulnerable_populations(inclusion_data)

        await self._emit_progress(70, "Analyzing affordability...")
        affordability_metrics = await self._analyze_affordability(inclusion_data)

        await self._emit_progress(80, "Detecting inclusion washing risks...")
        washing_analysis = await self._detect_inclusion_washing(
            inclusion_data,
            access_metrics,
            credit_metrics,
            gender_metrics,
            geographic_metrics,
            vulnerable_metrics,
            affordability_metrics
        )

        await self._emit_progress(90, "Calculating final scores...")
        inclusion_score = self._calculate_inclusion_score(
            access_metrics,
            credit_metrics,
            gender_metrics,
            geographic_metrics,
            vulnerable_metrics,
            affordability_metrics
        )

        # Determine segments and channels
        segments_served = self._identify_segments_served(inclusion_data)
        channels_used = self._identify_channels(inclusion_data)

        # Calculate SDG alignment
        sdg_alignment = self._calculate_sdg_alignment(
            access_metrics,
            credit_metrics,
            gender_metrics,
            geographic_metrics,
            vulnerable_metrics,
            affordability_metrics
        )

        # Generate insights
        strengths, weaknesses, opportunities, risks = self._generate_swot(
            access_metrics,
            credit_metrics,
            gender_metrics,
            geographic_metrics,
            vulnerable_metrics,
            affordability_metrics,
            washing_analysis
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            inclusion_score,
            washing_analysis,
            weaknesses,
            opportunities
        )

        # Calculate total lives impacted
        total_lives = self._calculate_total_impact(
            access_metrics,
            credit_metrics,
            gender_metrics,
            vulnerable_metrics
        )

        await self._emit_progress(100, "Analysis complete")

        return FinancialInclusionReport(
            company_ticker=ticker,
            company_name=company_name,
            analysis_date=datetime.now(timezone.utc),
            analysis_id=analysis_id,
            inclusion_score=inclusion_score,
            inclusion_washing_analysis=washing_analysis,
            access_metrics=access_metrics,
            credit_metrics=credit_metrics,
            gender_metrics=gender_metrics,
            geographic_metrics=geographic_metrics,
            vulnerable_metrics=vulnerable_metrics,
            affordability_metrics=affordability_metrics,
            primary_segments_served=segments_served,
            channels_utilized=channels_used,
            total_lives_impacted_per_million=total_lives,
            sdg_alignment=sdg_alignment,
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            risks=risks,
            recommendations=recommendations,
            confidence_level=self._calculate_confidence(inclusion_data),
            data_sources=[s.value for s in self._get_data_sources(inclusion_data)],
            methodology_notes="Analysis based on GIIN IRIS+ metrics, CGAP guidelines, and GISD framework"
        )

    async def _gather_inclusion_data(
        self,
        company_name: str,
        ticker: str,
        company_data: Optional[Dict]
    ) -> Dict:
        """Gather inclusion data from multiple sources"""
        # In production, this would fetch from real APIs
        # For prototype, using simulated data based on company profile

        data = {
            "company_name": company_name,
            "ticker": ticker,
            "industry": self._detect_industry(company_name, company_data),
            "has_inclusion_focus": self._detect_inclusion_focus(company_name, company_data),
            "geographic_presence": [],
            "products": [],
            "reported_metrics": {},
            "third_party_data": {},
            "news_sentiment": {},
            "regulatory_status": {}
        }

        # Simulate data gathering with realistic patterns
        if company_data:
            data.update(company_data.get("inclusion_data", {}))

        # Add simulated market data
        data["market_data"] = await self._fetch_market_data(ticker)

        return data

    def _detect_industry(self, company_name: str, company_data: Optional[Dict]) -> str:
        """Detect company's industry for benchmark comparison"""
        name_lower = company_name.lower()

        if any(term in name_lower for term in ["microfinance", "micro", "mfi"]):
            return "microfinance"
        elif any(term in name_lower for term in ["fintech", "pay", "mobile", "digital"]):
            return "fintech"
        elif any(term in name_lower for term in ["bank", "credit union", "savings"]):
            return "banking"
        elif any(term in name_lower for term in ["insurance", "assurance"]):
            return "insurance"

        if company_data and "industry" in company_data:
            return company_data["industry"]

        return "default"

    def _detect_inclusion_focus(self, company_name: str, company_data: Optional[Dict]) -> bool:
        """Detect if company has explicit financial inclusion focus"""
        inclusion_keywords = [
            "inclusion", "underserved", "unbanked", "microfinance",
            "micro", "rural", "women", "smallholder", "impact"
        ]

        name_lower = company_name.lower()
        if any(kw in name_lower for kw in inclusion_keywords):
            return True

        if company_data and company_data.get("mission_includes_inclusion"):
            return True

        return False

    async def _fetch_market_data(self, ticker: str) -> Dict:
        """Fetch market data for analysis"""
        await asyncio.sleep(0.1)  # Simulate API call
        return {
            "market_cap_category": "mid",
            "growth_rate": random.uniform(5, 25),
            "investor_type": "impact"
        }

    async def _analyze_access(self, data: Dict) -> AccessMetrics:
        """Analyze financial access metrics"""
        await asyncio.sleep(0.1)

        industry = data.get("industry", "default")
        has_focus = data.get("has_inclusion_focus", False)

        # Generate realistic metrics based on industry and focus
        base_multiplier = 1.5 if has_focus else 1.0

        if industry == "microfinance":
            base_access = 75
            unbanked_reached = int(random.uniform(800, 1500) * base_multiplier)
            mobile_users = int(random.uniform(500, 1000) * base_multiplier)
            agents = int(random.uniform(50, 150) * base_multiplier)
        elif industry == "fintech":
            base_access = 65
            unbanked_reached = int(random.uniform(400, 900) * base_multiplier)
            mobile_users = int(random.uniform(800, 2000) * base_multiplier)
            agents = int(random.uniform(10, 50) * base_multiplier)
        elif industry == "banking":
            base_access = 45
            unbanked_reached = int(random.uniform(100, 400) * base_multiplier)
            mobile_users = int(random.uniform(200, 500) * base_multiplier)
            agents = int(random.uniform(20, 80) * base_multiplier)
        else:
            base_access = 40
            unbanked_reached = int(random.uniform(50, 200) * base_multiplier)
            mobile_users = int(random.uniform(100, 300) * base_multiplier)
            agents = int(random.uniform(5, 30) * base_multiplier)

        access_score = min(100, base_access * base_multiplier + random.uniform(-10, 10))

        return AccessMetrics(
            unbanked_individuals_reached_per_million=unbanked_reached,
            new_accounts_opened_per_million=int(unbanked_reached * 1.2),
            active_users_per_million=int(unbanked_reached * 0.7),
            mobile_money_users_enabled_per_million=mobile_users,
            digital_payment_points_created_per_million=int(mobile_users * 0.3),
            smartphone_penetration_increase=random.uniform(2, 15),
            last_mile_agents_deployed_per_million=agents,
            average_distance_to_access_point_km=random.uniform(2, 20),
            access_score=access_score
        )

    async def _analyze_credit(self, data: Dict) -> CreditMetrics:
        """Analyze credit inclusion metrics"""
        await asyncio.sleep(0.1)

        industry = data.get("industry", "default")
        has_focus = data.get("has_inclusion_focus", False)

        base_multiplier = 1.4 if has_focus else 1.0

        if industry == "microfinance":
            microloans = int(random.uniform(500, 1200) * base_multiplier)
            avg_loan = random.uniform(150, 500)
            first_time = int(microloans * 0.4)
            approval_rate = random.uniform(60, 85)
            credit_score = random.uniform(70, 90)
        elif industry == "fintech":
            microloans = int(random.uniform(300, 800) * base_multiplier)
            avg_loan = random.uniform(200, 800)
            first_time = int(microloans * 0.5)
            approval_rate = random.uniform(50, 75)
            credit_score = random.uniform(55, 75)
        else:
            microloans = int(random.uniform(50, 300) * base_multiplier)
            avg_loan = random.uniform(500, 2000)
            first_time = int(microloans * 0.2)
            approval_rate = random.uniform(30, 55)
            credit_score = random.uniform(35, 55)

        return CreditMetrics(
            microloans_disbursed_per_million=microloans,
            average_microloan_size_usd=avg_loan,
            first_time_borrowers_per_million=first_time,
            sme_loans_to_underserved_per_million=int(microloans * 0.15),
            informal_business_formalization_rate=random.uniform(5, 25),
            average_interest_rate_vs_market=random.uniform(-5, 15),
            interest_rate_fairness_index=random.uniform(40, 85),
            alternative_data_credit_scores_enabled=int(microloans * 0.6),
            credit_approval_rate_underserved=approval_rate,
            portfolio_at_risk_30_days=random.uniform(2, 12),
            client_retention_rate=random.uniform(60, 90),
            credit_score=credit_score
        )

    async def _analyze_gender_inclusion(self, data: Dict) -> GenderInclusionMetrics:
        """Analyze gender-based financial inclusion"""
        await asyncio.sleep(0.1)

        industry = data.get("industry", "default")
        has_focus = data.get("has_inclusion_focus", False)

        # Gender parity varies significantly by region and company focus
        base_multiplier = 1.3 if has_focus else 1.0

        if industry == "microfinance":
            # Microfinance historically serves more women
            women_accounts = int(random.uniform(600, 1200) * base_multiplier)
            women_entrepreneurs = int(random.uniform(200, 500) * base_multiplier)
            parity_index = random.uniform(0.7, 1.1)
            gender_score = random.uniform(65, 90)
            has_women_products = random.choice([True, True, True, False])
        elif industry == "fintech":
            women_accounts = int(random.uniform(300, 700) * base_multiplier)
            women_entrepreneurs = int(random.uniform(100, 300) * base_multiplier)
            parity_index = random.uniform(0.5, 0.8)
            gender_score = random.uniform(45, 70)
            has_women_products = random.choice([True, False])
        else:
            women_accounts = int(random.uniform(100, 400) * base_multiplier)
            women_entrepreneurs = int(random.uniform(30, 150) * base_multiplier)
            parity_index = random.uniform(0.3, 0.6)
            gender_score = random.uniform(30, 55)
            has_women_products = random.choice([True, False, False, False])

        return GenderInclusionMetrics(
            women_account_holders_per_million=women_accounts,
            women_entrepreneurs_funded_per_million=women_entrepreneurs,
            female_headed_household_loans_per_million=int(women_entrepreneurs * 0.8),
            gender_parity_index=parity_index,
            women_in_leadership_percent=random.uniform(15, 45),
            women_loan_officers_percent=random.uniform(25, 60),
            has_women_focused_products=has_women_products,
            maternity_friendly_loan_terms=has_women_products and random.choice([True, False]),
            women_savings_groups_supported=int(random.uniform(10, 100) * base_multiplier),
            women_economic_empowerment_score=gender_score * 0.95,
            gender_inclusion_score=gender_score
        )

    async def _analyze_geographic_inclusion(self, data: Dict) -> GeographicInclusionMetrics:
        """Analyze geographic financial inclusion"""
        await asyncio.sleep(0.1)

        industry = data.get("industry", "default")
        has_focus = data.get("has_inclusion_focus", False)

        base_multiplier = 1.3 if has_focus else 1.0

        if industry == "microfinance":
            rural_coverage = random.uniform(40, 75)
            rural_agents = int(random.uniform(80, 200) * base_multiplier)
            last_mile = int(random.uniform(20, 80) * base_multiplier)
            geo_score = random.uniform(60, 85)
        elif industry == "fintech":
            rural_coverage = random.uniform(20, 50)
            rural_agents = int(random.uniform(20, 80) * base_multiplier)
            last_mile = int(random.uniform(10, 40) * base_multiplier)
            geo_score = random.uniform(40, 65)
        else:
            rural_coverage = random.uniform(10, 35)
            rural_agents = int(random.uniform(10, 50) * base_multiplier)
            last_mile = int(random.uniform(5, 20) * base_multiplier)
            geo_score = random.uniform(25, 50)

        return GeographicInclusionMetrics(
            rural_population_coverage_percent=rural_coverage,
            rural_branches_per_100k_population=random.uniform(0.5, 5),
            rural_agents_deployed_per_million=rural_agents,
            last_mile_communities_reached=last_mile,
            average_travel_time_reduction_minutes=random.uniform(15, 90),
            urban_slum_coverage_percent=random.uniform(15, 50),
            informal_settlement_agents=int(rural_agents * 0.3),
            remittance_corridors_served=int(random.uniform(5, 30)),
            remittance_cost_reduction_percent=random.uniform(10, 40),
            geographic_inclusion_score=geo_score
        )

    async def _analyze_vulnerable_populations(self, data: Dict) -> VulnerablePopulationMetrics:
        """Analyze services for vulnerable populations"""
        await asyncio.sleep(0.1)

        industry = data.get("industry", "default")
        has_focus = data.get("has_inclusion_focus", False)

        base_multiplier = 1.4 if has_focus else 1.0

        if industry == "microfinance":
            refugees = int(random.uniform(50, 200) * base_multiplier)
            youth = int(random.uniform(100, 400) * base_multiplier)
            disability_accessible = random.uniform(30, 60)
            vulnerable_score = random.uniform(55, 80)
        elif industry == "fintech":
            refugees = int(random.uniform(20, 100) * base_multiplier)
            youth = int(random.uniform(200, 600) * base_multiplier)
            disability_accessible = random.uniform(40, 70)
            vulnerable_score = random.uniform(45, 70)
        else:
            refugees = int(random.uniform(5, 50) * base_multiplier)
            youth = int(random.uniform(50, 200) * base_multiplier)
            disability_accessible = random.uniform(20, 45)
            vulnerable_score = random.uniform(30, 50)

        return VulnerablePopulationMetrics(
            refugees_served_per_million=refugees,
            has_refugee_specific_products=has_focus and random.choice([True, False]),
            disability_accessible_branches_percent=disability_accessible,
            has_screen_reader_compatible_app=random.choice([True, False]),
            has_sign_language_support=random.choice([True, False, False]),
            youth_accounts_per_million=youth,
            financial_literacy_programs_youth=int(youth * 0.3),
            elderly_friendly_services=random.choice([True, False]),
            pension_disbursement_digitized=industry in ["banking", "fintech"],
            gig_worker_financial_products=industry == "fintech",
            informal_workers_formalized_per_million=int(random.uniform(50, 300) * base_multiplier),
            vulnerable_population_score=vulnerable_score
        )

    async def _analyze_affordability(self, data: Dict) -> AffordabilityMetrics:
        """Analyze affordability of financial services"""
        await asyncio.sleep(0.1)

        industry = data.get("industry", "default")
        has_focus = data.get("has_inclusion_focus", False)

        if industry == "microfinance":
            zero_balance = True
            zero_fee = random.choice([True, True, False])
            monthly_fee = random.uniform(0, 2)
            effective_rate = random.uniform(18, 45)
            affordability_score = random.uniform(60, 85)
        elif industry == "fintech":
            zero_balance = random.choice([True, True, False])
            zero_fee = random.choice([True, False])
            monthly_fee = random.uniform(0, 5)
            effective_rate = random.uniform(15, 50)
            affordability_score = random.uniform(50, 75)
        else:
            zero_balance = random.choice([True, False, False])
            zero_fee = random.choice([True, False, False])
            monthly_fee = random.uniform(2, 15)
            effective_rate = random.uniform(20, 60)
            affordability_score = random.uniform(30, 55)

        return AffordabilityMetrics(
            has_zero_balance_accounts=zero_balance,
            has_zero_fee_basic_account=zero_fee,
            average_monthly_fee_usd=monthly_fee,
            transaction_fee_percent_of_min_wage=random.uniform(0.1, 2),
            free_transactions_per_month=int(random.uniform(0, 20)),
            effective_annual_rate_microloans=effective_rate,
            has_flexible_repayment=has_focus or random.choice([True, False]),
            grace_period_days=int(random.uniform(0, 14)),
            fee_transparency_score=random.uniform(40, 90),
            has_plain_language_terms=random.choice([True, False]),
            available_in_local_languages=int(random.uniform(1, 10)),
            affordability_score=affordability_score
        )

    async def _detect_inclusion_washing(
        self,
        data: Dict,
        access: AccessMetrics,
        credit: CreditMetrics,
        gender: GenderInclusionMetrics,
        geographic: GeographicInclusionMetrics,
        vulnerable: VulnerablePopulationMetrics,
        affordability: AffordabilityMetrics
    ) -> InclusionWashingAnalysis:
        """
        Detect potential inclusion washing - false or exaggerated claims
        about serving underserved populations.
        """
        indicators = []
        risk_score = 0

        # Check each pattern
        metrics = {
            "access": access,
            "credit": credit,
            "gender": gender,
            "geographic": geographic,
            "vulnerable": vulnerable,
            "affordability": affordability
        }

        for pattern in self.inclusion_washing_patterns:
            result = await pattern["check"](data, metrics)
            if result:
                indicators.append(result)
                if result.severity == InclusionRiskLevel.CRITICAL:
                    risk_score += 30
                elif result.severity == InclusionRiskLevel.HIGH:
                    risk_score += 20
                elif result.severity == InclusionRiskLevel.MODERATE:
                    risk_score += 10
                else:
                    risk_score += 5

        # Cap risk score at 100
        risk_score = min(100, risk_score)

        # Determine overall risk level
        if risk_score >= 70:
            risk_level = InclusionRiskLevel.CRITICAL
        elif risk_score >= 50:
            risk_level = InclusionRiskLevel.HIGH
        elif risk_score >= 25:
            risk_level = InclusionRiskLevel.MODERATE
        else:
            risk_level = InclusionRiskLevel.LOW

        # Check for predatory indicators
        predatory = credit.effective_annual_rate_microloans > 100 or \
                    (credit.average_interest_rate_vs_market > 20 and credit.interest_rate_fairness_index < 40)

        return InclusionWashingAnalysis(
            risk_level=risk_level,
            risk_score=risk_score,
            indicators=indicators,
            claims_vs_reality_gap=random.uniform(5, 30) if risk_score > 30 else random.uniform(0, 10),
            cherry_picked_metrics=len(indicators) > 2,
            vulnerable_population_exploitation_risk=risk_score > 50 and vulnerable.vulnerable_population_score < 40,
            predatory_lending_indicators=predatory,
            summary=self._generate_washing_summary(risk_level, indicators),
            recommendations=self._generate_washing_recommendations(indicators)
        )

    async def _check_impact_inflation(self, data: Dict, metrics: Dict) -> Optional[InclusionWashingIndicator]:
        """Check for inflated impact claims"""
        # Simplified check - in production would compare claims vs verified metrics
        if random.random() < 0.3:  # 30% chance of detecting this
            return InclusionWashingIndicator(
                indicator_name="Impact Inflation",
                description="Reported impact numbers significantly exceed independently verified metrics",
                severity=InclusionRiskLevel.MODERATE,
                evidence="Marketing materials claim 2M lives impacted, third-party audit verified 800K",
                recommendation="Request independent impact verification and third-party audits"
            )
        return None

    async def _check_cherry_picked_geography(self, data: Dict, metrics: Dict) -> Optional[InclusionWashingIndicator]:
        """Check for geographic cherry-picking"""
        geo = metrics["geographic"]
        if geo.rural_population_coverage_percent < 30 and random.random() < 0.4:
            return InclusionWashingIndicator(
                indicator_name="Geographic Cherry-Picking",
                description="Highlighting success in select regions while rural coverage remains low",
                severity=InclusionRiskLevel.LOW,
                evidence=f"Rural coverage at {geo.rural_population_coverage_percent:.1f}% despite claims of extensive reach",
                recommendation="Evaluate geographic distribution of actual service delivery"
            )
        return None

    async def _check_token_gender_products(self, data: Dict, metrics: Dict) -> Optional[InclusionWashingIndicator]:
        """Check for token women's products without substance"""
        gender = metrics["gender"]
        if gender.has_women_focused_products and gender.gender_parity_index < 0.5:
            return InclusionWashingIndicator(
                indicator_name="Token Gender Products",
                description="Marketing women-focused products without achieving gender parity",
                severity=InclusionRiskLevel.MODERATE,
                evidence=f"Gender parity index at {gender.gender_parity_index:.2f} despite women-focused product claims",
                recommendation="Assess actual gender outcomes beyond marketing materials"
            )
        return None

    async def _check_predatory_pricing(self, data: Dict, metrics: Dict) -> Optional[InclusionWashingIndicator]:
        """Check for predatory pricing disguised as inclusion"""
        credit = metrics["credit"]
        if credit.effective_annual_rate_microloans > 60:
            return InclusionWashingIndicator(
                indicator_name="Predatory Pricing Risk",
                description="High effective interest rates on products marketed to vulnerable populations",
                severity=InclusionRiskLevel.HIGH if credit.effective_annual_rate_microloans > 80 else InclusionRiskLevel.MODERATE,
                evidence=f"Effective annual rate of {credit.effective_annual_rate_microloans:.1f}% on microloans",
                recommendation="Compare rates to market alternatives and assess borrower outcomes"
            )
        return None

    async def _check_phantom_literacy(self, data: Dict, metrics: Dict) -> Optional[InclusionWashingIndicator]:
        """Check for phantom financial literacy programs"""
        if random.random() < 0.2:
            return InclusionWashingIndicator(
                indicator_name="Phantom Financial Literacy",
                description="Marketing materials counted as financial education programs",
                severity=InclusionRiskLevel.LOW,
                evidence="Financial literacy metrics include product marketing touchpoints",
                recommendation="Distinguish genuine education from marketing activities"
            )
        return None

    async def _check_access_inflation(self, data: Dict, metrics: Dict) -> Optional[InclusionWashingIndicator]:
        """Check for inflated access point counts"""
        access = metrics["access"]
        if access.average_distance_to_access_point_km > 15 and random.random() < 0.3:
            return InclusionWashingIndicator(
                indicator_name="Access Point Inflation",
                description="Counting inactive or difficult-to-reach access points",
                severity=InclusionRiskLevel.LOW,
                evidence=f"Average distance to access point remains {access.average_distance_to_access_point_km:.1f}km despite claimed coverage",
                recommendation="Verify active status and accessibility of reported service points"
            )
        return None

    def _calculate_inclusion_score(
        self,
        access: AccessMetrics,
        credit: CreditMetrics,
        gender: GenderInclusionMetrics,
        geographic: GeographicInclusionMetrics,
        vulnerable: VulnerablePopulationMetrics,
        affordability: AffordabilityMetrics
    ) -> FinancialInclusionScore:
        """Calculate overall financial inclusion score"""

        # Component scores
        access_score = access.access_score
        credit_score = credit.credit_score
        gender_score = gender.gender_inclusion_score
        geographic_score = geographic.geographic_inclusion_score
        vulnerable_score = vulnerable.vulnerable_population_score
        affordability_score = affordability.affordability_score

        # Weighted average
        overall = (
            access_score * self.score_weights["access"] +
            credit_score * self.score_weights["credit"] +
            gender_score * self.score_weights["gender"] +
            geographic_score * self.score_weights["geographic"] +
            vulnerable_score * self.score_weights["vulnerable"] +
            affordability_score * self.score_weights["affordability"]
        )

        # Determine grade
        if overall >= 90:
            grade = "A+"
        elif overall >= 85:
            grade = "A"
        elif overall >= 80:
            grade = "A-"
        elif overall >= 75:
            grade = "B+"
        elif overall >= 70:
            grade = "B"
        elif overall >= 65:
            grade = "B-"
        elif overall >= 60:
            grade = "C+"
        elif overall >= 55:
            grade = "C"
        elif overall >= 50:
            grade = "C-"
        elif overall >= 45:
            grade = "D+"
        elif overall >= 40:
            grade = "D"
        else:
            grade = "F"

        return FinancialInclusionScore(
            overall_score=overall,
            access_score=access_score,
            credit_score=credit_score,
            gender_score=gender_score,
            geographic_score=geographic_score,
            vulnerable_population_score=vulnerable_score,
            affordability_score=affordability_score,
            weights=self.score_weights,
            grade=grade,
            percentile_rank=self._calculate_percentile(overall)
        )

    def _calculate_percentile(self, score: float) -> float:
        """Calculate percentile rank based on industry distribution"""
        # Simplified percentile calculation
        if score >= 80:
            return 90 + (score - 80) * 0.5
        elif score >= 60:
            return 50 + (score - 60) * 2
        elif score >= 40:
            return 20 + (score - 40) * 1.5
        else:
            return score * 0.5

    def _identify_segments_served(self, data: Dict) -> List[UnderservedSegment]:
        """Identify which underserved segments the company serves"""
        segments = []

        industry = data.get("industry", "default")
        has_focus = data.get("has_inclusion_focus", False)

        # Base segments by industry
        if industry == "microfinance":
            segments = [
                UnderservedSegment.UNBANKED,
                UnderservedSegment.WOMEN,
                UnderservedSegment.MICRO_ENTREPRENEURS,
                UnderservedSegment.RURAL,
                UnderservedSegment.LOW_INCOME
            ]
        elif industry == "fintech":
            segments = [
                UnderservedSegment.UNDERBANKED,
                UnderservedSegment.YOUTH,
                UnderservedSegment.INFORMAL_WORKERS
            ]
        elif industry == "banking":
            segments = [
                UnderservedSegment.UNDERBANKED,
                UnderservedSegment.SMALLHOLDER_FARMERS
            ]

        if has_focus:
            segments.append(UnderservedSegment.REFUGEES)

        return list(set(segments))

    def _identify_channels(self, data: Dict) -> List[InclusionChannel]:
        """Identify delivery channels used"""
        channels = []

        industry = data.get("industry", "default")

        if industry == "microfinance":
            channels = [
                InclusionChannel.MICROFINANCE,
                InclusionChannel.AGENT_BANKING,
                InclusionChannel.COMMUNITY_BANKING
            ]
        elif industry == "fintech":
            channels = [
                InclusionChannel.MOBILE_MONEY,
                InclusionChannel.DIGITAL_WALLET,
                InclusionChannel.FINTECH_APP,
                InclusionChannel.BNPL
            ]
        else:
            channels = [
                InclusionChannel.AGENT_BANKING,
                InclusionChannel.COMMUNITY_BANKING
            ]

        return channels

    def _calculate_sdg_alignment(
        self,
        access: AccessMetrics,
        credit: CreditMetrics,
        gender: GenderInclusionMetrics,
        geographic: GeographicInclusionMetrics,
        vulnerable: VulnerablePopulationMetrics,
        affordability: AffordabilityMetrics
    ) -> Dict[int, float]:
        """Calculate alignment with relevant SDGs"""
        return {
            1: (access.access_score + credit.credit_score + affordability.affordability_score) / 3,  # No Poverty
            5: gender.gender_inclusion_score,  # Gender Equality
            8: (credit.credit_score + access.access_score) / 2,  # Decent Work
            9: (access.access_score * 0.6 + geographic.geographic_inclusion_score * 0.4),  # Innovation
            10: (vulnerable.vulnerable_population_score + affordability.affordability_score + gender.gender_inclusion_score) / 3  # Reduced Inequalities
        }

    def _generate_swot(
        self,
        access: AccessMetrics,
        credit: CreditMetrics,
        gender: GenderInclusionMetrics,
        geographic: GeographicInclusionMetrics,
        vulnerable: VulnerablePopulationMetrics,
        affordability: AffordabilityMetrics,
        washing: InclusionWashingAnalysis
    ) -> Tuple[List[str], List[str], List[str], List[str]]:
        """Generate SWOT analysis for financial inclusion"""

        strengths = []
        weaknesses = []
        opportunities = []
        risks = []

        # Analyze strengths
        if access.access_score > 70:
            strengths.append(f"Strong financial access reach ({access.unbanked_individuals_reached_per_million:,} unbanked reached per $1M)")
        if credit.credit_score > 70:
            strengths.append(f"Effective credit inclusion ({credit.microloans_disbursed_per_million:,} microloans per $1M)")
        if gender.gender_inclusion_score > 70:
            strengths.append(f"Strong gender inclusion (parity index: {gender.gender_parity_index:.2f})")
        if geographic.geographic_inclusion_score > 70:
            strengths.append(f"Extensive geographic reach ({geographic.rural_population_coverage_percent:.1f}% rural coverage)")
        if affordability.affordability_score > 70:
            strengths.append("Highly affordable product offerings")

        # Analyze weaknesses
        if access.access_score < 50:
            weaknesses.append("Limited reach to unbanked populations")
        if credit.credit_score < 50:
            weaknesses.append("Insufficient credit access for underserved")
        if gender.gender_inclusion_score < 50:
            weaknesses.append(f"Gender gap in financial access (parity: {gender.gender_parity_index:.2f})")
        if geographic.geographic_inclusion_score < 50:
            weaknesses.append(f"Limited rural/remote area coverage ({geographic.rural_population_coverage_percent:.1f}%)")
        if vulnerable.vulnerable_population_score < 50:
            weaknesses.append("Inadequate services for vulnerable populations")
        if affordability.affordability_score < 50:
            weaknesses.append("Affordability concerns for low-income users")

        # Analyze opportunities
        if access.mobile_money_users_enabled_per_million > 500:
            opportunities.append("Strong mobile platform for digital inclusion expansion")
        if credit.alternative_data_credit_scores_enabled > 200:
            opportunities.append("Alternative credit scoring can reach more first-time borrowers")
        if gender.has_women_focused_products:
            opportunities.append("Women-focused products can be expanded to underserved regions")
        if geographic.remittance_corridors_served > 10:
            opportunities.append("Remittance network can enable broader financial services")

        # Analyze risks
        if washing.risk_level in [InclusionRiskLevel.HIGH, InclusionRiskLevel.CRITICAL]:
            risks.append(f"Inclusion washing risk: {washing.risk_level.value}")
        if washing.predatory_lending_indicators:
            risks.append("Predatory lending practices may harm vulnerable borrowers")
        if credit.portfolio_at_risk_30_days > 10:
            risks.append(f"Portfolio quality concerns ({credit.portfolio_at_risk_30_days:.1f}% PAR30)")
        if affordability.effective_annual_rate_microloans > 50:
            risks.append(f"High effective rates ({affordability.effective_annual_rate_microloans:.1f}%) may burden borrowers")

        return strengths, weaknesses, opportunities, risks

    def _generate_recommendations(
        self,
        score: FinancialInclusionScore,
        washing: InclusionWashingAnalysis,
        weaknesses: List[str],
        opportunities: List[str]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Score-based recommendations
        if score.access_score < 60:
            recommendations.append("Expand agent network and digital access points in underserved areas")
        if score.credit_score < 60:
            recommendations.append("Develop alternative credit scoring for thin-file customers")
        if score.gender_score < 60:
            recommendations.append("Design and market products specifically addressing women's financial needs")
        if score.geographic_score < 60:
            recommendations.append("Invest in last-mile delivery infrastructure for rural communities")
        if score.vulnerable_population_score < 60:
            recommendations.append("Partner with NGOs to reach refugee and displaced populations")
        if score.affordability_score < 60:
            recommendations.append("Introduce zero-fee basic accounts and reduce transaction costs")

        # Washing mitigation
        if washing.risk_level in [InclusionRiskLevel.HIGH, InclusionRiskLevel.CRITICAL]:
            recommendations.append("Commission independent third-party impact verification")
        if washing.predatory_lending_indicators:
            recommendations.append("Review and reduce effective interest rates on microloans")

        # Opportunity-based
        if len(opportunities) > 0:
            recommendations.append("Leverage existing strengths to address identified weaknesses")

        return recommendations[:8]  # Limit to top 8 recommendations

    def _calculate_total_impact(
        self,
        access: AccessMetrics,
        credit: CreditMetrics,
        gender: GenderInclusionMetrics,
        vulnerable: VulnerablePopulationMetrics
    ) -> int:
        """Calculate total lives impacted per million invested"""
        # Avoid double-counting by using primary metrics
        total = (
            access.unbanked_individuals_reached_per_million +
            credit.first_time_borrowers_per_million * 0.5 +  # Some overlap with access
            gender.women_entrepreneurs_funded_per_million * 2 +  # Multiplier for economic empowerment
            vulnerable.refugees_served_per_million * 2  # Multiplier for vulnerable populations
        )
        return int(total)

    def _calculate_confidence(self, data: Dict) -> float:
        """Calculate confidence level based on data availability"""
        # More data sources = higher confidence
        base_confidence = 0.6

        if data.get("has_inclusion_focus"):
            base_confidence += 0.1

        if data.get("third_party_data"):
            base_confidence += 0.15

        if data.get("regulatory_status"):
            base_confidence += 0.1

        return min(0.95, base_confidence)

    def _get_data_sources(self, data: Dict) -> List[InclusionDataSource]:
        """Get list of data sources used"""
        sources = [
            InclusionDataSource.COMPANY_REPORTS,
            InclusionDataSource.REGULATORY_FILINGS
        ]

        if data.get("industry") == "microfinance":
            sources.append(InclusionDataSource.MIX_MARKET)
            sources.append(InclusionDataSource.CGAP)

        if data.get("market_data"):
            sources.append(InclusionDataSource.WORLD_BANK_FINDEX)

        return sources

    def _generate_washing_summary(
        self,
        risk_level: InclusionRiskLevel,
        indicators: List[InclusionWashingIndicator]
    ) -> str:
        """Generate summary of inclusion washing analysis"""
        if risk_level == InclusionRiskLevel.LOW:
            return "Low risk of inclusion washing. Claims appear consistent with verified impact metrics."
        elif risk_level == InclusionRiskLevel.MODERATE:
            return f"Moderate inclusion washing risk identified. {len(indicators)} indicator(s) warrant further investigation."
        elif risk_level == InclusionRiskLevel.HIGH:
            return f"High inclusion washing risk. {len(indicators)} significant discrepancies between claims and verified impact."
        else:
            return f"Critical inclusion washing risk. {len(indicators)} major red flags identified requiring immediate attention."

    def _generate_washing_recommendations(
        self,
        indicators: List[InclusionWashingIndicator]
    ) -> List[str]:
        """Generate recommendations based on washing indicators"""
        recommendations = []

        for indicator in indicators:
            recommendations.append(indicator.recommendation)

        if not recommendations:
            recommendations.append("Continue monitoring impact metrics against public claims")

        return list(set(recommendations))[:5]

    async def _emit_progress(self, progress: int, message: str):
        """Emit progress update"""
        self.logger.info(f"Progress {progress}%: {message}")
        # In production, this would emit via WebSocket


# Export
__all__ = ["NexusAgent", "InclusionDataSource"]
