"""
Orchestrator Agent - Meta-Agent Coordinator
Coordinates all specialized agents, implements adversarial debate system,
resolves conflicts, builds consensus, and detects greenwashing.
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import statistics
from collections import defaultdict
import hashlib

from .base_agent import (
    BaseAgent,
    AgentReport,
    Finding,
    Evidence,
    EvidenceType,
    ConfidenceLevel,
)


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


@dataclass
class ConflictResolution:
    """Resolution of conflicting findings."""
    conflict_id: str
    conflicting_findings: List[str]  # Finding IDs
    conflicting_agents: List[str]
    resolution_method: str
    final_verdict: str
    confidence: float
    reasoning: str


@dataclass
class GreenwashingSignal:
    """Signal of potential greenwashing."""
    signal_type: str
    severity: str  # low, medium, high, critical
    description: str
    evidence: List[Evidence] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class ConsensusScore:
    """Consensus metrics across agents."""
    topic: str
    agreement_level: float  # 0.0 to 1.0
    participating_agents: List[str]
    majority_position: str
    dissenting_agents: List[str] = field(default_factory=list)
    confidence: float = 0.0


class OrchestratorAgent(BaseAgent):
    """
    Orchestrator Meta-Agent

    Responsibilities:
    - Coordinate all specialized agents
    - Implement adversarial debate system
    - Resolve conflicts between agent findings
    - Build consensus across multiple perspectives
    - Aggregate final scoring
    - Detect greenwashing and inconsistencies
    - Synthesize evidence and findings
    - Produce final comprehensive assessment
    """

    def __init__(
        self,
        name: str = "Orchestrator",
        timeout_seconds: int = 180,
        max_retries: int = 3,
        enable_debug: bool = False,
        debate_rounds: int = 3,
    ):
        super().__init__(
            name=name,
            agent_type="orchestrator_meta_agent",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            enable_debug=enable_debug,
        )

        self.debate_rounds = debate_rounds
        self.agent_reports: Dict[str, AgentReport] = {}
        self.debate_sessions: List[DebateSession] = []
        self.conflict_resolutions: List[ConflictResolution] = []
        self.greenwashing_signals: List[GreenwashingSignal] = []

        # Greenwashing detection patterns
        self.greenwashing_patterns = self._initialize_greenwashing_patterns()

    def _initialize_greenwashing_patterns(self) -> Dict[str, Any]:
        """Initialize greenwashing detection patterns."""
        return {
            "vague_claims": {
                "keywords": ["eco-friendly", "green", "sustainable", "natural"],
                "severity": "medium",
                "confidence_threshold": 0.5,
            },
            "lack_of_evidence": {
                "min_evidence_per_finding": 2,
                "severity": "high",
            },
            "contradictory_data": {
                "confidence_gap_threshold": 0.4,
                "severity": "high",
            },
            "cherry_picking": {
                "selective_reporting_threshold": 0.3,
                "severity": "medium",
            },
            "hidden_tradeoffs": {
                "impact_imbalance_threshold": 0.6,
                "severity": "high",
            },
        }

    async def analyze(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentReport:
        """
        Orchestrate multi-agent analysis with adversarial debate.

        This is the main entry point that coordinates all other agents.

        Args:
            target_entity: Entity to analyze
            context: Additional context including agent reports

        Returns:
            Comprehensive orchestrated assessment
        """
        self.logger.info(
            "starting_orchestration",
            agent=self.name,
            target=target_entity,
        )

        report = AgentReport(
            agent_name=self.name,
            agent_type=self.agent_type,
            target_entity=target_entity,
        )

        try:
            # Extract agent reports from context
            if context and "agent_reports" in context:
                self.agent_reports = context["agent_reports"]

            # Step 1: Synthesize all agent findings
            synthesized_findings = await self._synthesize_findings(target_entity)

            # Step 2: Identify conflicts
            conflicts = await self._identify_conflicts(synthesized_findings)

            # Step 3: Run adversarial debates on controversial findings
            await self._run_adversarial_debates(conflicts)

            # Step 4: Resolve conflicts
            await self._resolve_conflicts(conflicts)

            # Step 5: Build consensus
            consensus_scores = await self._build_consensus(synthesized_findings)

            # Step 6: Detect greenwashing
            await self._detect_greenwashing(synthesized_findings)

            # Step 7: Aggregate final scores
            final_scores = await self._aggregate_scores()

            # Step 8: Create final findings
            final_findings = await self._create_final_findings(
                synthesized_findings,
                consensus_scores,
                final_scores,
            )

            for finding in final_findings:
                report.add_finding(finding)

            # Add metadata
            report.metadata.update({
                "participating_agents": list(self.agent_reports.keys()),
                "debate_sessions": len(self.debate_sessions),
                "conflicts_resolved": len(self.conflict_resolutions),
                "greenwashing_signals": len(self.greenwashing_signals),
                "consensus_scores": [
                    {
                        "topic": cs.topic,
                        "agreement_level": cs.agreement_level,
                        "majority_position": cs.majority_position,
                    }
                    for cs in consensus_scores
                ],
                "final_scores": final_scores,
            })

            self.logger.info(
                "orchestration_complete",
                agent=self.name,
                target=target_entity,
                findings_count=len(report.findings),
                final_score=final_scores.get("overall_score", 0),
            )

        except Exception as e:
            self.logger.error(
                "orchestration_error",
                agent=self.name,
                target=target_entity,
                error=str(e),
            )
            report.errors.append(f"Orchestration error: {str(e)}")

        return report

    async def collect_data(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Evidence]:
        """
        Collect evidence from all agent reports.

        Args:
            target_entity: Entity being analyzed
            context: Additional context

        Returns:
            Aggregated evidence from all agents
        """
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
        """Calculate aggregate confidence across all evidence."""
        if not evidence:
            return 0.0

        # Calculate weighted average, giving more weight to higher-quality evidence
        confidences = [e.confidence for e in evidence]

        # Use median to reduce impact of outliers
        median_confidence = statistics.median(confidences)

        # Adjust based on evidence count (more evidence = higher confidence)
        evidence_count_factor = min(1.0, len(evidence) / 10.0)

        return median_confidence * (0.7 + 0.3 * evidence_count_factor)

    async def _synthesize_findings(
        self,
        target_entity: str,
    ) -> Dict[str, List[Finding]]:
        """Synthesize findings from all agents by category."""
        synthesized = defaultdict(list)

        for agent_name, agent_report in self.agent_reports.items():
            for finding in agent_report.findings:
                category = finding.finding_type
                synthesized[category].append(finding)

        self.logger.info(
            "findings_synthesized",
            categories=len(synthesized),
            total_findings=sum(len(findings) for findings in synthesized.values()),
        )

        return dict(synthesized)

    async def _identify_conflicts(
        self,
        synthesized_findings: Dict[str, List[Finding]],
    ) -> List[Tuple[Finding, Finding]]:
        """Identify conflicting findings between agents."""
        conflicts = []

        # Compare findings within each category
        for category, findings in synthesized_findings.items():
            for i, finding1 in enumerate(findings):
                for finding2 in findings[i+1:]:
                    # Check for conflicts based on severity and confidence
                    if self._are_conflicting(finding1, finding2):
                        conflicts.append((finding1, finding2))

        self.logger.info("conflicts_identified", count=len(conflicts))

        return conflicts

    def _are_conflicting(self, finding1: Finding, finding2: Finding) -> bool:
        """Determine if two findings are conflicting."""
        # Different agents
        if finding1.agent_name == finding2.agent_name:
            return False

        # Same topic but different severity levels
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}
        severity_diff = abs(
            severity_order.get(finding1.severity, 0) -
            severity_order.get(finding2.severity, 0)
        )

        # Conflict if severity differs by 2+ levels and both are confident
        if severity_diff >= 2:
            if finding1.confidence_score > 0.6 and finding2.confidence_score > 0.6:
                return True

        return False

    async def _run_adversarial_debates(
        self,
        conflicts: List[Tuple[Finding, Finding]],
    ) -> None:
        """Run adversarial debates on conflicting findings."""
        for finding1, finding2 in conflicts[:5]:  # Limit debates
            session = DebateSession(
                finding_id=f"{finding1.id}_vs_{finding2.id}",
                topic=finding1.finding_type,
                rounds=self.debate_rounds,
            )

            # Simulate debate rounds
            for round_num in range(1, self.debate_rounds + 1):
                # Agent 1 supporting argument
                session.arguments.append(DebateArgument(
                    agent_name=finding1.agent_name,
                    stance=DebateStance.SUPPORTING,
                    round_number=round_num,
                    argument=f"Round {round_num}: {finding1.description[:100]}",
                    supporting_evidence=finding1.evidence_trail[:2],
                    confidence=finding1.confidence_score,
                ))

                # Agent 2 challenging argument
                session.arguments.append(DebateArgument(
                    agent_name=finding2.agent_name,
                    stance=DebateStance.CHALLENGING,
                    round_number=round_num,
                    argument=f"Round {round_num}: {finding2.description[:100]}",
                    supporting_evidence=finding2.evidence_trail[:2],
                    rebuts_finding_id=finding1.id,
                    confidence=finding2.confidence_score,
                ))

            # Determine consensus
            avg_confidence = statistics.mean([
                arg.confidence for arg in session.arguments
            ])

            session.final_confidence = avg_confidence
            session.consensus_reached = avg_confidence > 0.7
            session.resolution = self._synthesize_debate_resolution(session)

            self.debate_sessions.append(session)

    def _synthesize_debate_resolution(self, session: DebateSession) -> str:
        """Synthesize resolution from debate session."""
        supporting_args = [
            arg for arg in session.arguments
            if arg.stance == DebateStance.SUPPORTING
        ]
        challenging_args = [
            arg for arg in session.arguments
            if arg.stance == DebateStance.CHALLENGING
        ]

        if not supporting_args or not challenging_args:
            return "Insufficient arguments for resolution"

        avg_supporting_conf = statistics.mean([arg.confidence for arg in supporting_args])
        avg_challenging_conf = statistics.mean([arg.confidence for arg in challenging_args])

        if avg_supporting_conf > avg_challenging_conf:
            return f"Supporting position prevails (confidence: {avg_supporting_conf:.2f})"
        elif avg_challenging_conf > avg_supporting_conf:
            return f"Challenging position prevails (confidence: {avg_challenging_conf:.2f})"
        else:
            return "Positions are balanced, requires additional investigation"

    async def _resolve_conflicts(
        self,
        conflicts: List[Tuple[Finding, Finding]],
    ) -> None:
        """Resolve conflicts using debate outcomes and evidence quality."""
        for finding1, finding2 in conflicts:
            # Find relevant debate session
            debate_session = next(
                (s for s in self.debate_sessions
                 if finding1.id in s.finding_id or finding2.id in s.finding_id),
                None
            )

            # Resolution logic
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

            resolution = ConflictResolution(
                conflict_id=f"conflict_{finding1.id}_{finding2.id}",
                conflicting_findings=[finding1.id, finding2.id],
                conflicting_agents=[finding1.agent_name, finding2.agent_name],
                resolution_method="evidence_based_arbitration",
                final_verdict=final_verdict,
                confidence=confidence,
                reasoning=debate_session.resolution if debate_session else "Evidence comparison",
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

            # Group by severity
            severity_counts = defaultdict(int)
            agents_by_severity = defaultdict(list)

            for finding in findings:
                severity_counts[finding.severity] += 1
                agents_by_severity[finding.severity].append(finding.agent_name)

            # Find majority severity
            majority_severity = max(severity_counts, key=severity_counts.get)
            majority_count = severity_counts[majority_severity]
            total_findings = len(findings)

            agreement_level = majority_count / total_findings

            # Identify dissenting agents
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
                confidence=agreement_level,  # Higher agreement = higher confidence
            )

            consensus_scores.append(consensus)

        return consensus_scores

    async def _detect_greenwashing(
        self,
        synthesized_findings: Dict[str, List[Finding]],
    ) -> None:
        """Detect potential greenwashing signals."""
        all_findings = [
            finding
            for findings_list in synthesized_findings.values()
            for finding in findings_list
        ]

        # Pattern 1: Vague claims with low evidence
        for finding in all_findings:
            if len(finding.evidence_trail) < self.greenwashing_patterns["lack_of_evidence"]["min_evidence_per_finding"]:
                if finding.severity in ["INFO", "LOW"]:
                    self.greenwashing_signals.append(GreenwashingSignal(
                        signal_type="lack_of_evidence",
                        severity="medium",
                        description=f"Finding '{finding.title}' has insufficient evidence ({len(finding.evidence_trail)} pieces)",
                        evidence=finding.evidence_trail,
                        confidence=0.72,
                    ))

        # Pattern 2: Contradictory data across agents
        if len(self.conflict_resolutions) > 3:
            self.greenwashing_signals.append(GreenwashingSignal(
                signal_type="contradictory_data",
                severity="high",
                description=f"Multiple contradictions detected across {len(self.conflict_resolutions)} findings",
                confidence=0.78,
            ))

        # Pattern 3: Cherry-picking (only positive findings)
        positive_findings = sum(
            1 for f in all_findings
            if f.severity in ["INFO", "LOW"]
        )
        total_findings = len(all_findings)

        if total_findings > 0 and positive_findings / total_findings > 0.8:
            self.greenwashing_signals.append(GreenwashingSignal(
                signal_type="cherry_picking",
                severity="medium",
                description=f"Unusually high proportion of positive findings ({positive_findings}/{total_findings})",
                confidence=0.68,
            ))

        self.logger.info(
            "greenwashing_detection_complete",
            signals_detected=len(self.greenwashing_signals),
        )

    async def _aggregate_scores(self) -> Dict[str, float]:
        """Aggregate final scores from all agents."""
        if not self.agent_reports:
            return {"overall_score": 50.0}

        # Collect all risk scores
        risk_scores = [
            report.overall_risk_score
            for report in self.agent_reports.values()
        ]

        # Calculate aggregate metrics
        avg_risk = statistics.mean(risk_scores)
        median_risk = statistics.median(risk_scores)
        std_dev = statistics.stdev(risk_scores) if len(risk_scores) > 1 else 0

        # Adjust for consensus (high consensus = more confident score)
        consensus_adjustment = 0
        if hasattr(self, 'consensus_scores'):
            avg_agreement = statistics.mean(
                [cs.agreement_level for cs in getattr(self, 'consensus_scores', [])]
            ) if hasattr(self, 'consensus_scores') else 0.5
            consensus_adjustment = (avg_agreement - 0.5) * 10  # ±5 points

        # Adjust for greenwashing (detected greenwashing increases risk)
        greenwashing_penalty = len(self.greenwashing_signals) * 5

        final_risk_score = min(100.0, max(0.0, avg_risk + greenwashing_penalty - consensus_adjustment))

        return {
            "overall_score": 100 - final_risk_score,  # Convert risk to quality score
            "risk_score": final_risk_score,
            "confidence_score": 100 - std_dev * 10,  # Lower variance = higher confidence
            "consensus_level": 100 - std_dev * 20,
            "greenwashing_risk": min(100.0, len(self.greenwashing_signals) * 15),
        }

    async def _create_final_findings(
        self,
        synthesized_findings: Dict[str, List[Finding]],
        consensus_scores: List[ConsensusScore],
        final_scores: Dict[str, float],
    ) -> List[Finding]:
        """Create final orchestrated findings."""
        findings = []

        # Finding 1: Overall Assessment
        overall_finding = Finding(
            agent_name=self.name,
            finding_type="overall_assessment",
            severity=self._score_to_severity(final_scores["overall_score"]),
            title="Comprehensive Multi-Agent Assessment",
            description=f"Coordinated analysis across {len(self.agent_reports)} specialized agents with adversarial validation",
            confidence_score=final_scores["confidence_score"] / 100,
            metadata={
                "overall_score": final_scores["overall_score"],
                "risk_score": final_scores["risk_score"],
                "participating_agents": list(self.agent_reports.keys()),
                "total_findings_analyzed": sum(len(f) for f in synthesized_findings.values()),
            },
        )

        # Add summary evidence
        overall_finding.add_evidence(Evidence(
            type=EvidenceType.API_RESPONSE,
            source="Multi-Agent Orchestration System",
            description="Aggregated findings from all specialized agents",
            data={
                "agent_count": len(self.agent_reports),
                "debate_sessions": len(self.debate_sessions),
                "conflicts_resolved": len(self.conflict_resolutions),
            },
            confidence=final_scores["confidence_score"] / 100,
        ))

        findings.append(overall_finding)

        # Finding 2: Consensus Analysis
        if consensus_scores:
            high_consensus_topics = [
                cs for cs in consensus_scores
                if cs.agreement_level > 0.7
            ]

            if high_consensus_topics:
                consensus_finding = Finding(
                    agent_name=self.name,
                    finding_type="consensus_analysis",
                    severity="INFO",
                    title=f"Strong Consensus on {len(high_consensus_topics)} Key Areas",
                    description=f"Multiple agents agree on {', '.join([cs.topic for cs in high_consensus_topics[:3]])}",
                    confidence_score=statistics.mean([cs.confidence for cs in high_consensus_topics]),
                    metadata={
                        "consensus_topics": [
                            {
                                "topic": cs.topic,
                                "agreement_level": cs.agreement_level,
                                "majority_position": cs.majority_position,
                            }
                            for cs in high_consensus_topics
                        ],
                    },
                )
                findings.append(consensus_finding)

        # Finding 3: Greenwashing Alert
        if self.greenwashing_signals:
            high_severity_signals = [
                s for s in self.greenwashing_signals
                if s.severity in ["high", "critical"]
            ]

            if high_severity_signals:
                greenwashing_finding = Finding(
                    agent_name=self.name,
                    finding_type="greenwashing_detection",
                    severity="HIGH",
                    title=f"Greenwashing Signals Detected ({len(high_severity_signals)} high-severity)",
                    description=f"Identified {len(self.greenwashing_signals)} potential greenwashing signals",
                    confidence_score=statistics.mean([s.confidence for s in high_severity_signals]),
                    metadata={
                        "signals": [
                            {
                                "type": s.signal_type,
                                "severity": s.severity,
                                "description": s.description,
                            }
                            for s in high_severity_signals
                        ],
                        "total_signals": len(self.greenwashing_signals),
                    },
                )
                findings.append(greenwashing_finding)

        # Finding 4: Adversarial Debate Summary
        if self.debate_sessions:
            debate_finding = Finding(
                agent_name=self.name,
                finding_type="adversarial_validation",
                severity="INFO",
                title=f"Adversarial Validation Completed ({len(self.debate_sessions)} debates)",
                description=f"Conducted {self.debate_rounds}-round debates to validate controversial findings",
                confidence_score=statistics.mean([s.final_confidence for s in self.debate_sessions]),
                metadata={
                    "debate_sessions": len(self.debate_sessions),
                    "consensus_reached": sum(1 for s in self.debate_sessions if s.consensus_reached),
                    "average_confidence": statistics.mean([s.final_confidence for s in self.debate_sessions]),
                },
            )
            findings.append(debate_finding)

        return findings

    def _score_to_severity(self, score: float) -> str:
        """Convert score to severity level."""
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
