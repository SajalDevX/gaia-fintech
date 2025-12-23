"""
GAIA Sample Company Database
Simulated company data for demonstration purposes
"""

from typing import Dict, List, Any
import random
from datetime import datetime, timedelta


SAMPLE_COMPANIES = {
    "AAPL": {
        "name": "Apple Inc.",
        "ticker": "AAPL",
        "industry": "technology",
        "sector": "Consumer Electronics",
        "country": "United States",
        "market_cap": 3000000000000,
        "employees": 164000,
        "founded": 1976,
        "description": "Consumer electronics, software, and services company",
        "reported_esg": {
            "environmental": 82,
            "social": 78,
            "governance": 85
        },
        "actual_esg": {
            "environmental": 75,
            "social": 72,
            "governance": 83
        },
        "issues": [
            {"type": "Supply Chain Labor", "severity": "medium", "description": "Some supplier audits reveal overtime violations"},
            {"type": "E-Waste", "severity": "low", "description": "Recycling programs could be expanded"}
        ],
        "sdg_focus": [9, 8, 12, 13],
        "facilities": [
            {"location": "Cupertino, CA", "type": "headquarters", "lat": 37.3349, "lon": -122.0090},
            {"location": "Austin, TX", "type": "manufacturing", "lat": 30.2672, "lon": -97.7431},
            {"location": "Shenzhen, China", "type": "supplier", "lat": 22.5431, "lon": 114.0579}
        ]
    },
    "XOM": {
        "name": "Exxon Mobil Corporation",
        "ticker": "XOM",
        "industry": "energy",
        "sector": "Oil & Gas",
        "country": "United States",
        "market_cap": 450000000000,
        "employees": 62000,
        "founded": 1999,
        "description": "Multinational oil and gas corporation",
        "reported_esg": {
            "environmental": 65,
            "social": 70,
            "governance": 75
        },
        "actual_esg": {
            "environmental": 35,
            "social": 55,
            "governance": 70
        },
        "issues": [
            {"type": "Carbon Emissions", "severity": "critical", "description": "Significantly underreported Scope 3 emissions"},
            {"type": "Climate Lobbying", "severity": "high", "description": "Active lobbying against climate regulations"},
            {"type": "Oil Spills", "severity": "high", "description": "History of environmental incidents"}
        ],
        "sdg_focus": [7, 8, 13],
        "facilities": [
            {"location": "Houston, TX", "type": "headquarters", "lat": 29.7604, "lon": -95.3698},
            {"location": "Baytown, TX", "type": "refinery", "lat": 29.7355, "lon": -95.0352},
            {"location": "Nigeria", "type": "extraction", "lat": 4.8156, "lon": 7.0498}
        ],
        "greenwashing_indicators": {
            "emission_gap": 45,
            "lobbying_contradiction": True,
            "marketing_claims_verified": 0.3
        }
    },
    "MSFT": {
        "name": "Microsoft Corporation",
        "ticker": "MSFT",
        "industry": "technology",
        "sector": "Software",
        "country": "United States",
        "market_cap": 2800000000000,
        "employees": 221000,
        "founded": 1975,
        "description": "Technology company developing software, services, and devices",
        "reported_esg": {
            "environmental": 88,
            "social": 82,
            "governance": 90
        },
        "actual_esg": {
            "environmental": 85,
            "social": 80,
            "governance": 88
        },
        "issues": [
            {"type": "Data Privacy", "severity": "low", "description": "Minor privacy concerns in some regions"}
        ],
        "sdg_focus": [4, 8, 9, 13],
        "facilities": [
            {"location": "Redmond, WA", "type": "headquarters", "lat": 47.6740, "lon": -122.1215},
            {"location": "Dublin, Ireland", "type": "data_center", "lat": 53.3498, "lon": -6.2603}
        ]
    },
    "NESN": {
        "name": "Nestlé S.A.",
        "ticker": "NESN",
        "industry": "food",
        "sector": "Food & Beverage",
        "country": "Switzerland",
        "market_cap": 320000000000,
        "employees": 275000,
        "founded": 1866,
        "description": "Multinational food and drink processing conglomerate",
        "reported_esg": {
            "environmental": 75,
            "social": 80,
            "governance": 82
        },
        "actual_esg": {
            "environmental": 55,
            "social": 60,
            "governance": 78
        },
        "issues": [
            {"type": "Water Rights", "severity": "critical", "description": "Controversial water extraction in drought regions"},
            {"type": "Child Labor", "severity": "high", "description": "Cocoa supply chain child labor issues"},
            {"type": "Plastic Pollution", "severity": "high", "description": "Major single-use plastic producer"},
            {"type": "Deforestation", "severity": "medium", "description": "Palm oil supply chain linked to deforestation"}
        ],
        "sdg_focus": [2, 6, 12, 15],
        "facilities": [
            {"location": "Vevey, Switzerland", "type": "headquarters", "lat": 46.4603, "lon": 6.8426},
            {"location": "Ivory Coast", "type": "supplier", "lat": 5.3600, "lon": -4.0083},
            {"location": "São Paulo, Brazil", "type": "manufacturing", "lat": -23.5505, "lon": -46.6333}
        ],
        "greenwashing_indicators": {
            "emission_gap": 25,
            "supply_chain_violations": True,
            "marketing_claims_verified": 0.5
        }
    },
    "TSLA": {
        "name": "Tesla, Inc.",
        "ticker": "TSLA",
        "industry": "automotive",
        "sector": "Electric Vehicles",
        "country": "United States",
        "market_cap": 800000000000,
        "employees": 140000,
        "founded": 2003,
        "description": "Electric vehicle and clean energy company",
        "reported_esg": {
            "environmental": 92,
            "social": 75,
            "governance": 70
        },
        "actual_esg": {
            "environmental": 78,
            "social": 55,
            "governance": 60
        },
        "issues": [
            {"type": "Labor Relations", "severity": "high", "description": "Worker safety concerns and union opposition"},
            {"type": "Governance", "severity": "medium", "description": "Board independence questions"},
            {"type": "Cobalt Sourcing", "severity": "medium", "description": "Battery supply chain ethics concerns"}
        ],
        "sdg_focus": [7, 9, 11, 13],
        "facilities": [
            {"location": "Austin, TX", "type": "headquarters", "lat": 30.2232, "lon": -97.6200},
            {"location": "Fremont, CA", "type": "manufacturing", "lat": 37.4946, "lon": -121.9446},
            {"location": "Shanghai, China", "type": "manufacturing", "lat": 31.0926, "lon": 121.8053},
            {"location": "Berlin, Germany", "type": "manufacturing", "lat": 52.3980, "lon": 13.8220}
        ]
    },
    "JNJ": {
        "name": "Johnson & Johnson",
        "ticker": "JNJ",
        "industry": "healthcare",
        "sector": "Pharmaceuticals",
        "country": "United States",
        "market_cap": 380000000000,
        "employees": 152000,
        "founded": 1886,
        "description": "Healthcare products and pharmaceuticals company",
        "reported_esg": {
            "environmental": 78,
            "social": 85,
            "governance": 88
        },
        "actual_esg": {
            "environmental": 72,
            "social": 65,
            "governance": 75
        },
        "issues": [
            {"type": "Product Safety", "severity": "critical", "description": "Ongoing talc litigation concerns"},
            {"type": "Drug Pricing", "severity": "high", "description": "Pricing practices under scrutiny"},
            {"type": "Opioid Settlement", "severity": "high", "description": "Historical opioid distribution issues"}
        ],
        "sdg_focus": [3, 5, 10, 12],
        "facilities": [
            {"location": "New Brunswick, NJ", "type": "headquarters", "lat": 40.4862, "lon": -74.4518},
            {"location": "Belgium", "type": "manufacturing", "lat": 50.8503, "lon": 4.3517}
        ]
    },
    "PAYX": {
        "name": "Paychex, Inc.",
        "ticker": "PAYX",
        "industry": "finance",
        "sector": "Business Services",
        "country": "United States",
        "market_cap": 45000000000,
        "employees": 16000,
        "founded": 1971,
        "description": "HR and payroll services for small to medium businesses",
        "reported_esg": {
            "environmental": 70,
            "social": 82,
            "governance": 85
        },
        "actual_esg": {
            "environmental": 68,
            "social": 80,
            "governance": 84
        },
        "issues": [],
        "sdg_focus": [8, 10, 16],
        "facilities": [
            {"location": "Rochester, NY", "type": "headquarters", "lat": 43.1566, "lon": -77.6088}
        ]
    },
    "BP": {
        "name": "BP p.l.c.",
        "ticker": "BP",
        "industry": "energy",
        "sector": "Oil & Gas",
        "country": "United Kingdom",
        "market_cap": 100000000000,
        "employees": 67000,
        "founded": 1909,
        "description": "British multinational oil and gas company",
        "reported_esg": {
            "environmental": 70,
            "social": 72,
            "governance": 78
        },
        "actual_esg": {
            "environmental": 40,
            "social": 58,
            "governance": 72
        },
        "issues": [
            {"type": "Deepwater Horizon", "severity": "critical", "description": "Historical major environmental disaster"},
            {"type": "Carbon Emissions", "severity": "critical", "description": "Major fossil fuel producer"},
            {"type": "Greenwashing", "severity": "high", "description": "Renewable claims vs actual fossil fuel investment ratio"}
        ],
        "sdg_focus": [7, 13],
        "facilities": [
            {"location": "London, UK", "type": "headquarters", "lat": 51.5074, "lon": -0.1278},
            {"location": "Gulf of Mexico", "type": "offshore", "lat": 28.7367, "lon": -88.3700}
        ],
        "greenwashing_indicators": {
            "emission_gap": 55,
            "renewable_ratio": 0.08,
            "marketing_claims_verified": 0.25
        }
    },
    "NOVO": {
        "name": "Novo Nordisk A/S",
        "ticker": "NOVO",
        "industry": "healthcare",
        "sector": "Pharmaceuticals",
        "country": "Denmark",
        "market_cap": 500000000000,
        "employees": 55000,
        "founded": 1923,
        "description": "Global healthcare company specializing in diabetes care",
        "reported_esg": {
            "environmental": 88,
            "social": 90,
            "governance": 92
        },
        "actual_esg": {
            "environmental": 86,
            "social": 88,
            "governance": 90
        },
        "issues": [
            {"type": "Drug Pricing", "severity": "low", "description": "Some pricing concerns in US market"}
        ],
        "sdg_focus": [3, 10, 12, 17],
        "facilities": [
            {"location": "Bagsværd, Denmark", "type": "headquarters", "lat": 55.7558, "lon": 12.4545}
        ]
    },
    "VALE": {
        "name": "Vale S.A.",
        "ticker": "VALE",
        "industry": "mining",
        "sector": "Metals & Mining",
        "country": "Brazil",
        "market_cap": 65000000000,
        "employees": 125000,
        "founded": 1942,
        "description": "Brazilian multinational mining company",
        "reported_esg": {
            "environmental": 60,
            "social": 65,
            "governance": 70
        },
        "actual_esg": {
            "environmental": 25,
            "social": 35,
            "governance": 55
        },
        "issues": [
            {"type": "Dam Collapse", "severity": "critical", "description": "Brumadinho dam disaster - 270 deaths"},
            {"type": "Indigenous Rights", "severity": "critical", "description": "Land disputes with indigenous communities"},
            {"type": "Deforestation", "severity": "high", "description": "Amazon deforestation linked to operations"},
            {"type": "Water Pollution", "severity": "high", "description": "River contamination from mining waste"}
        ],
        "sdg_focus": [8, 9, 15],
        "facilities": [
            {"location": "Rio de Janeiro, Brazil", "type": "headquarters", "lat": -22.9068, "lon": -43.1729},
            {"location": "Minas Gerais, Brazil", "type": "mining", "lat": -19.8157, "lon": -43.9542}
        ],
        "greenwashing_indicators": {
            "emission_gap": 60,
            "safety_violations": True,
            "marketing_claims_verified": 0.2
        }
    }
}


