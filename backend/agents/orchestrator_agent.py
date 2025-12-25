"""
Orchestrator Agent - Meta-Agent Coordinator
Coordinates all specialized agents, implements LLM-powered adversarial debate,
resolves conflicts, builds consensus, and detects greenwashing.
"""

import asyncio
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from .base_agent import (
    BaseAgent,
    AgentReport,
    Finding,
    Evidence,
    EvidenceType,
)
from .prompts import get_system_prompt
from utils.llm_client import get_multi_llm_client, MultiProviderLLMClient


class DebateStance(str, Enum):
    """Stance in adversarial debate."""
    SUPPORTING = "supporting"
    CHALLENGING = "challenging"
    NEUTRAL = "neutral"


@dataclass
class DebateArgument:
    """Argument in adversarial debate."""
    agent_name: str
    stance: DebateStance
    round_number: int
    argument: str
    supporting_evidence: List[Evidence] = field(default_factory=list)
    rebuts_finding_id: Optional[str] = None
    confidence: float = 0.0


@dataclass
class DebateSession:
    """Complete debate session."""
    finding_id: str
    topic: str
    rounds: int
    arguments: List[DebateArgument] = field(default_factory=list)
    consensus_reached: bool = False
    final_confidence: float = 0.0
    resolution: str = ""
    winning_position: str = ""


@dataclass
class ConflictResolution:
    """Resolution of conflicting findings."""
    conflict_id: str
    conflicting_findings: List[str]
    conflicting_agents: List[str]
    resolution_method: str
    final_verdict: str
    confidence: float
    reasoning: str


