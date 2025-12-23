"""
GAIA Agents - Test Suite for New Agents
Demonstrates Sentinel, Veritas, and Pulse agents.
"""

import asyncio
import json
from datetime import datetime
from typing import List

from sentinel_agent import SentinelAgent
from veritas_agent import VeritasAgent
from pulse_agent import PulseAgent
from base_agent import AgentReport, Finding


async def test_sentinel_agent():
    """Test the Sentinel (Environmental Monitoring) Agent."""
    print("\n" + "="*80)
    print("SENTINEL AGENT - Environmental Monitoring Test")
    print("="*80 + "\n")

    # Initialize agent
    sentinel = SentinelAgent(timeout_seconds=30, enable_debug=True)

    # Test configuration
    company = "Amazon Rainforest Mining Corp"
    context = {
        "coordinates": (-3.4653, -62.2159),  # Amazon region
        "time_range_days": 365,
    }

    print(f"Target Company: {company}")
    print(f"Location: {context['coordinates']}")
    print(f"Time Range: {context['time_range_days']} days\n")

    # Execute analysis
    print("Executing environmental analysis...")
    report = await sentinel.execute_with_timeout(company, context)

    # Display results
    print_report_summary(report)

    # Show specific findings
    print("\nDetailed Findings:")
    for i, finding in enumerate(report.findings, 1):
        print(f"\n{i}. {finding.title} [{finding.severity}]")
        print(f"   Type: {finding.finding_type}")
        print(f"   Confidence: {finding.confidence_score:.2%} ({finding.get_confidence_level().value})")
        print(f"   Description: {finding.description}")
        print(f"   Evidence Count: {len(finding.evidence_trail)}")

        # Show first evidence piece
        if finding.evidence_trail:
            evidence = finding.evidence_trail[0]
            print(f"   Sample Evidence:")
            print(f"     - Source: {evidence.source}")
            print(f"     - Type: {evidence.type.value}")
            print(f"     - Description: {evidence.description}")

    # Performance metrics
    metrics = sentinel.get_performance_metrics()
    print(f"\n{'-'*80}")
    print(f"Performance Metrics:")
    print(f"  Success Rate: {metrics['success_rate']:.1%}")
    print(f"  Total Executions: {metrics['total_executions']}")

    return report


async def test_veritas_agent():
    """Test the Veritas (Supply Chain Verification) Agent."""
    print("\n" + "="*80)
    print("VERITAS AGENT - Supply Chain Verification Test")
    print("="*80 + "\n")

    # Initialize agent
    veritas = VeritasAgent(timeout_seconds=30, enable_debug=True)

    # Test configuration
    company = "Fast Fashion Global Ltd"
    context = {
        "industry": "textile_manufacturing",
        "products": ["clothing", "accessories"],
    }

    print(f"Target Company: {company}")
    print(f"Industry: {context['industry']}")
    print(f"Products: {', '.join(context['products'])}\n")

    # Execute analysis
    print("Executing supply chain verification...")
    report = await veritas.execute_with_timeout(company, context)

    # Display results
    print_report_summary(report)

    # Show specific findings
    print("\nDetailed Findings:")
    for i, finding in enumerate(report.findings, 1):
        print(f"\n{i}. {finding.title} [{finding.severity}]")
        print(f"   Type: {finding.finding_type}")
        print(f"   Confidence: {finding.confidence_score:.2%}")
        print(f"   Description: {finding.description}")

        # Show evidence summary
        if finding.evidence_trail:
            evidence_types = {}
            for evidence in finding.evidence_trail:
                evidence_types[evidence.type.value] = evidence_types.get(evidence.type.value, 0) + 1

            print(f"   Evidence Breakdown:")
            for etype, count in evidence_types.items():
                print(f"     - {etype}: {count} pieces")

    # Performance metrics
    metrics = veritas.get_performance_metrics()
    print(f"\n{'-'*80}")
    print(f"Performance Metrics:")
    print(f"  Success Rate: {metrics['success_rate']:.1%}")

    return report