def get_company(ticker: str) -> Dict[str, Any] | None:
    """Get company data by ticker symbol."""
    return SAMPLE_COMPANIES.get(ticker.upper())


def get_all_companies() -> List[Dict[str, Any]]:
    """Get all sample companies."""
    return list(SAMPLE_COMPANIES.values())


def search_companies(query: str) -> List[Dict[str, Any]]:
    """Search companies by name or ticker."""
    query = query.lower()
    results = []
    for ticker, company in SAMPLE_COMPANIES.items():
        if (query in ticker.lower() or
            query in company["name"].lower() or
            query in company.get("industry", "").lower()):
            results.append(company)
    return results


def generate_news_data(ticker: str, days: int = 30) -> List[Dict[str, Any]]:
    """Generate simulated news data for a company."""
    company = get_company(ticker)
    if not company:
        return []

    news_templates = {
        "positive": [
            f"{company['name']} announces new sustainability initiative",
            f"{company['name']} exceeds carbon reduction targets",
            f"{company['name']} recognized for workplace diversity",
            f"{company['name']} partners with environmental NGO",
            f"{company['name']} launches green bond program"
        ],
        "negative": [
            f"{company['name']} faces regulatory scrutiny over {company['issues'][0]['type'] if company['issues'] else 'practices'}",
            f"Whistleblower allegations against {company['name']}",
            f"{company['name']} criticized by environmental groups",
            f"Worker safety concerns at {company['name']} facility",
            f"Supply chain issues reported at {company['name']}"
        ],
        "neutral": [
            f"{company['name']} releases annual sustainability report",
            f"{company['name']} appoints new Chief Sustainability Officer",
            f"{company['name']} participates in industry ESG summit",
            f"Analysts review {company['name']} ESG performance"
        ]
    }

    news_items = []
    for i in range(min(20, days)):
        sentiment = random.choices(
            ["positive", "negative", "neutral"],
            weights=[0.3, 0.3, 0.4] if company.get("issues") else [0.5, 0.1, 0.4]
        )[0]

        headlines = news_templates.get(sentiment, news_templates["neutral"])
        headline = random.choice(headlines)

        news_items.append({
            "headline": headline,
            "source": random.choice(["Reuters", "Bloomberg", "WSJ", "Financial Times", "CNBC"]),
            "date": (datetime.now() - timedelta(days=random.randint(0, days))).isoformat(),
            "sentiment": sentiment,
            "relevance_score": random.uniform(0.6, 0.95)
        })

    return sorted(news_items, key=lambda x: x["date"], reverse=True)


