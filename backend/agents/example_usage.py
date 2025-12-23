"""
Example Usage of GAIA Agents
Demonstrates how to use the specialized agents and orchestrator.
"""

import asyncio
from agents import (
    RegulusAgent,
    ImpactAgent,
    OrchestratorAgent,
    get_agent,
    get_all_agents,
)


async def example_individual_agent():
    """Example: Using an individual agent."""
    print("\n=== Example 1: Individual Agent Usage ===\n")

    # Create a Regulus (regulatory compliance) agent
    regulus = RegulusAgent(
        timeout_seconds=90,
        enable_debug=True
    )

    # Analyze a company
    target_company = "TechCorp International"
    report = await regulus.analyze(
        target_entity=target_company,
        context={
            "industry": "technology",
            "jurisdictions": ["US", "EU", "CN"],
        }
    )

    # Display results
    print(f"Agent: {report.agent_name}")
    print(f"Target: {report.target_entity}")
    print(f"Risk Score: {report.overall_risk_score:.2f}")
    print(f"Findings: {len(report.findings)}")

    for finding in report.findings:
        print(f"\n  - {finding.title}")
        print(f"    Severity: {finding.severity}")
        print(f"    Confidence: {finding.confidence_score:.2f}")

    # Calculate compliance score
    compliance_metrics = regulus.calculate_compliance_score(report)
    print(f"\nCompliance Score: {compliance_metrics['compliance_score']:.1f}")
    print(f"Grade: {compliance_metrics['grade']}")
    print(f"Risk Level: {compliance_metrics['risk_level']}")


async def example_impact_agent():
    """Example: Using the Impact Quantification agent."""
    print("\n=== Example 2: Impact Quantification Agent ===\n")

    # Create an Impact agent
    impact_agent = ImpactAgent(
        timeout_seconds=90,
        enable_debug=True
    )

    # Analyze a sustainable investment
    target_project = "Green Energy Initiative"
    report = await impact_agent.analyze(
        target_entity=target_project,
        context={
            "sector": "renewable_energy",
            "investment_amount": 5_000_000,  # $5M investment
        }
    )

    print(f"Agent: {report.agent_name}")
    print(f"Target: {report.target_entity}")
    print(f"Findings: {len(report.findings)}")

    # Display SDG alignment
    if "sdg_alignment" in report.metadata:
        print("\nSDG Alignment:")
        for sdg in report.metadata["sdg_alignment"]:
            print(f"  - SDG {sdg['goal_number']}: {sdg['goal_name']}")
            print(f"    Alignment Score: {sdg['alignment_score']:.2f}")
            print(f"    Contribution: {sdg['contribution_level']}")

    # Display impact metrics
    if "impact_metrics" in report.metadata:
        print("\nImpact Metrics (per $1M invested):")
        for metric in report.metadata["impact_metrics"][:5]:
            print(f"  - {metric['name']}: {metric['per_million_usd']:.2f} {metric['unit']}")

    # Generate impact report
    impact_report = impact_agent.generate_impact_report(report)
    print(f"\nOverall Impact Score: {impact_report['overall_impact_score']:.1f}")
    print(f"Confidence Level: {impact_report['confidence_level']}")


async def example_orchestrator():
    """Example: Using the Orchestrator to coordinate multiple agents."""
    print("\n=== Example 3: Multi-Agent Orchestration ===\n")

    target_entity = "SustainableCorp Inc."

    # Step 1: Run individual agents
    print("Running individual agents...")

    regulus = RegulusAgent()
    impact = ImpactAgent()

    regulus_report = await regulus.analyze(
        target_entity=target_entity,
        context={"industry": "manufacturing"}
    )

    impact_report = await impact.analyze(
        target_entity=target_entity,
        context={"sector": "sustainable_agriculture", "investment_amount": 10_000_000}
    )

    print(f"  ✓ Regulus: {len(regulus_report.findings)} findings")
    print(f"  ✓ Impact: {len(impact_report.findings)} findings")

    # Step 2: Orchestrate with meta-agent
    print("\nOrchestrating with meta-agent...")

    orchestrator = OrchestratorAgent(
        debate_rounds=3,
        timeout_seconds=180
    )

    final_report = await orchestrator.analyze(
        target_entity=target_entity,
        context={
            "agent_reports": {
                "regulus": regulus_report,
                "impact": impact_report,
            }
        }
    )

    # Display orchestrated results
    print(f"\n=== Final Orchestrated Assessment ===")
    print(f"Target: {final_report.target_entity}")
    print(f"Overall Risk Score: {final_report.overall_risk_score:.2f}")
    print(f"Total Findings: {len(final_report.findings)}")

    # Display metadata
    metadata = final_report.metadata
    print(f"\nParticipating Agents: {', '.join(metadata.get('participating_agents', []))}")
    print(f"Debate Sessions: {metadata.get('debate_sessions', 0)}")
    print(f"Conflicts Resolved: {metadata.get('conflicts_resolved', 0)}")
    print(f"Greenwashing Signals: {metadata.get('greenwashing_signals', 0)}")

    # Display consensus scores
    if "consensus_scores" in metadata:
        print("\nConsensus Analysis:")
        for cs in metadata["consensus_scores"]:
            print(f"  - {cs['topic']}: {cs['agreement_level']*100:.1f}% agreement")
            print(f"    Majority Position: {cs['majority_position']}")

    # Display final scores
    if "final_scores" in metadata:
        scores = metadata["final_scores"]
        print(f"\nFinal Scores:")
        print(f"  Overall Score: {scores.get('overall_score', 0):.1f}/100")
        print(f"  Confidence: {scores.get('confidence_score', 0):.1f}/100")
        print(f"  Consensus Level: {scores.get('consensus_level', 0):.1f}/100")
        print(f"  Greenwashing Risk: {scores.get('greenwashing_risk', 0):.1f}/100")

    # Display key findings
    print("\nKey Findings:")
    for i, finding in enumerate(final_report.findings, 1):
        print(f"\n  {i}. {finding.title}")
        print(f"     Type: {finding.finding_type}")
        print(f"     Severity: {finding.severity}")
        print(f"     Confidence: {finding.confidence_score:.2f}")


async def example_factory_pattern():
    """Example: Using factory functions."""
    print("\n=== Example 4: Factory Pattern Usage ===\n")

    # Create agent using factory function
    regulus = get_agent("regulus", timeout_seconds=120)
    print(f"Created agent: {regulus}")

    # Get all agents at once
    all_agents = get_all_agents(timeout_seconds=90, enable_debug=False)
    print(f"\nAll agents: {list(all_agents.keys())}")

    # Run analysis with all agents
    target = "GlobalCorp Ltd."
    reports = {}

    for agent_type, agent in all_agents.items():
        if agent_type != "orchestrator":  # Skip orchestrator for now
            report = await agent.analyze(target)
            reports[agent_type] = report
            print(f"  ✓ {agent_type}: {len(report.findings)} findings")


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("GAIA Agent System - Usage Examples")
    print("="*60)

    # Run examples
    await example_individual_agent()
    await example_impact_agent()
    await example_orchestrator()
    await example_factory_pattern()

    print("\n" + "="*60)
    print("Examples completed successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