@dataclass
class GreenwashingSignal:
    """Signal of potential greenwashing."""
    signal_type: str
    severity: str
    description: str
    evidence: List[Evidence] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class ConsensusScore:
    """Consensus metrics across agents."""
    topic: str
    agreement_level: float
    participating_agents: List[str]
    majority_position: str
    dissenting_agents: List[str] = field(default_factory=list)
    confidence: float = 0.0


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Meta-Agent with LLM-Powered Adversarial Debate

    Uses multi-provider LLM (Gemini, OpenAI, Claude) for real reasoning.

    Responsibilities:
    - Coordinate all specialized agents
    - Implement real LLM-powered adversarial debate
    - Resolve conflicts using AI reasoning
    - Build consensus across multiple perspectives
    - Detect greenwashing using LLM analysis
    - Synthesize evidence and findings
    """

    def __init__(
        self,
        name: str = "Orchestrator",
        timeout_seconds: int = 180,
        max_retries: int = 3,
        enable_debug: bool = False,
        debate_rounds: int = 3,
        llm_client: MultiProviderLLMClient = None,
    ):
        super().__init__(
            name=name,
            agent_type="orchestrator_meta_agent",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            enable_debug=enable_debug,
        )

        self.llm_client = llm_client or get_multi_llm_client()
        self.system_prompt = get_system_prompt("orchestrator")
        self.debate_rounds = debate_rounds
        self.agent_reports: Dict[str, AgentReport] = {}
        self.debate_sessions: List[DebateSession] = []
        self.conflict_resolutions: List[ConflictResolution] = []
        self.greenwashing_signals: List[GreenwashingSignal] = []

    async def analyze(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentReport:
        """Orchestrate multi-agent analysis with LLM-powered adversarial debate."""
        self.logger.info("starting_orchestration", target=target_entity)

        report = AgentReport(
            agent_name=self.name,
            agent_type=self.agent_type,
            target_entity=target_entity,
        )

        try:
            if context and "agent_reports" in context:
                self.agent_reports = context["agent_reports"]

            # Step 1: Synthesize all agent findings
            synthesized_findings = await self._synthesize_findings(target_entity)

            # Step 2: Identify conflicts
            conflicts = await self._identify_conflicts(synthesized_findings)

            # Step 3: Run LLM-powered adversarial debates
            await self._run_adversarial_debates(target_entity, conflicts)

            # Step 4: Resolve conflicts with LLM
            await self._resolve_conflicts(target_entity, conflicts)

            # Step 5: Build consensus
            consensus_scores = await self._build_consensus(synthesized_findings)

            # Step 6: LLM-powered greenwashing detection
            await self._detect_greenwashing(target_entity, synthesized_findings)

            # Step 7: Aggregate final scores
            final_scores = await self._aggregate_scores(target_entity)

            # Step 8: Create final findings
            final_findings = await self._create_final_findings(
                target_entity,
                synthesized_findings,
                consensus_scores,
                final_scores,
            )

            for finding in final_findings:
                report.add_finding(finding)

            report.metadata.update({
                "participating_agents": list(self.agent_reports.keys()),
                "debate_sessions": len(self.debate_sessions),
                "conflicts_resolved": len(self.conflict_resolutions),
                "greenwashing_signals": len(self.greenwashing_signals),
                "final_scores": final_scores,
            })

            self.logger.info(
                "orchestration_complete",
                findings_count=len(report.findings),
                final_score=final_scores.get("overall_score", 0),
            )

        except Exception as e:
            self.logger.error("orchestration_error", error=str(e))
            report.errors.append(f"Orchestration error: {str(e)}")

        return report

    async def collect_data(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Evidence]:
        """Collect evidence from all agent reports."""
        all_evidence = []
        for agent_name, agent_report in self.agent_reports.items():
            for finding in agent_report.findings:
                all_evidence.extend(finding.evidence_trail)
        return all_evidence

    def calculate_confidence(
        self,
        evidence: List[Evidence],
        context: Optional[Dict[str, Any]] = None,
    ) -> float:
        if not evidence:
            return 0.0
        confidences = [e.confidence for e in evidence]
        median_confidence = statistics.median(confidences)
        evidence_count_factor = min(1.0, len(evidence) / 10.0)
        return median_confidence * (0.7 + 0.3 * evidence_count_factor)

    async def _synthesize_findings(self, target_entity: str) -> Dict[str, List[Finding]]:
        """Synthesize findings from all agents by category."""
        synthesized = defaultdict(list)
        for agent_name, agent_report in self.agent_reports.items():
            for finding in agent_report.findings:
                synthesized[finding.finding_type].append(finding)

        self.logger.info(
            "findings_synthesized",
            categories=len(synthesized),
            total=sum(len(f) for f in synthesized.values()),
        )
        return dict(synthesized)

    async def _identify_conflicts(
        self,
        synthesized_findings: Dict[str, List[Finding]],
    ) -> List[Tuple[Finding, Finding]]:
        """Identify conflicting findings between agents."""
        conflicts = []
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}

        # Collect all findings for cross-category comparison
        all_findings = [f for flist in synthesized_findings.values() for f in flist]

        # Strategy 1: Same category conflicts (original)
        for category, findings in synthesized_findings.items():
            for i, finding1 in enumerate(findings):
                for finding2 in findings[i+1:]:
                    if finding1.agent_name == finding2.agent_name:
                        continue

                    severity_diff = abs(
                        severity_order.get(finding1.severity, 0) -
                        severity_order.get(finding2.severity, 0)
                    )

                    # Lower threshold: severity diff >= 1 and at least one high confidence
                    if severity_diff >= 1 and (finding1.confidence_score > 0.5 or finding2.confidence_score > 0.5):
                        conflicts.append((finding1, finding2))

        # Strategy 2: Cross-category conflicts (different agent perspectives)
        for i, finding1 in enumerate(all_findings):
            for finding2 in all_findings[i+1:]:
                if finding1.agent_name == finding2.agent_name:
                    continue
                if (finding1, finding2) in conflicts or (finding2, finding1) in conflicts:
                    continue

                # Look for positive vs negative assessments
                sev1 = severity_order.get(finding1.severity, 2)
                sev2 = severity_order.get(finding2.severity, 2)

                # If one agent says LOW risk and another says HIGH/CRITICAL
                if (sev1 <= 1 and sev2 >= 3) or (sev2 <= 1 and sev1 >= 3):
                    conflicts.append((finding1, finding2))

        # Strategy 3: Always generate at least 1 debate if we have findings from multiple agents
        if not conflicts and len(set(f.agent_name for f in all_findings)) >= 2:
            # Pick the two most different severity findings from different agents
            sorted_findings = sorted(all_findings, key=lambda f: severity_order.get(f.severity, 2))
            for f1 in sorted_findings[:3]:
                for f2 in sorted_findings[-3:]:
                    if f1.agent_name != f2.agent_name and (f1, f2) not in conflicts:
                        conflicts.append((f1, f2))
                        break
                if conflicts:
                    break

        self.logger.info("conflicts_identified", count=len(conflicts))
        return conflicts

    async def _run_adversarial_debates(
        self,
        target_entity: str,
        conflicts: List[Tuple[Finding, Finding]],
    ) -> None:
        """Run LLM-powered adversarial debates on conflicting findings."""
        from config import get_settings
        settings = get_settings()
        max_debates = getattr(settings, 'MAX_DEBATES', 2)  # Default to 2 debates max

        for idx, (finding1, finding2) in enumerate(conflicts[:max_debates]):  # Limit debates
            # Create a more descriptive topic from both findings
            topic = f"{finding1.title} vs {finding2.title}"
            if len(topic) > 80:
                topic = f"{finding1.finding_type}: {finding1.agent_name} vs {finding2.agent_name}"

            session = DebateSession(
                finding_id=f"{finding1.id}_vs_{finding2.id}",
                topic=topic,
                rounds=self.debate_rounds,
            )

            for round_num in range(1, self.debate_rounds + 1):
                # LLM generates supporting argument
                support_arg = await self._generate_debate_argument(
                    target_entity=target_entity,
                    finding=finding1,
                    opposing_finding=finding2,
                    round_num=round_num,
                    stance="supporting",
                    previous_arguments=session.arguments,
                )
                session.arguments.append(support_arg)

                # LLM generates challenging argument
                challenge_arg = await self._generate_debate_argument(
                    target_entity=target_entity,
                    finding=finding2,
                    opposing_finding=finding1,
                    round_num=round_num,
                    stance="challenging",
                    previous_arguments=session.arguments,
                )
                session.arguments.append(challenge_arg)

            # LLM determines final resolution
            resolution = await self._generate_debate_resolution(
                target_entity, session, finding1, finding2
            )
            session.resolution = resolution["summary"]
            session.winning_position = resolution["winner"]
            session.final_confidence = resolution["confidence"]
            session.consensus_reached = resolution["consensus"]

            self.debate_sessions.append(session)

    async def _generate_debate_argument(
        self,
        target_entity: str,
        finding: Finding,
        opposing_finding: Finding,
        round_num: int,
        stance: str,
        previous_arguments: List[DebateArgument],
    ) -> DebateArgument:
        """Generate a debate argument using LLM."""
        import random
        try:
            prev_args_text = ""
            if previous_arguments:
                prev_args_text = "\n".join([
                    f"- {arg.agent_name} ({arg.stance.value}): {arg.argument[:200]}"
                    for arg in previous_arguments[-4:]
                ])

            # Add unique identifiers to prevent caching
            unique_id = random.randint(1000, 9999)

            if stance == "supporting":
                role_desc = f"You are the {finding.agent_name} agent DEFENDING your findings"
                action = "DEFEND your position and explain why your analysis is accurate"
            else:
                role_desc = f"You are the {opposing_finding.agent_name} agent CHALLENGING the opposing view"
                action = "CHALLENGE the opposing position and point out flaws or missing considerations"

            prompt = f"""[Debate ID: {unique_id}] {role_desc} in an ESG debate about {target_entity}.