def generate_social_sentiment(ticker: str) -> Dict[str, Any]:
    """Generate simulated social media sentiment data."""
    company = get_company(ticker)
    if not company:
        return {}

    # Base sentiment influenced by issues
    issue_severity = sum(
        {"critical": 30, "high": 20, "medium": 10, "low": 5}.get(i.get("severity", "low"), 5)
        for i in company.get("issues", [])
    )

    base_positive = max(20, 70 - issue_severity)
    base_negative = min(60, 15 + issue_severity)
    base_neutral = 100 - base_positive - base_negative

    return {
        "overall_sentiment": "positive" if base_positive > 50 else "negative" if base_negative > 40 else "mixed",
        "sentiment_score": round((base_positive - base_negative) / 100, 2),
        "breakdown": {
            "positive": base_positive + random.randint(-5, 5),
            "negative": base_negative + random.randint(-5, 5),
            "neutral": base_neutral + random.randint(-5, 5)
        },
        "trending_topics": [
            issue.get("type", "Sustainability") for issue in company.get("issues", [])[:3]
        ] or ["ESG Performance", "Innovation"],
        "mention_volume": random.randint(1000, 50000),
        "engagement_rate": round(random.uniform(0.02, 0.08), 3),
        "influencer_sentiment": random.choice(["positive", "mixed", "negative"]),
        "platforms_analyzed": ["Twitter/X", "LinkedIn", "Reddit", "News Comments"]
    }


