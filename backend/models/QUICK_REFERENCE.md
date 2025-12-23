# GAIA Models - Quick Reference Card

## Import Statement
```python
from models import *
```

## Core Models by Category

### Company (company.py)
| Model | Purpose | Key Fields |
|-------|---------|------------|
| `CompanyProfile` | Complete company info | company_id, name, industry, stock_info |
| `StockInformation` | Stock/ticker data | ticker, exchange, market_cap, current_price |
| `InvestmentQuery` | User query | ticker, investment_amount_usd, esg_priority |

### Assessment (assessment.py)
| Model | Purpose | Key Fields |
|-------|---------|------------|
| `AssessmentResult` | Complete assessment | assessment_id, esg_scores, greenwashing_risk |
| `ESGScores` | ESG breakdown | overall_score, environmental, social, governance |
| `ESGComponentScore` | Component detail | category, score, factors, strengths, weaknesses |
| `GreenwashingRiskScore` | Greenwashing detection | overall_risk_score, risk_factors, red_flags |
| `SustainabilityRating` | Overall rating | overall_rating, rating_score, strengths, weaknesses |
| `InvestmentRecommendationResult` | Investment advice | recommendation, rationale, esg_alignment_score |

### Agents (agent_models.py)
| Model | Purpose | Key Fields |
|-------|---------|------------|
| `AgentFinding` | Agent discovery | finding_id, agent_type, title, confidence_score |
| `AgentChallenge` | Adversarial challenge | challenge_id, challenge_type, specific_concerns |
| `AgentResponse` | Challenge response | response_id, acknowledgments, rebuttals |
| `DebateRound` | Debate round | findings, challenges, responses, consensus_reached |
| `ConsensusResult` | Final consensus | consensus_score, validated_findings, consensus_narrative |

### Evidence (evidence.py)
| Model | Purpose | Key Fields |
|-------|---------|------------|
| `EvidenceItem` | Evidence piece | evidence_id, title, source, confidence_score |
| `EvidenceSource` | Source info | source_name, source_type, credibility_score |
| `BlockchainRecord` | Blockchain verification | blockchain_hash, transaction_id, verification_url |
| `EvidenceTrail` | Complete evidence | evidence_items, blockchain_records, overall_confidence |
| `ProvenanceRecord` | Data lineage | origin_description, transformations, verification_chain |

### SDG (sdg.py)
| Model | Purpose | Key Fields |
|-------|---------|------------|
| `SDGContribution` | SDG contribution | sdg_goal, contribution_score, impact_type |
| `SDGAlignment` | Overall SDG alignment | overall_alignment_score, sdg_contributions, primary_sdgs |
| `SDGImpactMetric` | Quantified impact | metric_name, value, unit, verified |
| `SDGReport` | Complete SDG report | sdg_alignment, total_impact_score, major_achievements |

## Common Enums

### Industry & Market
```python
IndustryClassification: TECHNOLOGY, FINANCE, HEALTHCARE, ENERGY, etc.
MarketCapSize: MEGA_CAP, LARGE_CAP, MID_CAP, SMALL_CAP, etc.
StockExchange: NYSE, NASDAQ, LSE, TSE, etc.
```

### Ratings & Levels
```python
RatingLevel: LEADER, ADVANCED, AVERAGE, LAGGARD, CRITICAL
InvestmentRecommendation: STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL, AVOID
RiskLevel: MINIMAL, LOW, MODERATE, HIGH, CRITICAL
ConfidenceLevel: VERY_HIGH, HIGH, MEDIUM, LOW, VERY_LOW
```

### Agents
```python
AgentType: ENVIRONMENTAL_ANALYST, SOCIAL_ANALYST, GOVERNANCE_ANALYST,
          SDG_SPECIALIST, GREENWASHING_DETECTOR, FINANCIAL_ANALYST,
          DATA_VALIDATOR, SATELLITE_ANALYST, ADVERSARIAL_CRITIC
FindingType: STRENGTH, WEAKNESS, RISK, OPPORTUNITY, CONCERN, ACHIEVEMENT
ChallengeType: DATA_QUALITY, METHODOLOGY, LOGIC, EVIDENCE, BIAS
```

### Evidence
```python
EvidenceType: DOCUMENT, REPORT, SATELLITE_DATA, SUSTAINABILITY_REPORT,
             FINANCIAL_STATEMENT, THIRD_PARTY_AUDIT, etc.
SourceType: PRIMARY, SECONDARY, TERTIARY, REMOTE_SENSING, EXPERT_OPINION
VerificationStatus: VERIFIED, PARTIALLY_VERIFIED, UNVERIFIED, DISPUTED, REJECTED
DataQuality: EXCELLENT, GOOD, FAIR, POOR, UNRELIABLE
```

### SDG
```python
SDGGoal: 1-17 (UN Sustainable Development Goals)
ImpactType: POSITIVE, NEGATIVE, NEUTRAL, MIXED
ImpactMagnitude: TRANSFORMATIVE, SIGNIFICANT, MODERATE, LIMITED, MINIMAL
ContributionType: DIRECT, INDIRECT, ENABLING, CATALYTIC
```