async def test_pulse_agent():
    """Test the Pulse (Social Sentiment) Agent."""
    print("\n" + "="*80)
    print("PULSE AGENT - Social Sentiment Monitoring Test")
    print("="*80 + "\n")

    # Initialize agent
    pulse = PulseAgent(timeout_seconds=30, enable_debug=True)

    # Test configuration
    company = "TechGiant Social Media Inc"
    context = {
        "timeframe_days": 90,
        "languages": ["en", "es", "fr"],
    }

    print(f"Target Company: {company}")
    print(f"Timeframe: {context['timeframe_days']} days")
    print(f"Languages: {', '.join(context['languages'])}\n")

    # Execute analysis
    print("Executing social sentiment analysis...")
    report = await pulse.execute_with_timeout(company, context)

    # Display results
    print_report_summary(report)

    # Show specific findings
    print("\nDetailed Findings:")
    for i, finding in enumerate(report.findings, 1):
        print(f"\n{i}. {finding.title} [{finding.severity}]")
        print(f"   Type: {finding.finding_type}")
        print(f"   Confidence: {finding.confidence_score:.2%}")
        print(f"   Description: {finding.description}")

        # Show data insights
        if finding.evidence_trail:
            for evidence in finding.evidence_trail[:1]:  # Show first evidence
                print(f"   Key Data:")
                for key, value in evidence.data.items():
                    if isinstance(value, (int, float)):
                        print(f"     - {key}: {value}")
                    elif isinstance(value, str):
                        print(f"     - {key}: {value}")

    # Performance metrics
    metrics = pulse.get_performance_metrics()
    print(f"\n{'-'*80}")
    print(f"Performance Metrics:")
    print(f"  Success Rate: {metrics['success_rate']:.1%}")

    return report


async def test_parallel_execution():
    """Test running all three agents in parallel."""
    print("\n" + "="*80)
    print("PARALLEL MULTI-AGENT EXECUTION TEST")
    print("="*80 + "\n")

    company = "GlobalCorp Industries"

    print(f"Target: {company}")
    print("Running Sentinel, Veritas, and Pulse agents in parallel...\n")

    # Initialize agents
    sentinel = SentinelAgent(timeout_seconds=30)
    veritas = VeritasAgent(timeout_seconds=30)
    pulse = PulseAgent(timeout_seconds=30)

    # Prepare contexts
    sentinel_context = {"coordinates": (40.7128, -74.0060), "time_range_days": 180}
    veritas_context = {"industry": "manufacturing", "products": ["electronics"]}
    pulse_context = {"timeframe_days": 60, "languages": ["en"]}

    # Execute in parallel
    start_time = datetime.utcnow()

    results = await asyncio.gather(
        sentinel.execute_with_timeout(company, sentinel_context),
        veritas.execute_with_timeout(company, veritas_context),
        pulse.execute_with_timeout(company, pulse_context),
        return_exceptions=True,
    )

    execution_time = (datetime.utcnow() - start_time).total_seconds()

    sentinel_report, veritas_report, pulse_report = results

    # Aggregate results
    print("Parallel Execution Complete!")
    print(f"Total Execution Time: {execution_time:.2f}s\n")

    print("Results Summary:")
    print(f"  Sentinel: {len(sentinel_report.findings)} findings, "
          f"{sentinel_report.overall_risk_score:.1f}/100 risk score")
    print(f"  Veritas: {len(veritas_report.findings)} findings, "
          f"{veritas_report.overall_risk_score:.1f}/100 risk score")
    print(f"  Pulse: {len(pulse_report.findings)} findings, "
          f"{pulse_report.overall_risk_score:.1f}/100 risk score")

    # Calculate aggregate risk score
    avg_risk = (sentinel_report.overall_risk_score +
                veritas_report.overall_risk_score +
                pulse_report.overall_risk_score) / 3

    total_findings = (len(sentinel_report.findings) +
                     len(veritas_report.findings) +
                     len(pulse_report.findings))

    print(f"\nAggregate Assessment:")
    print(f"  Overall Risk Score: {avg_risk:.2f}/100")
    print(f"  Total Findings: {total_findings}")
    print(f"  Recommendation: {get_recommendation(avg_risk)}")

    return {
        "sentinel": sentinel_report,
        "veritas": veritas_report,
        "pulse": pulse_report,
        "aggregate_risk": avg_risk,
    }