def generate_satellite_data(ticker: str) -> Dict[str, Any]:
    """Generate simulated satellite monitoring data."""
    company = get_company(ticker)
    if not company:
        return {}

    facilities = company.get("facilities", [])
    has_env_issues = any(
        i.get("type") in ["Deforestation", "Pollution", "Oil Spills", "Water Pollution"]
        for i in company.get("issues", [])
    )

    facility_data = []
    for facility in facilities:
        anomaly_detected = has_env_issues and random.random() > 0.5
        facility_data.append({
            "location": facility["location"],
            "type": facility["type"],
            "coordinates": {"lat": facility["lat"], "lon": facility["lon"]},
            "vegetation_index": round(random.uniform(0.2, 0.8) if not anomaly_detected else random.uniform(0.1, 0.4), 2),
            "thermal_anomaly": anomaly_detected and random.random() > 0.7,
            "air_quality_index": random.randint(20, 80) if not anomaly_detected else random.randint(80, 150),
            "water_quality_nearby": random.choice(["good", "moderate"]) if not anomaly_detected else random.choice(["poor", "moderate"]),
            "land_use_change_detected": anomaly_detected and random.random() > 0.6,
            "last_updated": datetime.now().isoformat()
        })

    return {
        "facilities_monitored": len(facilities),
        "data_sources": ["Sentinel-2", "Landsat-8", "NASA MODIS"],
        "analysis_period": "Last 30 days",
        "facilities": facility_data,
        "alerts": [
            {
                "type": "Environmental Anomaly",
                "location": f["location"],
                "severity": random.choice(["low", "medium", "high"]),
                "description": "Unusual thermal signature detected"
            }
            for f in facility_data if f.get("thermal_anomaly")
        ]
    }


def generate_supply_chain_data(ticker: str) -> Dict[str, Any]:
    """Generate simulated supply chain verification data."""
    company = get_company(ticker)
    if not company:
        return {}

    has_supply_issues = any(
        "supply" in i.get("type", "").lower() or "labor" in i.get("type", "").lower()
        for i in company.get("issues", [])
    )

    tiers = {
        "tier1": random.randint(20, 100),
        "tier2": random.randint(100, 500),
        "tier3": random.randint(200, 1000)
    }

    verified_pct = random.uniform(0.6, 0.95) if not has_supply_issues else random.uniform(0.3, 0.7)

    return {
        "total_suppliers": sum(tiers.values()),
        "suppliers_by_tier": tiers,
        "verified_suppliers_pct": round(verified_pct * 100, 1),
        "certifications_checked": [
            "ISO 14001", "SA8000", "Fair Trade", "FSC", "BSCI"
        ],
        "high_risk_regions": [
            region for region in ["Southeast Asia", "West Africa", "South America"]
            if random.random() > 0.5
        ],
        "audit_coverage": round(random.uniform(0.4, 0.9) * 100, 1),
        "violations_found": random.randint(0, 10) if has_supply_issues else random.randint(0, 3),
        "remediation_rate": round(random.uniform(0.6, 0.95) * 100, 1),
        "blockchain_verified": random.randint(int(tiers["tier1"] * 0.3), tiers["tier1"])
    }


