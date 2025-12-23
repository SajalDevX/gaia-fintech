# GAIA Agents - Quick Start Guide

## Installation

No additional installation needed! All dependencies are already in `requirements.txt`.

```bash
cd /home/sajal/Desktop/Hackathons/gaia-project/backend
pip install -r requirements.txt
```

## 5-Minute Tutorial

### Step 1: Import the Agents

```python
import asyncio
from agents import SentinelAgent, VeritasAgent, PulseAgent
```

### Step 2: Create Agent Instances

```python
# Environmental monitoring
sentinel = SentinelAgent(timeout_seconds=60)

# Supply chain verification
veritas = VeritasAgent(timeout_seconds=60)

# Social sentiment monitoring
pulse = PulseAgent(timeout_seconds=60)
```

### Step 3: Run an Analysis

```python
async def analyze_company(company_name):
    # Analyze with Sentinel
    report = await sentinel.execute_with_timeout(
        company_name,
        context={"coordinates": (40.7128, -74.0060)}  # NYC
    )

    print(f"Company: {report.target_entity}")
    print(f"Risk Score: {report.overall_risk_score:.2f}/100")
    print(f"Findings: {len(report.findings)}")

    # Show findings
    for finding in report.findings:
        print(f"\n- [{finding.severity}] {finding.title}")
        print(f"  Confidence: {finding.confidence_score:.2%}")

# Run it
asyncio.run(analyze_company("Example Corp"))
```

### Step 4: Run All Agents in Parallel

```python
async def full_analysis(company_name):
    # Run all three agents simultaneously
    results = await asyncio.gather(
        sentinel.execute_with_timeout(company_name),
        veritas.execute_with_timeout(company_name),
        pulse.execute_with_timeout(company_name),
    )

    sentinel_report, veritas_report, pulse_report = results

    # Calculate overall risk
    avg_risk = (
        sentinel_report.overall_risk_score +
        veritas_report.overall_risk_score +
        pulse_report.overall_risk_score
    ) / 3

    print(f"\n=== Analysis Results for {company_name} ===")
    print(f"Environmental Risk: {sentinel_report.overall_risk_score:.2f}")
    print(f"Supply Chain Risk: {veritas_report.overall_risk_score:.2f}")
    print(f"Social Risk: {pulse_report.overall_risk_score:.2f}")
    print(f"\nOverall Risk: {avg_risk:.2f}/100")

    if avg_risk < 40:
        print("Recommendation: HIGH RISK - Caution Required")
    elif avg_risk < 60:
        print("Recommendation: MODERATE RISK - Monitor Closely")
    else:
        print("Recommendation: LOW RISK - Acceptable")

asyncio.run(full_analysis("Global Industries Inc"))
```

## Common Use Cases

### Use Case 1: Environmental Impact Assessment

```python
from agents import SentinelAgent

async def environmental_check(company, location):
    sentinel = SentinelAgent()

    report = await sentinel.execute_with_timeout(
        company,
        context={
            "coordinates": location,
            "time_range_days": 365,
        }
    )

    # Check for critical environmental issues
    critical = [f for f in report.findings if f.severity == "CRITICAL"]

    if critical:
        print(f"⚠️  CRITICAL: {len(critical)} environmental violations found!")
        for finding in critical:
            print(f"  - {finding.title}")
    else:
        print(f"✓ No critical environmental issues detected")

    return report

# Example
asyncio.run(environmental_check(
    "Amazon Logging Co",
    location=(-3.4653, -62.2159)  # Amazon region
))
```

### Use Case 2: Supply Chain Due Diligence