async def test_adversarial_debate():
    """Test adversarial debate between agents."""
    print("\n" + "="*80)
    print("ADVERSARIAL DEBATE TEST")
    print("="*80 + "\n")

    # Create agents
    sentinel = SentinelAgent()
    veritas = VeritasAgent()

    from base_agent import Finding, Evidence, EvidenceType

    # Sentinel makes a claim
    print("SCENARIO: Sentinel detects environmental violation")
    print("-" * 80)

    sentinel_finding = Finding(
        agent_name="Sentinel",
        finding_type="pollution",
        severity="HIGH",
        title="Excessive air pollution detected",
        description="Air Quality Index exceeds safe levels near facility. AQI: 120",
        confidence_score=0.82,
    )

    evidence1 = Evidence(
        type=EvidenceType.SENSOR_DATA,
        source="EPA Air Quality Monitor",
        description="AQI reading of 120, PM2.5: 45 μg/m³",
        data={"aqi": 120, "pm25": 45},
        confidence=0.85,
    )
    sentinel_finding.add_evidence(evidence1)

    print(f"\nSentinel Finding:")
    print(f"  Title: {sentinel_finding.title}")
    print(f"  Severity: {sentinel_finding.severity}")
    print(f"  Confidence: {sentinel_finding.confidence_score:.2%}")
    print(f"  Evidence: {sentinel_finding.evidence_trail[0].description}")

    # Veritas challenges
    print(f"\n\nVeritas CHALLENGES with counter-evidence:")
    print("-" * 80)

    counter_evidence = [
        Evidence(
            type=EvidenceType.CERTIFICATION,
            source="ISO 14001 Environmental Management",
            description="Current ISO 14001 certification, last audit passed",
            data={"audit_date": "2024-10-15", "status": "compliant"},
            confidence=0.91,
        ),
        Evidence(
            type=EvidenceType.PUBLIC_RECORD,
            source="Air Quality Improvement Plan",
            description="Active air quality improvement program, 30% reduction target",
            data={"reduction_target": 0.30, "timeline": "2025"},
            confidence=0.78,
        ),
    ]

    for i, ev in enumerate(counter_evidence, 1):
        print(f"\n  Counter-Evidence {i}:")
        print(f"    Source: {ev.source}")
        print(f"    Description: {ev.description}")
        print(f"    Confidence: {ev.confidence:.2%}")

    # Perform challenge
    challenge_result = await veritas.challenge_finding(
        sentinel_finding,
        counter_evidence
    )

    print(f"\n\nDEBATE OUTCOME:")
    print("-" * 80)
    print(f"  Challenge Successful: {challenge_result['challenged']}")
    print(f"  Original Confidence: {challenge_result['original_confidence']:.2%}")
    print(f"  Adjusted Confidence: {challenge_result['adjusted_confidence']:.2%}")
    print(f"  Confidence Reduction: {challenge_result['adjustment_factor']:.2%}")
    print(f"\n  Interpretation: {challenge_result['reason']}")

    if challenge_result['adjusted_confidence'] < 0.5:
        print("\n  Result: Finding WEAKENED by counter-evidence")
        print("  Recommendation: Additional investigation required")
    else:
        print("\n  Result: Finding STANDS despite counter-evidence")
        print("  Recommendation: Concerns remain valid")