def generate_regulatory_data(ticker: str) -> Dict[str, Any]:
    """Generate simulated regulatory compliance data."""
    company = get_company(ticker)
    if not company:
        return {}

    has_regulatory_issues = any(
        i.get("severity") in ["critical", "high"]
        for i in company.get("issues", [])
    )

    return {
        "jurisdictions_monitored": random.randint(50, 190),
        "compliance_score": round(random.uniform(70, 95) if not has_regulatory_issues else random.uniform(45, 75), 1),
        "pending_regulations": [
            {"name": "EU CSRD", "impact": "high", "deadline": "2025"},
            {"name": "SEC Climate Disclosure", "impact": "high", "deadline": "2024"},
            {"name": "EU Taxonomy", "impact": "medium", "deadline": "2024"}
        ],
        "enforcement_actions": random.randint(0, 3) if not has_regulatory_issues else random.randint(2, 8),
        "fines_last_5_years": random.randint(0, 50000000) if not has_regulatory_issues else random.randint(10000000, 500000000),
        "lobbying_expenditure": random.randint(1000000, 50000000),
        "political_donations": random.randint(100000, 10000000),
        "regulatory_risk_score": round(random.uniform(20, 50) if not has_regulatory_issues else random.uniform(50, 85), 1)
    }


# ============================================================
# FINANCIAL INCLUSION SAMPLE COMPANIES
# ============================================================