ROUND {round_num} of {self.debate_rounds}

YOUR FINDING TO {stance.upper()}:
Title: {finding.title}
Details: {finding.description}
Severity Assessment: {finding.severity}
Your Agent Role: {finding.agent_name}

THE OPPOSING VIEW YOU MUST ADDRESS:
Title: {opposing_finding.title}
Details: {opposing_finding.description}
Severity: {opposing_finding.severity}
Opposing Agent: {opposing_finding.agent_name}

{f"PREVIOUS DEBATE EXCHANGES:{chr(10)}{prev_args_text}" if prev_args_text else "This is the opening argument."}

YOUR TASK: {action}
Write a unique, specific argument (2-3 sentences) that directly addresses the conflict between these two findings.
{"Build on or counter the previous arguments." if round_num > 1 else "Make your opening case."}
Be specific about {target_entity} and reference concrete ESG factors."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.7,  # Higher temperature for more varied debate arguments
            )

            # Use correct agent name based on stance
            agent_name = finding.agent_name if stance == "supporting" else opposing_finding.agent_name

            return DebateArgument(
                agent_name=agent_name,
                stance=DebateStance.SUPPORTING if stance == "supporting" else DebateStance.CHALLENGING,
                round_number=round_num,
                argument=result.strip(),
                supporting_evidence=finding.evidence_trail[:2],
                confidence=finding.confidence_score,
            )

        except Exception as e:
            self.logger.error("debate_argument_error", error=str(e))
            fallback_agent = finding.agent_name if stance == "supporting" else opposing_finding.agent_name
            return DebateArgument(
                agent_name=fallback_agent,
                stance=DebateStance.SUPPORTING if stance == "supporting" else DebateStance.CHALLENGING,
                round_number=round_num,
                argument=f"[{fallback_agent}'s argument on {finding.title}]",
                confidence=finding.confidence_score * 0.5,
            )

    async def _generate_debate_resolution(
        self,
        target_entity: str,
        session: DebateSession,
        finding1: Finding,
        finding2: Finding,
    ) -> Dict[str, Any]:
        """Generate debate resolution using LLM."""
        try:
            arguments_text = "\n".join([
                f"Round {arg.round_number} - {arg.agent_name} ({arg.stance.value}): {arg.argument}"
                for arg in session.arguments
            ])

            prompt = f"""As a neutral ESG arbiter, evaluate this adversarial debate about {target_entity}.

POSITION 1 ({finding1.agent_name}):
{finding1.title}: {finding1.description}
Severity: {finding1.severity}

POSITION 2 ({finding2.agent_name}):
{finding2.title}: {finding2.description}
Severity: {finding2.severity}

DEBATE ARGUMENTS:
{arguments_text}

Analyze the debate and determine:
1. Which position has stronger evidence and reasoning?
2. What is the final verdict?
3. Was consensus reached?
4. What is your confidence level (0-1)?

Provide a concise resolution summary (2-3 sentences)."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
            )

            result_lower = result.lower()
            if finding1.agent_name.lower() in result_lower and "stronger" in result_lower:
                winner = "Position 1"
                confidence = 0.75
            elif finding2.agent_name.lower() in result_lower and "stronger" in result_lower:
                winner = "Position 2"
                confidence = 0.75
            else:
                winner = "Balanced"
                confidence = 0.60

            consensus = "consensus" in result_lower or "agree" in result_lower

            return {
                "summary": result.strip()[:500],
                "winner": winner,
                "confidence": confidence,
                "consensus": consensus,
            }

        except Exception as e:
            self.logger.error("debate_resolution_error", error=str(e))
            return {
                "summary": "Unable to determine clear resolution",
                "winner": "Inconclusive",
                "confidence": 0.5,
                "consensus": False,
            }

    async def _resolve_conflicts(
        self,
        target_entity: str,
        conflicts: List[Tuple[Finding, Finding]],
    ) -> None:
        """Resolve conflicts using debate outcomes and LLM reasoning."""
        for finding1, finding2 in conflicts:
            debate_session = next(
                (s for s in self.debate_sessions
                 if finding1.id in s.finding_id or finding2.id in s.finding_id),
                None
            )

            if debate_session:
                final_verdict = debate_session.resolution
                confidence = debate_session.final_confidence
                reasoning = f"Debate winner: {debate_session.winning_position}"
            else:
                evidence_score1 = len(finding1.evidence_trail) * finding1.confidence_score
                evidence_score2 = len(finding2.evidence_trail) * finding2.confidence_score

                if evidence_score1 > evidence_score2 * 1.2:
                    final_verdict = f"{finding1.agent_name} finding accepted"
                    confidence = finding1.confidence_score
                elif evidence_score2 > evidence_score1 * 1.2:
                    final_verdict = f"{finding2.agent_name} finding accepted"
                    confidence = finding2.confidence_score
                else:
                    final_verdict = "Findings merged with adjusted confidence"
                    confidence = (finding1.confidence_score + finding2.confidence_score) / 2

                reasoning = "Evidence-based comparison"

            resolution = ConflictResolution(
                conflict_id=f"conflict_{finding1.id}_{finding2.id}",
                conflicting_findings=[finding1.id, finding2.id],
                conflicting_agents=[finding1.agent_name, finding2.agent_name],
                resolution_method="llm_adversarial_debate",
                final_verdict=final_verdict,
                confidence=confidence,
                reasoning=reasoning,
            )

            self.conflict_resolutions.append(resolution)

    async def _build_consensus(
        self,
        synthesized_findings: Dict[str, List[Finding]],
    ) -> List[ConsensusScore]:
        """Build consensus across agent findings."""
        consensus_scores = []

        for category, findings in synthesized_findings.items():
            if len(findings) < 2:
                continue

            severity_counts = defaultdict(int)
            agents_by_severity = defaultdict(list)

            for finding in findings:
                severity_counts[finding.severity] += 1
                agents_by_severity[finding.severity].append(finding.agent_name)

            majority_severity = max(severity_counts, key=severity_counts.get)
            majority_count = severity_counts[majority_severity]
            total_findings = len(findings)
            agreement_level = majority_count / total_findings

            dissenting = []
            for severity, agents in agents_by_severity.items():
                if severity != majority_severity:
                    dissenting.extend(agents)

            consensus = ConsensusScore(
                topic=category,
                agreement_level=agreement_level,
                participating_agents=[f.agent_name for f in findings],
                majority_position=majority_severity,
                dissenting_agents=dissenting,
                confidence=agreement_level,
            )
            consensus_scores.append(consensus)

        return consensus_scores

    async def _detect_greenwashing(
        self,
        target_entity: str,
        synthesized_findings: Dict[str, List[Finding]],
    ) -> None:
        """Detect potential greenwashing using LLM analysis."""
        try:
            all_findings = [f for flist in synthesized_findings.values() for f in flist]

            findings_summary = "\n".join([
                f"- [{f.agent_name}] {f.title}: {f.description[:100]} (Severity: {f.severity})"
                for f in all_findings[:15]
            ])

            prompt = f"""Analyze these ESG findings for {target_entity} for potential greenwashing or "impact washing".