async def test_data_collection():
    """Test data collection capabilities of each agent."""
    print("\n" + "="*80)
    print("DATA COLLECTION TEST")
    print("="*80 + "\n")

    company = "Test Corporation"

    # Test Sentinel data collection
    print("1. Sentinel Agent - Environmental Data Collection")
    print("-" * 80)
    sentinel = SentinelAgent()
    sentinel_data = await sentinel.collect_data(
        company,
        {"coordinates": (40.7128, -74.0060), "time_range_days": 90}
    )
    print(f"  Collected {len(sentinel_data)} evidence pieces")
    print(f"  Evidence types: {set(e.type.value for e in sentinel_data)}")
    print(f"  Sources: {set(e.source for e in sentinel_data)}")

    # Test Veritas data collection
    print("\n2. Veritas Agent - Supply Chain Data Collection")
    print("-" * 80)
    veritas = VeritasAgent()
    veritas_data = await veritas.collect_data(
        company,
        {"industry": "manufacturing"}
    )
    print(f"  Collected {len(veritas_data)} evidence pieces")
    print(f"  Evidence types: {set(e.type.value for e in veritas_data)}")
    print(f"  Sources: {len(set(e.source for e in veritas_data))} unique sources")

    # Test Pulse data collection
    print("\n3. Pulse Agent - Media/Sentiment Data Collection")
    print("-" * 80)
    pulse = PulseAgent()
    pulse_data = await pulse.collect_data(
        company,
        {"timeframe_days": 60}
    )
    print(f"  Collected {len(pulse_data)} evidence pieces")
    print(f"  Evidence types: {set(e.type.value for e in pulse_data)}")
    print(f"  Time range: {min(e.timestamp for e in pulse_data).date()} to "
          f"{max(e.timestamp for e in pulse_data).date()}")

    # Test confidence calculation
    print("\n4. Confidence Score Calculation")
    print("-" * 80)
    sentinel_confidence = sentinel.calculate_confidence(sentinel_data)
    veritas_confidence = veritas.calculate_confidence(veritas_data)
    pulse_confidence = pulse.calculate_confidence(pulse_data)

    print(f"  Sentinel: {sentinel_confidence:.2%}")
    print(f"  Veritas: {veritas_confidence:.2%}")
    print(f"  Pulse: {pulse_confidence:.2%}")


def print_report_summary(report: AgentReport):
    """Print a formatted summary of an agent report."""
    print(f"\n{'='*80}")
    print(f"REPORT SUMMARY - {report.agent_name}")
    print(f"{'='*80}")
    print(f"Target: {report.target_entity}")
    print(f"Agent Type: {report.agent_type}")
    print(f"Execution Time: {report.execution_time_seconds:.2f}s")
    print(f"Overall Risk Score: {report.overall_risk_score:.2f}/100")
    print(f"Total Findings: {len(report.findings)}")

    # Breakdown by severity
    severity_counts = {}
    for finding in report.findings:
        severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1

    if severity_counts:
        print(f"\nFindings by Severity:")
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]:
            if severity in severity_counts:
                print(f"  {severity}: {severity_counts[severity]}")

    # Errors
    if report.errors:
        print(f"\nErrors Encountered: {len(report.errors)}")
        for error in report.errors:
            print(f"  - {error}")


def get_recommendation(risk_score: float) -> str:
    """Get investment recommendation based on risk score."""
    if risk_score < 20:
        return "CRITICAL - AVOID"
    elif risk_score < 40:
        return "HIGH RISK - Caution Required"
    elif risk_score < 60:
        return "MODERATE RISK - Monitor Closely"
    elif risk_score < 80:
        return "LOW RISK - Acceptable"
    else:
        return "MINIMAL RISK - Recommended"


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("GAIA AGENT FRAMEWORK - COMPREHENSIVE TEST SUITE")
    print("Sentinel, Veritas, and Pulse Agents")
    print("="*80)

    # Individual agent tests
    print("\n[TEST SUITE 1] Individual Agent Testing")
    sentinel_report = await test_sentinel_agent()
    veritas_report = await test_veritas_agent()
    pulse_report = await test_pulse_agent()

    # Parallel execution test
    print("\n[TEST SUITE 2] Parallel Execution")
    parallel_results = await test_parallel_execution()

    # Adversarial debate test
    print("\n[TEST SUITE 3] Adversarial Debate")
    await test_adversarial_debate()

    # Data collection test
    print("\n[TEST SUITE 4] Data Collection")
    await test_data_collection()

    # Save results to file
    output_file = "/tmp/gaia_test_results.json"
    results = {
        "test_time": datetime.utcnow().isoformat(),
        "sentinel_report": sentinel_report.to_dict(),
        "veritas_report": veritas_report.to_dict(),
        "pulse_report": pulse_report.to_dict(),
        "parallel_results": {
            "aggregate_risk": parallel_results["aggregate_risk"],
            "total_findings": sum([
                len(parallel_results["sentinel"].findings),
                len(parallel_results["veritas"].findings),
                len(parallel_results["pulse"].findings),
            ]),
        },
    }

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n{'='*80}")
    print(f"ALL TESTS COMPLETED SUCCESSFULLY")
    print(f"Results saved to: {output_file}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