```python
from agents import VeritasAgent

async def supply_chain_audit(company, industry):
    veritas = VeritasAgent()

    report = await veritas.execute_with_timeout(
        company,
        context={
            "industry": industry,
            "products": ["electronics", "textiles"],
        }
    )

    # Check for supply chain red flags
    red_flags = [
        f for f in report.findings
        if f.finding_type in ["conflict_minerals", "labor_rights"]
        and f.severity in ["HIGH", "CRITICAL"]
    ]

    if red_flags:
        print(f"🚩 {len(red_flags)} supply chain red flags:")
        for flag in red_flags:
            print(f"  - {flag.title} (Confidence: {flag.confidence_score:.0%})")
    else:
        print("✓ Supply chain appears clean")

    return report

# Example
asyncio.run(supply_chain_audit(
    "Fast Fashion Global",
    industry="textile_manufacturing"
))
```

### Use Case 3: Reputation Risk Monitoring

```python
from agents import PulseAgent

async def reputation_check(company):
    pulse = PulseAgent()

    report = await pulse.execute_with_timeout(
        company,
        context={"timeframe_days": 90}
    )

    # Get reputation metrics
    reputation_finding = next(
        (f for f in report.findings if f.finding_type == "reputation_risk"),
        None
    )

    if reputation_finding:
        rep_score = reputation_finding.metadata.get("reputation_score", 50)
        print(f"Reputation Score: {rep_score:.0f}/100")

        if rep_score < 40:
            print("Status: 🔴 Critical reputation issues")
        elif rep_score < 60:
            print("Status: 🟡 Moderate reputation concerns")
        else:
            print("Status: 🟢 Good reputation")

    return report

# Example
asyncio.run(reputation_check("TechGiant Corp"))
```

### Use Case 4: Adversarial Validation

```python
from agents import SentinelAgent, VeritasAgent
from base_agent import Finding, Evidence, EvidenceType

async def validate_claim():
    sentinel = SentinelAgent()
    veritas = VeritasAgent()

    # Sentinel makes a finding
    finding = Finding(
        agent_name="Sentinel",
        finding_type="pollution",
        severity="HIGH",
        title="High pollution levels detected",
        description="AQI exceeds safe levels",
        confidence_score=0.82,
    )

    # Add evidence
    finding.add_evidence(Evidence(
        type=EvidenceType.SENSOR_DATA,
        source="EPA Monitor",
        description="AQI: 120",
        confidence=0.85,
    ))

    print(f"Original Finding:")
    print(f"  Severity: {finding.severity}")
    print(f"  Confidence: {finding.confidence_score:.2%}")

    # Veritas challenges with counter-evidence
    counter = [
        Evidence(
            type=EvidenceType.CERTIFICATION,
            source="ISO 14001",
            description="Current environmental certification",
            confidence=0.91,
        )
    ]

    result = await veritas.challenge_finding(finding, counter)

    print(f"\nAfter Challenge:")
    print(f"  Adjusted Confidence: {result['adjusted_confidence']:.2%}")
    print(f"  Reduction: {result['adjustment_factor']:.2%}")

asyncio.run(validate_claim())
```

## Testing Your Setup

Run the comprehensive test suite:

```bash
cd /home/sajal/Desktop/Hackathons/gaia-project/backend/agents
python test_new_agents.py
```

Expected output:
- Test results for all three agents
- Parallel execution demonstration
- Adversarial debate example
- Data collection validation
- JSON results file

## Understanding the Output

### Agent Report Structure

```python
{
    "agent_name": "Sentinel",
    "agent_type": "environmental_monitoring",
    "target_entity": "Example Corp",
    "overall_risk_score": 45.2,  # 0-100 (lower is riskier)
    "findings": [...],
    "execution_time_seconds": 1.23,
    "errors": []
}
```

### Finding Structure

```python
{
    "title": "Deforestation detected",
    "severity": "HIGH",  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    "confidence_score": 0.82,  # 0.0-1.0
    "evidence_trail": [...],
    "description": "Detailed description..."
}
```

### Risk Score Interpretation

- **0-20**: CRITICAL - Avoid investment
- **20-40**: HIGH - Significant concerns
- **40-60**: MODERATE - Monitor closely
- **60-80**: LOW - Acceptable with oversight
- **80-100**: MINIMAL - Low risk

### Confidence Levels