INCLUSION_COMPANIES = {
    "GRMT": {
        "name": "Grameen Trust Microfinance",
        "ticker": "GRMT",
        "industry": "microfinance",
        "sector": "Financial Inclusion",
        "country": "Bangladesh",
        "market_cap": 2500000000,
        "employees": 25000,
        "founded": 1983,
        "description": "Pioneer in microfinance serving rural women and smallholder farmers",
        "reported_esg": {
            "environmental": 72,
            "social": 95,
            "governance": 88
        },
        "actual_esg": {
            "environmental": 70,
            "social": 93,
            "governance": 86
        },
        "issues": [],
        "sdg_focus": [1, 5, 8, 10],
        "facilities": [
            {"location": "Dhaka, Bangladesh", "type": "headquarters", "lat": 23.8103, "lon": 90.4125}
        ],
        "inclusion_data": {
            "has_inclusion_focus": True,
            "industry": "microfinance",
            "segments_served": ["unbanked", "women", "rural", "smallholder_farmers", "micro_entrepreneurs"],
            "channels": ["microfinance", "agent_banking", "community_banking"],
            "metrics": {
                "unbanked_reached_per_million": 2500,
                "women_borrowers_percent": 97,
                "rural_coverage_percent": 85,
                "average_loan_size_usd": 250,
                "first_time_borrowers_percent": 45,
                "repayment_rate": 98.5,
                "gender_parity_index": 1.05,
                "effective_interest_rate": 22
            }
        }
    },
    "MPSA": {
        "name": "M-Pesa Global Services",
        "ticker": "MPSA",
        "industry": "fintech",
        "sector": "Mobile Money",
        "country": "Kenya",
        "market_cap": 8000000000,
        "employees": 5000,
        "founded": 2007,
        "description": "Mobile money platform connecting unbanked populations across Africa",
        "reported_esg": {
            "environmental": 65,
            "social": 90,
            "governance": 82
        },
        "actual_esg": {
            "environmental": 63,
            "social": 88,
            "governance": 80
        },
        "issues": [
            {"type": "Agent Fraud", "severity": "low", "description": "Occasional agent fraud incidents"}
        ],
        "sdg_focus": [1, 8, 9, 10],
        "facilities": [
            {"location": "Nairobi, Kenya", "type": "headquarters", "lat": -1.2921, "lon": 36.8219}
        ],
        "inclusion_data": {
            "has_inclusion_focus": True,
            "industry": "fintech",
            "segments_served": ["unbanked", "underbanked", "informal_workers", "rural", "women"],
            "channels": ["mobile_money", "agent_banking", "digital_wallet"],
            "metrics": {
                "unbanked_reached_per_million": 3500,
                "mobile_money_users": 50000000,
                "agents_deployed": 400000,
                "transaction_volume_daily": 85000000,
                "rural_coverage_percent": 75,
                "average_transaction_usd": 25,
                "gender_parity_index": 0.85
            }
        }
    },
    "BRAC": {
        "name": "BRAC Financial Services",
        "ticker": "BRAC",
        "industry": "microfinance",
        "sector": "Development Finance",
        "country": "Bangladesh",
        "market_cap": 1800000000,
        "employees": 100000,
        "founded": 1972,
        "description": "World's largest NGO providing microfinance, education, and healthcare",
        "reported_esg": {
            "environmental": 75,
            "social": 98,
            "governance": 90
        },
        "actual_esg": {
            "environmental": 74,
            "social": 96,
            "governance": 88
        },
        "issues": [],
        "sdg_focus": [1, 2, 3, 4, 5, 8, 10],
        "facilities": [
            {"location": "Dhaka, Bangladesh", "type": "headquarters", "lat": 23.7937, "lon": 90.4066}
        ],
        "inclusion_data": {
            "has_inclusion_focus": True,
            "industry": "microfinance",
            "segments_served": ["unbanked", "women", "rural", "youth", "refugees", "smallholder_farmers"],
            "channels": ["microfinance", "community_banking", "cooperative"],
            "metrics": {
                "unbanked_reached_per_million": 2800,
                "women_borrowers_percent": 87,
                "rural_coverage_percent": 92,
                "youth_programs_participants": 2500000,
                "refugees_served": 250000,
                "countries_operating": 11,
                "gender_parity_index": 0.95
            }
        }
    },
    "NUBN": {
        "name": "Nubank Digital",
        "ticker": "NUBN",
        "industry": "fintech",
        "sector": "Digital Banking",
        "country": "Brazil",
        "market_cap": 35000000000,
        "employees": 8000,
        "founded": 2013,
        "description": "Latin America's largest digital bank serving underbanked populations",
        "reported_esg": {
            "environmental": 70,
            "social": 85,
            "governance": 80
        },
        "actual_esg": {
            "environmental": 68,
            "social": 82,
            "governance": 78
        },
        "issues": [
            {"type": "Credit Risk", "severity": "low", "description": "Rapid growth increasing credit exposure"}
        ],
        "sdg_focus": [8, 9, 10],
        "facilities": [
            {"location": "São Paulo, Brazil", "type": "headquarters", "lat": -23.5505, "lon": -46.6333}
        ],
        "inclusion_data": {
            "has_inclusion_focus": True,
            "industry": "fintech",
            "segments_served": ["underbanked", "youth", "informal_workers", "micro_entrepreneurs"],
            "channels": ["fintech_app", "digital_wallet"],
            "metrics": {
                "customers_total": 80000000,
                "first_bank_account_percent": 35,
                "zero_fee_accounts": True,
                "credit_card_first_timers_percent": 40,
                "average_customer_age": 32,
                "gender_parity_index": 0.78
            }
        }
    },
    "EQTY": {
        "name": "Equity Group Holdings",
        "ticker": "EQTY",
        "industry": "banking",
        "sector": "Commercial Banking",
        "country": "Kenya",
        "market_cap": 4500000000,
        "employees": 35000,
        "founded": 1984,
        "description": "African bank focused on financial inclusion and serving MSMEs",
        "reported_esg": {
            "environmental": 70,
            "social": 88,
            "governance": 85
        },
        "actual_esg": {
            "environmental": 68,
            "social": 85,
            "governance": 82
        },
        "issues": [],
        "sdg_focus": [1, 5, 8, 10, 17],
        "facilities": [
            {"location": "Nairobi, Kenya", "type": "headquarters", "lat": -1.2864, "lon": 36.8172}
        ],
        "inclusion_data": {
            "has_inclusion_focus": True,
            "industry": "banking",
            "segments_served": ["unbanked", "underbanked", "women", "youth", "smallholder_farmers", "micro_entrepreneurs"],
            "channels": ["agent_banking", "mobile_money", "community_banking"],
            "metrics": {
                "customers_total": 17000000,
                "agents_deployed": 75000,
                "women_borrowers_percent": 48,
                "rural_branches_percent": 65,
                "sme_loans_percent": 45,
                "scholarship_beneficiaries": 26000,
                "gender_parity_index": 0.82
            }
        }
    },
    "GCSH": {
        "name": "GCash Financial Technologies",
        "ticker": "GCSH",
        "industry": "fintech",
        "sector": "Mobile Payments",
        "country": "Philippines",
        "market_cap": 5000000000,
        "employees": 3000,
        "founded": 2004,
        "description": "Philippines' leading mobile wallet for financial inclusion",
        "reported_esg": {
            "environmental": 62,
            "social": 88,
            "governance": 78
        },
        "actual_esg": {
            "environmental": 60,
            "social": 85,
            "governance": 75
        },
        "issues": [
            {"type": "Cybersecurity", "severity": "low", "description": "Phishing attempts targeting users"}
        ],
        "sdg_focus": [1, 8, 9, 10],
        "facilities": [
            {"location": "Taguig, Philippines", "type": "headquarters", "lat": 14.5176, "lon": 121.0509}
        ],
        "inclusion_data": {
            "has_inclusion_focus": True,
            "industry": "fintech",
            "segments_served": ["unbanked", "underbanked", "informal_workers", "youth", "rural"],
            "channels": ["mobile_money", "digital_wallet", "fintech_app"],
            "metrics": {
                "registered_users": 90000000,
                "monthly_active_users": 45000000,
                "remittance_corridors": 15,
                "merchants_onboarded": 4000000,
                "rural_penetration_percent": 55,
                "gender_parity_index": 0.88
            }
        }
    },
    "MKOP": {
        "name": "M-KOPA Solar",
        "ticker": "MKOP",
        "industry": "fintech",
        "sector": "Pay-As-You-Go",
        "country": "Kenya",
        "market_cap": 800000000,
        "employees": 2500,
        "founded": 2011,
        "description": "Pay-as-you-go financing for off-grid solar and smartphones",
        "reported_esg": {
            "environmental": 92,
            "social": 90,
            "governance": 82
        },
        "actual_esg": {
            "environmental": 90,
            "social": 88,
            "governance": 80
        },
        "issues": [],
        "sdg_focus": [1, 7, 8, 10, 13],
        "facilities": [
            {"location": "Nairobi, Kenya", "type": "headquarters", "lat": -1.2921, "lon": 36.8219}
        ],
        "inclusion_data": {
            "has_inclusion_focus": True,
            "industry": "fintech",
            "segments_served": ["unbanked", "rural", "low_income", "women"],
            "channels": ["paygo", "mobile_money", "agent_banking"],
            "metrics": {
                "customers_total": 3000000,
                "solar_homes_connected": 2500000,
                "smartphones_financed": 1500000,
                "co2_avoided_tons": 2500000,
                "rural_percent": 85,
                "women_customers_percent": 55,
                "repayment_rate": 94,
                "average_daily_payment_usd": 0.50
            }
        }
    },
    "PTYM": {
        "name": "Paytm Financial Services",
        "ticker": "PTYM",
        "industry": "fintech",
        "sector": "Digital Payments",
        "country": "India",
        "market_cap": 6000000000,
        "employees": 12000,
        "founded": 2010,
        "description": "India's leading digital payments and financial services platform",
        "reported_esg": {
            "environmental": 65,
            "social": 80,
            "governance": 72
        },
        "actual_esg": {
            "environmental": 62,
            "social": 75,
            "governance": 68
        },
        "issues": [
            {"type": "Regulatory Compliance", "severity": "medium", "description": "RBI compliance concerns"}
        ],
        "sdg_focus": [8, 9, 10],
        "facilities": [
            {"location": "Noida, India", "type": "headquarters", "lat": 28.5355, "lon": 77.3910}
        ],
        "inclusion_data": {
            "has_inclusion_focus": True,
            "industry": "fintech",
            "segments_served": ["underbanked", "informal_workers", "micro_entrepreneurs", "rural", "women"],
            "channels": ["mobile_money", "digital_wallet", "fintech_app", "bnpl"],
            "metrics": {
                "registered_users": 350000000,
                "merchants_onboarded": 30000000,
                "monthly_transactions": 1500000000,
                "rural_merchants_percent": 45,
                "first_digital_payment_percent": 30,
                "gender_parity_index": 0.65
            }
        }
    },
    "KIVA": {
        "name": "Kiva Microfunds",
        "ticker": "KIVA",
        "industry": "microfinance",
        "sector": "Crowdfunding",
        "country": "United States",
        "market_cap": 500000000,
        "employees": 150,
        "founded": 2005,
        "description": "Crowdfunded microloans connecting lenders with underserved entrepreneurs",
        "reported_esg": {
            "environmental": 68,
            "social": 98,
            "governance": 92
        },
        "actual_esg": {
            "environmental": 67,
            "social": 97,
            "governance": 91
        },
        "issues": [],
        "sdg_focus": [1, 5, 8, 10, 17],
        "facilities": [
            {"location": "San Francisco, CA", "type": "headquarters", "lat": 37.7749, "lon": -122.4194}
        ],
        "inclusion_data": {
            "has_inclusion_focus": True,
            "industry": "microfinance",
            "segments_served": ["unbanked", "women", "refugees", "micro_entrepreneurs", "smallholder_farmers"],
            "channels": ["microfinance", "cooperative"],
            "metrics": {
                "total_loans_funded_usd": 1900000000,
                "borrowers_served": 5000000,
                "lenders_participating": 2000000,
                "countries_reached": 77,
                "women_borrowers_percent": 80,
                "refugee_loans_funded": 250000,
                "repayment_rate": 96.3
            }
        }
    },
    "FDLT": {
        "name": "FinDev Lending Technologies",
        "ticker": "FDLT",
        "industry": "fintech",
        "sector": "Alternative Lending",
        "country": "United States",
        "market_cap": 1200000000,
        "employees": 800,
        "founded": 2015,
        "description": "AI-powered lending for underserved small businesses in emerging markets",
        "reported_esg": {
            "environmental": 60,
            "social": 82,
            "governance": 78
        },
        "actual_esg": {
            "environmental": 58,
            "social": 70,
            "governance": 72
        },
        "issues": [
            {"type": "Interest Rates", "severity": "medium", "description": "Higher rates for high-risk segments"},
            {"type": "AI Bias", "severity": "low", "description": "Potential algorithmic bias in credit scoring"}
        ],
        "sdg_focus": [8, 9, 10],
        "facilities": [
            {"location": "New York, NY", "type": "headquarters", "lat": 40.7128, "lon": -74.0060}
        ],
        "inclusion_data": {
            "has_inclusion_focus": True,
            "industry": "fintech",
            "segments_served": ["underbanked", "micro_entrepreneurs", "informal_workers"],
            "channels": ["fintech_app", "bnpl"],
            "metrics": {
                "loans_disbursed": 500000,
                "average_loan_size_usd": 5000,
                "first_time_borrowers_percent": 60,
                "approval_rate_underserved": 45,
                "effective_interest_rate": 35,
                "countries_operating": 12,
                "gender_parity_index": 0.55
            },
            "inclusion_washing_concerns": {
                "high_interest_rates": True,
                "claims_vs_reality_gap": 25
            }
        }
    }
}

