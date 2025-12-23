# GAIA Agent Framework

Core agent framework for the Global AI-powered Impact Assessment (GAIA) system.

## Overview

The GAIA agent framework provides a modular, extensible system for analyzing environmental, social, and governance (ESG) impacts across multiple dimensions. Each specialized agent focuses on a specific domain while sharing a common base architecture.

## Architecture

### Base Agent (`base_agent.py`)

The foundation for all agents, providing:

- **Async Execution**: Non-blocking analysis with timeout protection
- **Evidence Collection**: Structured data gathering with confidence scoring
- **Error Handling**: Automatic retry logic with exponential backoff
- **Adversarial Debate**: Agents can challenge each other's findings
- **Performance Tracking**: Built-in metrics for monitoring agent performance

#### Key Classes

- `BaseAgent`: Abstract base class for all agents
- `AgentReport`: Comprehensive analysis results
- `Finding`: Individual discovery with severity and confidence
- `Evidence`: Single piece of evidence with type and source
- `ConfidenceLevel`: Enum for confidence classifications

### Core Specialized Agents

#### 1. Sentinel Agent (`sentinel_agent.py`)

**Environmental and Satellite Monitoring**

Capabilities:
- Satellite imagery analysis (simulated)
- Deforestation detection using NDVI changes
- Air and water pollution monitoring
- Facility expansion detection
- Biodiversity impact assessment
- Environmental risk scoring

Data Sources (Simulated):
- Sentinel-2
- Landsat-8
- MODIS
- Planet Labs
- Copernicus

#### 2. Veritas Agent (`veritas_agent.py`)

**Supply Chain Verification and Transparency**

Capabilities:
- Multi-tier supply chain mapping
- Blockchain record verification (simulated)
- Supplier certification validation
- Shipping manifest analysis
- Conflict minerals detection
- Labor rights risk assessment
- Cross-referencing with sanctions lists

Verification Types:
- ISO certifications (9001, 14001, SA8000)
- Fair Trade, B Corp, FSC
- Blockchain transaction records
- Customs and trade documents

#### 3. Pulse Agent (`pulse_agent.py`)

**Social Sentiment and Media Monitoring**

Capabilities:
- Multi-language sentiment analysis
- News media monitoring
- Social media tracking
- Labor violation detection
- Protest and activism monitoring
- Consumer sentiment analysis
- Reputation risk scoring

Media Sources:
- News outlets (Reuters, Bloomberg, AP, etc.)
- Social media platforms (Twitter, Facebook, LinkedIn)
- Consumer review platforms
- Labor rights organizations

## Usage

### Basic Agent Usage

```python
import asyncio
from agents import SentinelAgent, VeritasAgent, PulseAgent

async def analyze_company(company_name: str):
    # Initialize agents
    sentinel = SentinelAgent(timeout_seconds=60)
    veritas = VeritasAgent(timeout_seconds=60)
    pulse = PulseAgent(timeout_seconds=60)

    # Prepare context
    context = {
        "coordinates": (40.7128, -74.0060),  # NYC
        "industry": "manufacturing",
        "timeframe_days": 180,
    }

    # Run agents in parallel
    results = await asyncio.gather(
        sentinel.execute_with_timeout(company_name, context),
        veritas.execute_with_timeout(company_name, context),
        pulse.execute_with_timeout(company_name, context),
    )

    sentinel_report, veritas_report, pulse_report = results

    # Process results
    print(f"Environmental Risk: {sentinel_report.overall_risk_score:.2f}/100")
    print(f"Supply Chain Risk: {veritas_report.overall_risk_score:.2f}/100")
    print(f"Social/Reputation Risk: {pulse_report.overall_risk_score:.2f}/100")

    return results

# Run analysis
asyncio.run(analyze_company("Example Corp"))
```

### Factory Pattern

```python
from agents import get_agent, get_all_agents

# Create individual agent
sentinel = get_agent("sentinel", timeout_seconds=120)

# Create all agents at once
agents = get_all_agents(timeout_seconds=90)

# Run specific agent
report = await agents["veritas"].analyze("Company XYZ")
```

### Adversarial Debate

```python
from base_agent import Finding, Evidence, EvidenceType

# Agent 1 makes a finding
sentinel = SentinelAgent()
finding = Finding(
    agent_name="Sentinel",
    finding_type="pollution",
    severity="HIGH",
    title="Pollution detected",
    confidence_score=0.82,
)

# Agent 2 challenges with counter-evidence
veritas = VeritasAgent()
counter_evidence = [
    Evidence(
        type=EvidenceType.CERTIFICATION,
        source="ISO 14001",
        description="Current environmental certification",
        confidence=0.91,
    ),
]

# Perform challenge
result = await veritas.challenge_finding(finding, counter_evidence)

print(f"Original confidence: {result['original_confidence']}")
print(f"Adjusted confidence: {result['adjusted_confidence']}")
```

### Data Collection

```python
# Collect raw evidence
sentinel = SentinelAgent()
evidence_list = await sentinel.collect_data(
    target_entity="Company ABC",
    context={"coordinates": (lat, lon), "time_range_days": 365}
)

# Calculate confidence
confidence = sentinel.calculate_confidence(evidence_list)
print(f"Data confidence: {confidence:.2%}")
```