- **0.90-1.00**: VERY_HIGH - Highly reliable
- **0.75-0.89**: HIGH - Reliable
- **0.50-0.74**: MEDIUM - Moderately reliable
- **0.30-0.49**: LOW - Less reliable
- **0.00-0.29**: VERY_LOW - Least reliable

## Pro Tips

### 1. Always Use Context

Provide context for better analysis:

```python
context = {
    "coordinates": (lat, lon),      # For Sentinel
    "industry": "manufacturing",    # For Veritas
    "timeframe_days": 90,           # For Pulse
}
```

### 2. Filter by Confidence

Focus on high-confidence findings:

```python
high_confidence = [
    f for f in report.findings
    if f.confidence_score >= 0.75
]
```

### 3. Check Specific Risk Areas

```python
# Environmental
deforestation = [f for f in report.findings if f.finding_type == "deforestation"]

# Supply chain
labor_risks = [f for f in report.findings if f.finding_type == "labor_rights"]

# Social
protests = [f for f in report.findings if f.finding_type == "protests_activism"]
```

### 4. Use Factory Pattern

```python
from agents import get_agent, get_all_agents

# Single agent
sentinel = get_agent("sentinel", timeout_seconds=120)

# All agents
agents = get_all_agents(timeout_seconds=90)
for agent_type, agent in agents.items():
    report = await agent.analyze("Company XYZ")
```

### 5. Handle Timeouts Gracefully

```python
try:
    report = await agent.execute_with_timeout(company, context)
except asyncio.TimeoutError:
    print("Analysis timed out - try increasing timeout_seconds")
```

## Integration Examples

### With FastAPI

```python
from fastapi import FastAPI
from agents import get_all_agents

app = FastAPI()

@app.post("/analyze")
async def analyze(company: str):
    agents = get_all_agents(timeout_seconds=60)

    results = await asyncio.gather(
        agents["sentinel"].analyze(company),
        agents["veritas"].analyze(company),
        agents["pulse"].analyze(company),
    )

    return {
        "company": company,
        "sentinel": results[0].to_dict(),
        "veritas": results[1].to_dict(),
        "pulse": results[2].to_dict(),
    }
```

### With Celery (Async Tasks)

```python
from celery import Celery
from agents import SentinelAgent

app = Celery('gaia')

@app.task
def analyze_company_async(company_name):
    sentinel = SentinelAgent()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    report = loop.run_until_complete(
        sentinel.execute_with_timeout(company_name)
    )

    return report.to_dict()
```

### With Scheduled Jobs

```python
import schedule
import time
from agents import get_all_agents

async def daily_monitoring(companies):
    agents = get_all_agents()

    for company in companies:
        reports = {}
        for agent_type, agent in agents.items():
            reports[agent_type] = await agent.analyze(company)

        # Store or email reports
        save_to_database(company, reports)

def run_scheduled():
    companies = ["Company A", "Company B"]
    asyncio.run(daily_monitoring(companies))

schedule.every().day.at("09:00").do(run_scheduled)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Troubleshooting

### Import Error

```python
# If you get import errors, make sure you're in the right directory
import sys
sys.path.append('/home/sajal/Desktop/Hackathons/gaia-project/backend')
from agents import SentinelAgent
```

### Timeout Issues

```python
# Increase timeout for slow analyses
agent = SentinelAgent(timeout_seconds=120)
```

### Memory Issues

```python
# Process companies in batches
async def batch_analysis(companies, batch_size=10):
    for i in range(0, len(companies), batch_size):
        batch = companies[i:i+batch_size]
        # Process batch
        await asyncio.gather(*[analyze(c) for c in batch])
```

## Next Steps

1. **Read the full README.md** for detailed documentation
2. **Run test_new_agents.py** to see all features in action
3. **Check IMPLEMENTATION_SUMMARY.md** for technical details
4. **Integrate with your FastAPI backend**
5. **Add real data sources** for production use

## Support

For questions or issues:
1. Check the README.md
2. Review the test suite examples
3. Examine the base_agent.py implementation
4. See example_usage.py for more patterns

Happy analyzing!