# Add inclusion companies to main database
SAMPLE_COMPANIES.update(INCLUSION_COMPANIES)


def generate_inclusion_data(ticker: str) -> Dict[str, Any]:
    """Generate financial inclusion metrics for a company."""
    company = get_company(ticker)
    if not company:
        return {}

    # Check if company has explicit inclusion data
    if "inclusion_data" in company:
        base_data = company["inclusion_data"]
        metrics = base_data.get("metrics", {})

        # Calculate inclusion scores
        has_focus = base_data.get("has_inclusion_focus", False)
        industry = base_data.get("industry", "default")

        base_score = 75 if industry == "microfinance" else 60 if industry == "fintech" else 45

        return {
            "has_inclusion_focus": has_focus,
            "industry": industry,
            "segments_served": base_data.get("segments_served", []),
            "channels_utilized": base_data.get("channels", []),
            "scores": {
                "overall": base_score + random.uniform(-5, 10),
                "access": base_score + random.uniform(0, 15),
                "credit": base_score + random.uniform(-5, 10),
                "gender": metrics.get("gender_parity_index", 0.5) * 100,
                "geographic": metrics.get("rural_coverage_percent", 50) if "rural_coverage_percent" in metrics else base_score,
                "vulnerable": base_score - 10 + random.uniform(0, 20),
                "affordability": 100 - metrics.get("effective_interest_rate", 30) if "effective_interest_rate" in metrics else base_score
            },
            "metrics": metrics,
            "washing_risk": {
                "level": "low" if not base_data.get("inclusion_washing_concerns") else "moderate",
                "score": 20 if not base_data.get("inclusion_washing_concerns") else 45,
                "predatory_lending": metrics.get("effective_interest_rate", 0) > 50
            },
            "total_lives_impacted_per_million": metrics.get("unbanked_reached_per_million", 500) +
                                                 metrics.get("first_time_borrowers_percent", 20) * 10
        }

    # Generate inclusion data for companies without explicit data
    industry = company.get("industry", "default")
    is_financial = industry in ["finance", "banking", "insurance"]

    base_score = 35 if not is_financial else 45

    return {
        "has_inclusion_focus": False,
        "industry": industry,
        "segments_served": ["underbanked"] if is_financial else [],
        "channels_utilized": ["fintech_app"] if is_financial else [],
        "scores": {
            "overall": base_score + random.uniform(-10, 15),
            "access": base_score + random.uniform(-5, 10),
            "credit": base_score + random.uniform(-10, 10),
            "gender": 40 + random.uniform(-10, 20),
            "geographic": 30 + random.uniform(-5, 15),
            "vulnerable": 25 + random.uniform(-5, 15),
            "affordability": 45 + random.uniform(-10, 15)
        },
        "metrics": {
            "unbanked_reached_per_million": random.randint(50, 300),
            "gender_parity_index": 0.4 + random.uniform(0, 0.3)
        },
        "washing_risk": {
            "level": "moderate",
            "score": 35 + random.uniform(0, 20),
            "predatory_lending": False
        },
        "total_lives_impacted_per_million": random.randint(100, 500)
    }


