# GAIA Data Models

Comprehensive Pydantic v2 data models for the Global AI-powered Impact Assessment System.

## Overview

This package contains all data models used throughout the GAIA system for ESG assessment, SDG alignment analysis, multi-agent collaboration, and evidence verification.

## Module Structure

### 1. `company.py` - Company and Investment Models

**Purpose**: Models for company profiles, stock information, and investment queries.

**Key Models**:
- `CompanyProfile`: Comprehensive company information including industry classification, geographic presence, and historical ESG data
- `StockInformation`: Stock ticker, exchange, market cap, and financial metrics
- `GeographicPresence`: Regional operations and revenue distribution
- `HistoricalESGDataPoint`: Time-series ESG performance data
- `InvestmentQuery`: User investment analysis request parameters

**Enums**:
- `IndustryClassification`: 16 industry categories
- `MarketCapSize`: Market capitalization classifications (mega-cap to nano-cap)
- `StockExchange`: Major global stock exchanges
- `GeographicRegion`: 7 major geographic regions

**Example Usage**:
```python
from models import CompanyProfile, StockInformation, IndustryClassification

company = CompanyProfile(
    company_id="TSLA-US",
    name="Tesla, Inc.",
    industry=IndustryClassification.TECHNOLOGY,
    stock_info=StockInformation(
        ticker="TSLA",
        exchange="NASDAQ",
        current_price=242.84,
        market_cap=770000000000
    )
)
```

### 2. `assessment.py` - ESG Assessment and Rating Models

**Purpose**: Models for ESG scoring, greenwashing detection, and investment recommendations.

**Key Models**:
- `ESGScores`: Comprehensive ESG scoring with Environmental, Social, and Governance components
- `ESGComponentScore`: Detailed breakdown of individual ESG components
- `GreenwashingRiskScore`: AI-powered greenwashing detection with risk factors
- `SustainabilityRating`: Overall sustainability rating and qualitative assessment
- `InvestmentRecommendationResult`: Investment guidance with rationale
- `AssessmentResult`: Complete assessment package

**Enums**:
- `RatingLevel`: leader, advanced, average, laggard, critical
- `InvestmentRecommendation`: strong_buy, buy, hold, sell, strong_sell, avoid
- `RiskLevel`: minimal, low, moderate, high, critical

**Example Usage**:
```python
from models import ESGScores, ESGComponentScore, RatingLevel

esg_scores = ESGScores(
    overall_score=82.3,
    environmental=ESGComponentScore(
        category="Environmental",
        score=78.5,
        weight=0.33,
        weighted_score=25.9
    ),
    rating_level=RatingLevel.ADVANCED
)
```

### 3. `agent_models.py` - Multi-Agent Communication Models

**Purpose**: Models for adversarial debate, agent findings, and consensus building.

**Key Models**:
- `AgentFinding`: Individual agent discovery or insight
- `AgentChallenge`: Adversarial challenge to a finding
- `AgentResponse`: Response to a challenge
- `DebateRound`: Complete round of adversarial debate
- `ConsensusResult`: Final consensus after all debate rounds

**Enums**:
- `AgentType`: 10 specialized agent types (environmental_analyst, greenwashing_detector, etc.)
- `FindingType`: strength, weakness, risk, opportunity, concern, etc.
- `ChallengeType`: data_quality, methodology, logic, evidence, bias, etc.
- `ConfidenceLevel`: very_high, high, medium, low, very_low

**Example Usage**:
```python
from models import AgentFinding, AgentType, FindingType, ConfidenceLevel

finding = AgentFinding(
    finding_id="ENV-001-TSLA",
    agent_type=AgentType.ENVIRONMENTAL_ANALYST,
    finding_type=FindingType.STRENGTH,
    title="Strong Carbon Reduction Performance",
    description="Company achieved 35% carbon reduction vs 2020 baseline",
    confidence_score=88.5,
    confidence_level=ConfidenceLevel.HIGH
)
```

### 4. `evidence.py` - Evidence Trail and Verification Models

**Purpose**: Models for evidence collection, verification, and blockchain tracking.

**Key Models**:
- `EvidenceItem`: Individual piece of evidence with source and verification
- `EvidenceSource`: Source information with credibility scoring
- `BlockchainRecord`: Blockchain verification record (simulated or real)
- `EvidenceTrail`: Complete evidence trail for an assessment
- `ProvenanceRecord`: Detailed data lineage and provenance