FINDINGS FROM MULTIPLE AGENTS:
{findings_summary}

Check for these greenwashing patterns:
1. VAGUE_CLAIMS: Unsubstantiated eco-friendly claims without evidence
2. LACK_OF_EVIDENCE: Positive findings without supporting data
3. CONTRADICTORY_DATA: Conflicting claims across different areas
4. CHERRY_PICKING: Only highlighting positive metrics while hiding negatives
5. HIDDEN_TRADEOFFS: Claims that ignore negative impacts in other areas

For each pattern detected, rate severity (low/medium/high/critical) and explain.
If no greenwashing is detected, state that clearly."""

            result = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
            )

            # Parse LLM response for signals with better descriptions
            result_lower = result.lower()
            patterns = [
                ("vague_claims", "vague", "Unsubstantiated environmental claims lacking specific metrics or verification"),
                ("lack_of_evidence", "lack of evidence", "Positive sustainability claims without supporting data or third-party validation"),
                ("contradictory_data", "contradict", "Conflicting statements between environmental claims and actual operational data"),
                ("cherry_picking", "cherry", "Selective reporting of favorable ESG metrics while omitting negative indicators"),
                ("hidden_tradeoffs", "tradeoff", "Environmental benefits claimed while ignoring negative impacts in other areas"),
            ]

            for pattern_type, keyword, default_desc in patterns:
                if keyword in result_lower:
                    # Determine severity from context
                    if "critical" in result_lower or "severe" in result_lower:
                        severity = "critical"
                    elif "significant" in result_lower or "major" in result_lower:
                        severity = "high"
                    elif "minor" in result_lower or "low" in result_lower:
                        severity = "low"
                    else:
                        severity = "medium"

                    # Try to extract relevant sentence from LLM response
                    description = default_desc
                    for sentence in result.split('.'):
                        if keyword in sentence.lower() and len(sentence) > 20:
                            description = sentence.strip()[:200]
                            break

                    self.greenwashing_signals.append(GreenwashingSignal(
                        signal_type=pattern_type,
                        severity=severity,
                        description=description,
                        confidence=0.75,
                    ))

            # Add overall greenwashing finding evidence
            self.greenwashing_signals.append(GreenwashingSignal(
                signal_type="llm_analysis",
                severity="info",
                description=result[:300],
                confidence=0.80,
            ))

        except Exception as e:
            self.logger.error("greenwashing_detection_error", error=str(e))

    async def _aggregate_scores(self, target_entity: str) -> Dict[str, float]:
        """Aggregate final scores from all agents with LLM synthesis."""
        if not self.agent_reports:
            return {"overall_score": 50.0}

        risk_scores = [report.overall_risk_score for report in self.agent_reports.values()]

        avg_risk = statistics.mean(risk_scores)
        std_dev = statistics.stdev(risk_scores) if len(risk_scores) > 1 else 0

        greenwashing_penalty = len([s for s in self.greenwashing_signals if s.severity in ["high", "critical"]]) * 8

        final_risk_score = min(100.0, max(0.0, avg_risk + greenwashing_penalty))

        return {
            "overall_score": 100 - final_risk_score,
            "risk_score": final_risk_score,
            "confidence_score": max(0, 100 - std_dev * 10),
            "consensus_level": max(0, 100 - std_dev * 20),
            "greenwashing_risk": min(100.0, len(self.greenwashing_signals) * 12),
        }

    async def _create_final_findings(
        self,
        target_entity: str,
        synthesized_findings: Dict[str, List[Finding]],
        consensus_scores: List[ConsensusScore],
        final_scores: Dict[str, float],
    ) -> List[Finding]:
        """Create final orchestrated findings with LLM synthesis."""
        findings = []

        # Generate overall assessment using LLM
        try:
            all_findings_text = "\n".join([
                f"- {f.agent_name}: {f.title} ({f.severity})"
                for flist in synthesized_findings.values()
                for f in flist
            ][:20])

            prompt = f"""Synthesize a final ESG assessment for {target_entity} based on these multi-agent findings:

{all_findings_text}

SCORES:
- Overall Score: {final_scores.get('overall_score', 50):.1f}/100
- Risk Score: {final_scores.get('risk_score', 50):.1f}/100
- Greenwashing Risk: {final_scores.get('greenwashing_risk', 0):.1f}/100

DEBATES: {len(self.debate_sessions)} adversarial debates conducted
CONFLICTS RESOLVED: {len(self.conflict_resolutions)}

Provide a 2-3 sentence executive summary of the ESG assessment."""

            summary = await self.llm_client.generate_text(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.4,
            )

            overall_finding = Finding(
                agent_name=self.name,
                finding_type="overall_assessment",
                severity=self._score_to_severity(final_scores["overall_score"]),
                title="Comprehensive Multi-Agent ESG Assessment",
                description=summary.strip()[:500],
                confidence_score=final_scores["confidence_score"] / 100,
                metadata={
                    "overall_score": final_scores["overall_score"],
                    "risk_score": final_scores["risk_score"],
                    "participating_agents": list(self.agent_reports.keys()),
                },
            )

            overall_finding.add_evidence(Evidence(
                type=EvidenceType.API_RESPONSE,
                source="LLM-Powered Orchestration",
                description="AI-synthesized assessment from multiple agents",
                data={"agent_count": len(self.agent_reports)},
                confidence=final_scores["confidence_score"] / 100,
            ))

            findings.append(overall_finding)

        except Exception as e:
            self.logger.error("final_findings_error", error=str(e))

        # Greenwashing finding
        high_severity_signals = [s for s in self.greenwashing_signals if s.severity in ["high", "critical"]]
        if high_severity_signals:
            findings.append(Finding(
                agent_name=self.name,
                finding_type="greenwashing_detection",
                severity="HIGH",
                title=f"Greenwashing Risk Detected ({len(high_severity_signals)} signals)",
                description=f"LLM analysis identified potential greenwashing patterns",
                confidence_score=0.78,
                metadata={"signals": [s.signal_type for s in high_severity_signals]},
            ))

        # Debate summary finding
        if self.debate_sessions:
            findings.append(Finding(
                agent_name=self.name,
                finding_type="adversarial_validation",
                severity="INFO",
                title=f"LLM Adversarial Debates Completed ({len(self.debate_sessions)})",
                description=f"{self.debate_rounds}-round debates validated controversial findings",
                confidence_score=statistics.mean([s.final_confidence for s in self.debate_sessions]),
                metadata={
                    "debates": len(self.debate_sessions),
                    "consensus_reached": sum(1 for s in self.debate_sessions if s.consensus_reached),
                },
            ))

        return findings

    def _score_to_severity(self, score: float) -> str:
        if score >= 80:
            return "INFO"
        elif score >= 60:
            return "LOW"
        elif score >= 40:
            return "MEDIUM"
        elif score >= 20:
            return "HIGH"
        else:
            return "CRITICAL"