def get_inclusion_focused_companies() -> List[Dict[str, Any]]:
    """Get all companies with strong financial inclusion focus."""
    return [
        company for company in SAMPLE_COMPANIES.values()
        if company.get("inclusion_data", {}).get("has_inclusion_focus", False)
    ]


def get_inclusion_benchmarks(industry: str) -> Dict[str, Any]:
    """Get financial inclusion benchmarks by industry."""
    benchmarks = {
        "microfinance": {
            "average_score": 78,
            "access_benchmark": 82,
            "gender_benchmark": 75,
            "geographic_benchmark": 80,
            "leaders": ["GRMT", "BRAC", "KIVA"]
        },
        "fintech": {
            "average_score": 62,
            "access_benchmark": 70,
            "gender_benchmark": 55,
            "geographic_benchmark": 50,
            "leaders": ["MPSA", "GCSH", "NUBN"]
        },
        "banking": {
            "average_score": 48,
            "access_benchmark": 55,
            "gender_benchmark": 42,
            "geographic_benchmark": 40,
            "leaders": ["EQTY"]
        },
        "default": {
            "average_score": 40,
            "access_benchmark": 45,
            "gender_benchmark": 38,
            "geographic_benchmark": 35,
            "leaders": []
        }
    }
    return benchmarks.get(industry.lower(), benchmarks["default"])