## Score Ranges

All scores use 0-100 scale:
- **90-100**: Excellent/Leader
- **80-89**: Very Good/Advanced
- **70-79**: Good
- **60-69**: Above Average
- **50-59**: Average
- **40-49**: Below Average
- **30-39**: Poor/Laggard
- **20-29**: Very Poor
- **0-19**: Critical

## Common Patterns

### Create Company Profile
```python
company = CompanyProfile(
    company_id="TSLA-US",
    name="Tesla, Inc.",
    industry=IndustryClassification.TECHNOLOGY,
    stock_info=StockInformation(
        ticker="TSLA",
        exchange=StockExchange.NASDAQ
    )
)
```

### Create ESG Assessment
```python
assessment = AssessmentResult(
    assessment_id="TSLA-20251223-001",
    company_id="TSLA-US",
    company_name="Tesla, Inc.",
    esg_scores=ESGScores(
        overall_score=82.3,
        environmental=env_score,
        social=soc_score,
        governance=gov_score,
        rating_level=RatingLevel.ADVANCED
    ),
    greenwashing_risk=GreenwashingRiskScore(
        overall_risk_score=25.5,
        risk_level=RiskLevel.LOW
    )
)
```

### Create Agent Finding
```python
finding = AgentFinding(
    finding_id="ENV-001-TSLA",
    agent_type=AgentType.ENVIRONMENTAL_ANALYST,
    finding_type=FindingType.STRENGTH,
    title="Strong Carbon Reduction",
    description="35% reduction vs baseline",
    confidence_score=88.5,
    confidence_level=ConfidenceLevel.HIGH
)
```

### Add Evidence
```python
evidence = EvidenceItem(
    evidence_id="EVD-001-TSLA",
    evidence_type=EvidenceType.SUSTAINABILITY_REPORT,
    title="2023 Carbon Data",
    source=EvidenceSource(
        source_id="SRC-001",
        source_name="Tesla Impact Report 2023",
        source_type=SourceType.PRIMARY
    ),
    confidence_score=85.0,
    verification_status=VerificationStatus.VERIFIED
)
```

### Assess SDG Contribution
```python
sdg_contrib = SDGContribution(
    sdg_goal=7,  # Clean Energy
    goal_name="Affordable and Clean Energy",
    contribution_score=88.5,
    impact_type=ImpactType.POSITIVE,
    impact_magnitude=ImpactMagnitude.SIGNIFICANT,
    contribution_type=ContributionType.DIRECT
)
```

## Serialization

### To JSON
```python
# Pydantic v2 method
json_str = assessment.model_dump_json(indent=2)

# To dict
data_dict = assessment.model_dump()
```

### From JSON/Dict
```python
# From dict
assessment = AssessmentResult(**data_dict)

# From JSON string
import json
assessment = AssessmentResult(**json.loads(json_str))
```

## Validation

### Automatic Validation
```python
from pydantic import ValidationError

try:
    # This will fail - score out of range
    esg = ESGScores(overall_score=150)
except ValidationError as e:
    print(e.errors())
```

### Field Validators
All models include validators for:
- Score ranges (0-100)
- SDG goals (1-17)
- URL formatting
- Date/time validation
- Enum type safety

## Required Fields Quick Reference

### Minimal CompanyProfile
```python
CompanyProfile(
    company_id="UNIQUE-ID",
    name="Company Name",
    industry=IndustryClassification.TECHNOLOGY
)
```

### Minimal AssessmentResult
```python
AssessmentResult(
    assessment_id="UNIQUE-ID",
    company_id="COMP-ID",
    company_name="Company Name",
    esg_scores=esg_scores,
    greenwashing_risk=greenwashing_risk,
    sustainability_rating=sustainability_rating,
    investment_recommendation=investment_recommendation
)
```

### Minimal AgentFinding
```python
AgentFinding(
    finding_id="UNIQUE-ID",
    agent_type=AgentType.ENVIRONMENTAL_ANALYST,
    finding_type=FindingType.STRENGTH,
    title="Finding Title",
    description="Finding description",
    confidence_score=85.0,
    confidence_level=ConfidenceLevel.HIGH,
    impact_score=75.0,
    relevance_score=80.0
)
```

## Tips

1. Always provide `confidence_score` for transparency
2. Use enums instead of strings for type safety
3. Include `created_at` timestamps (auto-generated if not provided)
4. Link evidence with `evidence_ids` fields
5. Use `custom_fields` dict for extensibility
6. Leverage `model_dump()` for API responses
7. Use `model_validate()` for external data validation

## Common Field Names

- `*_id`: Unique identifiers (required, string)
- `*_score`: Numerical scores (0-100 range)
- `*_at`: Timestamps (datetime objects)
- `*_count`: Counts (non-negative integers)
- `*_url`: URLs (automatically formatted)
- `*_percentage`: Percentages (0-100 range)

## Documentation

See `README.md` for comprehensive documentation and examples.