**Enums**:
- `EvidenceType`: 15 types including documents, satellite data, reports, etc.
- `SourceType`: primary, secondary, tertiary, remote_sensing, etc.
- `VerificationStatus`: verified, partially_verified, unverified, disputed, rejected
- `DataQuality`: excellent, good, fair, poor, unreliable

**Example Usage**:
```python
from models import EvidenceItem, EvidenceSource, EvidenceType, VerificationStatus

evidence = EvidenceItem(
    evidence_id="EVD-001-TSLA",
    evidence_type=EvidenceType.SUSTAINABILITY_REPORT,
    title="2023 Carbon Emissions Data",
    description="Reported 35% reduction in carbon emissions",
    source=EvidenceSource(
        source_id="SRC-001",
        source_name="Tesla 2023 Impact Report",
        source_type="primary",
        credibility_score=88.5
    ),
    confidence_score=85.0,
    verification_status=VerificationStatus.VERIFIED
)
```

### 5. `sdg.py` - SDG Impact Models

**Purpose**: Models for UN Sustainable Development Goals alignment and impact assessment.

**Key Models**:
- `SDGContribution`: Contribution to a specific SDG goal
- `SDGTarget`: Contribution to specific SDG targets (e.g., 7.2, 13.1)
- `SDGImpactMetric`: Quantified impact metrics with units
- `SDGAlignment`: Overall SDG alignment across all 17 goals
- `SDGReport`: Comprehensive SDG impact report

**Enums**:
- `SDGGoal`: 17 UN SDG goals (1-17)
- `ImpactType`: positive, negative, neutral, mixed
- `ImpactMagnitude`: transformative, significant, moderate, limited, minimal
- `ContributionType`: direct, indirect, enabling, catalytic

**Example Usage**:
```python
from models import SDGContribution, SDGGoal, ImpactType, ImpactMagnitude

sdg_contribution = SDGContribution(
    sdg_goal=7,  # Affordable and Clean Energy
    goal_name="Affordable and Clean Energy",
    contribution_score=88.5,
    impact_type=ImpactType.POSITIVE,
    impact_magnitude=ImpactMagnitude.SIGNIFICANT,
    alignment_rationale="Core business in renewable energy and EVs"
)
```

### 6. `__init__.py` - Package Exports

Centralizes all model exports for easy importing:

```python
from models import (
    CompanyProfile,
    ESGScores,
    AgentFinding,
    EvidenceItem,
    SDGContribution,
    AssessmentResult
)
```

## Features

### Pydantic v2 Features Used

1. **Field Validation**: Extensive use of validators for data integrity
2. **ConfigDict**: Modern Pydantic v2 configuration with examples
3. **Type Safety**: Comprehensive type hints for all fields
4. **Serialization**: Built-in JSON serialization support
5. **Documentation**: Detailed field descriptions and examples

### Validation Features

- **Score Validation**: All scores validated to 0-100 range
- **SDG Validation**: SDG goals validated to 1-17 range
- **URL Validation**: Automatic URL formatting
- **Date Validation**: Datetime validation with defaults
- **Enum Validation**: Type-safe enumerations

### Data Quality Features

- **Confidence Scores**: Every assessment includes confidence metrics
- **Data Quality Ratings**: Explicit data quality tracking
- **Verification Status**: Multi-level verification tracking
- **Provenance Tracking**: Complete data lineage

### Extensibility

- **Custom Fields**: `custom_fields` dict in most models
- **Metadata**: Comprehensive metadata in all models
- **Tags and Keywords**: Flexible categorization
- **Additional Sources**: Support for multiple data sources

## Model Relationships

```
CompanyProfile
    └── StockInformation
    └── GeographicPresence[]
    └── HistoricalESGDataPoint[]

AssessmentResult
    ├── CompanyProfile (reference)
    ├── ESGScores
    │   ├── ESGComponentScore (Environmental)
    │   ├── ESGComponentScore (Social)
    │   └── ESGComponentScore (Governance)
    ├── GreenwashingRiskScore
    ├── SustainabilityRating
    ├── InvestmentRecommendationResult
    └── SDGAlignment
        └── SDGContribution[] (one per relevant SDG)
            └── SDGTarget[]
            └── SDGImpactMetric[]

ConsensusResult
    ├── DebateRound[]
    │   ├── AgentFinding[]
    │   ├── AgentChallenge[]
    │   └── AgentResponse[]
    └── AgentFinding[] (validated findings)

EvidenceTrail
    ├── EvidenceItem[]
    │   ├── EvidenceSource
    │   └── ProvenanceRecord
    └── BlockchainRecord[]
```