## Evidence Types

The framework supports multiple evidence types:

- `SATELLITE_IMAGE`: Satellite imagery and remote sensing data
- `SENSOR_DATA`: Environmental sensor readings
- `BLOCKCHAIN_RECORD`: Blockchain verification records
- `CERTIFICATION`: Compliance certifications
- `SHIPPING_MANIFEST`: Trade and shipping documents
- `NEWS_ARTICLE`: News media articles
- `SOCIAL_MEDIA`: Social media posts and engagement
- `PUBLIC_RECORD`: Government and public databases

## Confidence Scoring

All findings include confidence scores (0.0 to 1.0) based on:

- Evidence quality and quantity
- Source reliability
- Data recency
- Cross-verification

Confidence levels:
- `VERY_HIGH`: 0.90 - 1.00
- `HIGH`: 0.75 - 0.89
- `MEDIUM`: 0.50 - 0.74
- `LOW`: 0.30 - 0.49
- `VERY_LOW`: 0.00 - 0.29

## Risk Scoring

Overall risk scores (0-100):
- **0-20**: CRITICAL - Avoid
- **20-40**: HIGH - Caution required
- **40-60**: MODERATE - Monitor closely
- **60-80**: LOW - Acceptable
- **80-100**: MINIMAL - Recommended

Risk scores are calculated based on:
- Finding severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Confidence in findings
- Number and type of violations
- Weighted importance of different factors

## Testing

Run the comprehensive test suite:

```bash
cd backend/agents
python test_new_agents.py
```

Test suite includes:
1. Individual agent testing
2. Parallel execution
3. Adversarial debate scenarios
4. Data collection validation

## Extension Guide

### Creating a New Agent

```python
from base_agent import BaseAgent, AgentReport, Finding, Evidence

class MyCustomAgent(BaseAgent):
    def __init__(self, name="CustomAgent", **kwargs):
        super().__init__(
            name=name,
            agent_type="custom_analysis",
            **kwargs
        )

    async def analyze(self, target_entity: str, context=None) -> AgentReport:
        report = AgentReport(
            agent_name=self.name,
            agent_type=self.agent_type,
            target_entity=target_entity,
        )

        # Collect evidence
        evidence = await self.collect_data(target_entity, context)

        # Create findings
        finding = Finding(
            agent_name=self.name,
            finding_type="custom",
            title="My Finding",
            description="Analysis results...",
        )

        # Add evidence to finding
        for ev in evidence:
            finding.add_evidence(ev)

        report.add_finding(finding)
        return report

    async def collect_data(self, target_entity: str, context=None) -> list:
        # Implement data collection
        return []

    def calculate_confidence(self, evidence: list, context=None) -> float:
        # Implement confidence calculation
        return 0.8
```

### Register New Agent

Add to `__init__.py`:

```python
from .my_custom_agent import MyCustomAgent

AGENT_REGISTRY["custom"] = MyCustomAgent
```

## Performance Considerations

### Timeout Management

- Default timeout: 60 seconds per agent
- Configurable per agent instance
- Automatic timeout handling with partial results

### Retry Logic

- Automatic retry on transient failures
- Exponential backoff (2s, 4s, 8s)
- Maximum 3 retry attempts
- Specific to network/connection errors

### Parallel Execution

- Agents run independently and can be parallelized
- Use `asyncio.gather()` for concurrent execution
- Typical 3-agent analysis: ~30-45 seconds

### Performance Metrics

Each agent tracks:
- Total executions
- Success/failure rate
- Average execution time
- Error patterns

Access metrics:

```python
metrics = agent.get_performance_metrics()
print(f"Success rate: {metrics['success_rate']:.1%}")
```

## Data Sources

### Current Implementation

The current implementation uses **simulated data** for demonstration purposes. All satellite imagery, supply chain records, and social media data are generated algorithmically.

### Production Integration

For production use, integrate real data sources:

1. **Sentinel Agent**:
   - NASA Earthdata API
   - ESA Copernicus API
   - Planet Labs API
   - Environmental sensor networks

2. **Veritas Agent**:
   - Blockchain networks (Ethereum, Hyperledger)
   - Customs databases
   - Certification registries (ISO, Fair Trade)
   - Supplier databases

3. **Pulse Agent**:
   - News APIs (NewsAPI, GDELT)
   - Social media APIs (Twitter, Reddit)
   - Review platforms (Trustpilot, Glassdoor)
   - Labor rights databases

## Dependencies

Core dependencies (from `requirements.txt`):
- `asyncio`: Async execution
- `tenacity`: Retry logic
- `structlog`: Structured logging
- `numpy`: Numerical operations
- `pydantic`: Data validation

Optional for production:
- `rasterio`: Satellite image processing
- `geopandas`: Geospatial analysis
- `transformers`: NLP for sentiment analysis
- `web3`: Blockchain integration

## License

Part of the GAIA project - Global AI-powered Impact Assessment system.

## Support

For questions or issues:
1. Check the test suite for examples
2. Review agent-specific documentation
3. Examine the base agent implementation
4. See `example_usage.py` for more patterns