## Common Patterns

### Creating an Assessment

```python
from models import (
    CompanyProfile,
    ESGScores,
    AssessmentResult,
    IndustryClassification
)

# 1. Create company profile
company = CompanyProfile(
    company_id="TSLA-US",
    name="Tesla, Inc.",
    industry=IndustryClassification.TECHNOLOGY
)

# 2. Create ESG scores
esg_scores = ESGScores(
    overall_score=82.3,
    environmental=env_score,
    social=social_score,
    governance=gov_score,
    rating_level=RatingLevel.ADVANCED
)

# 3. Create full assessment
assessment = AssessmentResult(
    assessment_id="TSLA-US-20251223-001",
    company_id=company.company_id,
    company_name=company.name,
    esg_scores=esg_scores,
    greenwashing_risk=greenwashing_score,
    sustainability_rating=rating,
    investment_recommendation=recommendation
)
```

### Agent Debate Flow

```python
from models import (
    AgentFinding,
    AgentChallenge,
    AgentResponse,
    DebateRound,
    ConsensusResult
)

# 1. Agent makes finding
finding = AgentFinding(
    finding_id="ENV-001",
    agent_type=AgentType.ENVIRONMENTAL_ANALYST,
    title="Strong emissions reduction",
    confidence_score=85.0
)

# 2. Adversarial agent challenges
challenge = AgentChallenge(
    challenge_id="CHAL-001",
    finding_id=finding.finding_id,
    challenger_agent_type=AgentType.ADVERSARIAL_CRITIC,
    challenge_type=ChallengeType.EVIDENCE,
    title="Question data completeness"
)

# 3. Original agent responds
response = AgentResponse(
    response_id="RESP-001",
    challenge_id=challenge.challenge_id,
    response_type="clarification",
    description="Additional evidence provided"
)

# 4. Create debate round
round = DebateRound(
    round_id="ROUND-001",
    round_number=1,
    findings=[finding],
    challenges=[challenge],
    responses=[response]
)

# 5. Build consensus
consensus = ConsensusResult(
    consensus_id="CONSENSUS-001",
    total_rounds=3,
    debate_rounds=[round],
    consensus_achieved=True,
    consensus_score=85.5
)
```

## Validation Examples

### Automatic Score Clamping

```python
# Scores are automatically validated
esg_score = ESGScores(
    overall_score=150.0  # Will raise ValidationError
)

# Correct usage
esg_score = ESGScores(
    overall_score=85.5  # Valid, 0-100 range
)
```

### SDG Goal Validation

```python
# Invalid SDG goal
contribution = SDGContribution(
    sdg_goal=18,  # Will raise ValidationError (must be 1-17)
    contribution_score=80.0
)

# Valid usage
contribution = SDGContribution(
    sdg_goal=7,  # Valid SDG goal
    contribution_score=80.0
)
```

## Best Practices

1. **Always provide confidence scores**: Include confidence metrics for transparency
2. **Use enums for categories**: Leverage enums for type safety
3. **Include evidence**: Link evidence items to support findings
4. **Track provenance**: Use provenance records for data lineage
5. **Validate with examples**: Use the examples in ConfigDict for testing
6. **Document custom fields**: Add descriptions for custom field usage

## Dependencies

- `pydantic >= 2.0`: Core validation framework
- `pydantic_settings`: For configuration models (used in config.py)
- `typing`: Type hints (standard library)
- `datetime`: Timestamp handling (standard library)
- `enum`: Enumerations (standard library)

## Testing

```python
# Serialize to JSON
assessment_json = assessment.model_dump_json(indent=2)

# Deserialize from dict
assessment_dict = assessment.model_dump()
new_assessment = AssessmentResult(**assessment_dict)

# Validate external data
try:
    company = CompanyProfile(**external_data)
except ValidationError as e:
    print(f"Validation errors: {e.errors()}")
```

## Version

**Current Version**: 1.0.0

## License

Part of the GAIA (Global AI-powered Impact Assessment) system.
