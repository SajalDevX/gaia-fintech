"""
GAIA Analysis Service
Core service for orchestrating multi-agent ESG/SDG analysis with real AI agents.
Uses multi-provider LLM (Gemini, OpenAI, Claude) for load-balanced AI reasoning.
"""

import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import structlog

from config import get_settings, SDG_GOALS, RISK_LEVELS

# Import real AI agents
from agents.sentinel_agent import SentinelAgent
# Import blockchain for audit trail
from utils.blockchain import (
    get_blockchain,
    record_agent_finding,
    record_debate_argument,
    record_greenwashing_alert,
    record_consensus,
    finalize_assessment,
    get_audit_trail
)
from agents.veritas_agent import VeritasAgent
from agents.pulse_agent import PulseAgent
from agents.regulus_agent import RegulusAgent
from agents.impact_agent import ImpactAgent
from agents.nexus_agent import NexusAgent
from agents.orchestrator_agent import OrchestratorAgent
from utils.llm_client import get_multi_llm_client

logger = structlog.get_logger()
settings = get_settings()


class AnalysisService:
    """
    Core analysis service using real AI agents:
    1. Sentinel Agent - Environmental monitoring
    2. Veritas Agent - Supply chain verification
    3. Pulse Agent - News sentiment analysis
    4. Regulus Agent - Regulatory compliance
    5. Impact Agent - SDG impact quantification
    6. NEXUS Agent - Financial inclusion
    7. Orchestrator Agent - Adversarial debate & synthesis

    All agents use multi-provider LLM (Gemini, OpenAI, Claude) with load balancing.
    """

    def __init__(self):
        """Initialize the analysis service with real AI agents."""
        self.active_analyses: Dict[str, Dict[str, Any]] = {}
        self.completed_analyses: Dict[str, Dict[str, Any]] = {}

        # Initialize multi-provider LLM client
        self.llm_client = get_multi_llm_client()

        # Initialize real AI agents
        self.agents = self._initialize_agents()

    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize real AI agents with shared LLM client."""
        return {
            "sentinel": SentinelAgent(llm_client=self.llm_client),
            "veritas": VeritasAgent(llm_client=self.llm_client),
            "pulse": PulseAgent(llm_client=self.llm_client),
            "regulus": RegulusAgent(llm_client=self.llm_client),
            "impact": ImpactAgent(llm_client=self.llm_client),
            "nexus": NexusAgent(llm_client=self.llm_client),
            "orchestrator": OrchestratorAgent(llm_client=self.llm_client),
        }

    async def run_analysis(
        self,
        analysis_id: str,
        ticker: str,
        company_name: Optional[str] = None,
        include_satellite: bool = True,
        include_sentiment: bool = True,
        include_supply_chain: bool = True,
        debate_rounds: int = 3,
        connection_manager=None
    ) -> Dict[str, Any]:
        """
        Run complete multi-agent analysis with real AI and adversarial debate.

        Uses real LLM calls via Gemini, OpenAI, and Claude with load balancing.
        """
        start_time = datetime.utcnow()

        try:
            logger.info("starting_real_ai_analysis", analysis_id=analysis_id, ticker=ticker)

            # Initialize analysis state
            self.active_analyses[analysis_id] = {
                "id": analysis_id,
                "ticker": ticker,
                "company_name": company_name or ticker,
                "status": "initializing",
                "progress": 0.0,
                "current_stage": "initialization",
                "completed_agents": [],
                "pending_agents": ["sentinel", "veritas", "pulse", "regulus", "impact", "nexus"],
                "results": {},
                "created_at": start_time,
                "updated_at": start_time
            }

            # Send initial WebSocket update
            if connection_manager:
                await connection_manager.send_message(analysis_id, {
                    "type": "status",
                    "status": "started",
                    "progress": 0.0,
                    "message": f"Starting real AI analysis for {ticker}",
                    "timestamp": start_time.isoformat()
                })

            # Phase 1: Run all AI agents in parallel
            agent_results = await self._run_agents(
                analysis_id, ticker, company_name,
                include_sentiment, include_supply_chain,
                connection_manager
            )

            # Phase 2: Run Orchestrator with real LLM adversarial debate
            orchestrator_result = await self._run_orchestrator(
                analysis_id, ticker, agent_results, debate_rounds, connection_manager
            )

            # Phase 3: Generate Final Assessment
            final_assessment = await self._generate_final_assessment(
                analysis_id, ticker, company_name,
                agent_results, orchestrator_result, connection_manager
            )

            # Mark as completed
            end_time = datetime.utcnow()
            processing_time = (end_time - start_time).total_seconds()

            # Finalize on blockchain
            blockchain_result = finalize_assessment(
                company_ticker=ticker,
                assessment_data={
                    "overall_score": final_assessment.get("overall_score"),
                    "risk_level": final_assessment.get("risk_level"),
                    "agents_completed": list(agent_results.keys()),
                    "greenwashing_risk": final_assessment.get("greenwashing_risk", 0)
                }
            )

            final_results = {
                "analysis_id": analysis_id,
                "ticker": ticker,
                "company_name": company_name or ticker,
                "status": "completed",
                "progress": 100.0,
                "ai_powered": True,
                "llm_providers": ["gemini", "openai", "claude"],
                **final_assessment,
                "agent_results": agent_results,
                "orchestrator_summary": orchestrator_result,
                "blockchain": blockchain_result,
                "audit_trail": get_audit_trail(ticker),
                "created_at": start_time,
                "completed_at": end_time,
                "processing_time": processing_time
            }

            # Move to completed analyses
            self.completed_analyses[analysis_id] = final_results
            del self.active_analyses[analysis_id]

            # Send final WebSocket update
            if connection_manager:
                await connection_manager.send_message(analysis_id, {
                    "type": "completed",
                    "status": "completed",
                    "progress": 100.0,
                    "results": final_results,
                    "message": f"AI analysis completed for {ticker}",
                    "timestamp": end_time.isoformat()
                })

            logger.info(
                "real_ai_analysis_completed",
                analysis_id=analysis_id,
                ticker=ticker,
                processing_time=processing_time
            )

            return final_results

        except Exception as e:
            logger.error("analysis_failed", analysis_id=analysis_id, error=str(e), exc_info=True)

            if analysis_id in self.active_analyses:
                self.active_analyses[analysis_id].update({
                    "status": "failed",
                    "error": str(e),
                    "updated_at": datetime.utcnow()
                })

            if connection_manager:
                await connection_manager.send_message(analysis_id, {
                    "type": "error",
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })

            raise

    async def _run_agents(
        self,
        analysis_id: str,
        ticker: str,
        company_name: Optional[str],
        include_sentiment: bool,
        include_supply_chain: bool,
        connection_manager
    ) -> Dict[str, Any]:
        """Run all real AI agents in parallel."""
        logger.info("running_real_ai_agents", analysis_id=analysis_id)

        self.active_analyses[analysis_id].update({
            "status": "running_agents",
            "current_stage": "multi-agent AI analysis",
            "progress": 10.0,
            "updated_at": datetime.utcnow()
        })

        if connection_manager:
            await connection_manager.send_message(analysis_id, {
                "type": "stage",
                "stage": "agents",
                "progress": 10.0,
                "message": "Running multi-agent AI analysis with load-balanced LLMs",
                "timestamp": datetime.utcnow().isoformat()
            })

        context = {"ticker": ticker, "company_name": company_name, "industry": "Unknown"}

        # Run real AI agents in parallel
        tasks = [
            self._run_agent("sentinel", ticker, context, "Environmental", 20.0, connection_manager, analysis_id),
            self._run_agent("regulus", ticker, context, "Regulatory", 30.0, connection_manager, analysis_id),
            self._run_agent("impact", ticker, context, "SDG Impact", 40.0, connection_manager, analysis_id),
        ]

        if include_sentiment:
            tasks.append(self._run_agent("pulse", ticker, context, "Sentiment", 50.0, connection_manager, analysis_id))

        if include_supply_chain:
            tasks.append(self._run_agent("veritas", ticker, context, "Supply Chain", 60.0, connection_manager, analysis_id))
            tasks.append(self._run_agent("nexus", ticker, context, "Financial Inclusion", 65.0, connection_manager, analysis_id))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        agent_results = {}
        for result in results:
            if isinstance(result, Exception):
                logger.error("agent_error", error=str(result))
            elif isinstance(result, dict):
                agent_results.update(result)

        return agent_results

    async def _run_agent(
        self,
        agent_name: str,
        ticker: str,
        context: Dict[str, Any],
        display_name: str,
        progress: float,
        connection_manager,
        analysis_id: str
    ) -> Dict[str, Any]:
        """Run a single real AI agent."""
        try:
            logger.info(f"running_{agent_name}_agent", ticker=ticker)

            # Notify frontend that agent is starting
            if connection_manager:
                await connection_manager.send_message(analysis_id, {
                    "type": "agent_start",
                    "agent_id": agent_name,
                    "agent": display_name,
                    "task": f"Analyzing {display_name.lower()} factors...",
                    "timestamp": datetime.utcnow().isoformat()
                })

            agent = self.agents[agent_name]
            report = await agent.analyze(target_entity=ticker, context=context)

            # Convert report to dict
            result = {
                agent_name: {
                    "agent": display_name,
                    "status": "completed",
                    "score": 100 - report.overall_risk_score,
                    "findings": [
                        {
                            "title": f.title,
                            "description": f.description,
                            "severity": f.severity,
                            "confidence": f.confidence_score
                        }
                        for f in report.findings
                    ],
                    "finding_count": len(report.findings),
                    "errors": report.errors,
                    "metadata": report.metadata,
                    "completed_at": datetime.utcnow().isoformat()
                }
            }

            # Record findings to blockchain
            for finding in report.findings:
                record_agent_finding(
                    agent_id=agent_name,
                    company_ticker=ticker,
                    finding_type=finding.finding_type,
                    finding_data={"title": finding.title, "description": finding.description},
                    confidence=finding.confidence_score,
                    severity=finding.severity
                )

            # Update progress
            await self._update_agent_progress(analysis_id, agent_name, progress, connection_manager)

            return result

        except Exception as e:
            logger.error(f"{agent_name}_agent_error", error=str(e))
            return {agent_name: {"status": "error", "error": str(e)}}

    async def _run_orchestrator(
        self,
        analysis_id: str,
        ticker: str,
        agent_results: Dict[str, Any],
        debate_rounds: int,
        connection_manager
    ) -> Dict[str, Any]:
        """Run the Orchestrator with real LLM-powered adversarial debate."""
        logger.info("running_real_orchestrator", analysis_id=analysis_id, rounds=debate_rounds)

        self.active_analyses[analysis_id].update({
            "status": "adversarial_debate",
            "current_stage": f"LLM adversarial debate",
            "progress": 70.0,
            "updated_at": datetime.utcnow()
        })

        if connection_manager:
            # Notify orchestrator is starting
            await connection_manager.send_message(analysis_id, {
                "type": "agent_start",
                "agent_id": "orchestrator",
                "agent": "Orchestrator",
                "task": "Running adversarial debate...",
                "timestamp": datetime.utcnow().isoformat()
            })
            await connection_manager.send_message(analysis_id, {
                "type": "stage",
                "stage": "debate",
                "progress": 70.0,
                "message": f"Running LLM-powered adversarial debate ({debate_rounds} rounds)",
                "timestamp": datetime.utcnow().isoformat()
            })

        try:
            # Prepare agent reports for orchestrator
            from agents.base_agent import AgentReport, Finding
            agent_reports = {}
            for name, data in agent_results.items():
                if isinstance(data, dict) and data.get("status") == "completed":
                    # Create report with findings for orchestrator
                    report = AgentReport(
                        agent_name=name,
                        agent_type=name,
                        target_entity=ticker
                    )
                    report.overall_risk_score = 100 - data.get("score", 50)

                    # Add findings to the report (crucial for debate)
                    for finding_data in data.get("findings", []):
                        finding = Finding(
                            agent_name=name,
                            finding_type=finding_data.get("title", "unknown").lower().replace(" ", "_")[:50],
                            title=finding_data.get("title", "Unknown Finding"),
                            description=finding_data.get("description", ""),
                            severity=finding_data.get("severity", "INFO"),
                            confidence_score=finding_data.get("confidence", 0.5)
                        )
                        report.add_finding(finding)

                    agent_reports[name] = report
                    logger.info(f"orchestrator_agent_report", agent=name, findings_count=len(report.findings))

            # Run orchestrator with real LLM debate
            orchestrator = self.agents["orchestrator"]
            orchestrator.debate_rounds = debate_rounds

            context = {"agent_reports": agent_reports}
            orch_report = await orchestrator.analyze(target_entity=ticker, context=context)

            # Update progress during debate
            if connection_manager:
                # Send debate updates for each round
                for i, session in enumerate(orchestrator.debate_sessions):
                    await connection_manager.send_message(analysis_id, {
                        "type": "debate_update",
                        "round": i + 1,
                        "total_rounds": len(orchestrator.debate_sessions),
                        "topic": session.topic or "Conflict Resolution",
                        "timestamp": datetime.utcnow().isoformat()
                    })

                await connection_manager.send_message(analysis_id, {
                    "type": "debate_complete",
                    "progress": 85.0,
                    "debates": len(orchestrator.debate_sessions),
                    "greenwashing_signals": len(orchestrator.greenwashing_signals),
                    "timestamp": datetime.utcnow().isoformat()
                })

                # Mark orchestrator as complete
                await connection_manager.send_message(analysis_id, {
                    "type": "agent_complete",
                    "agent_id": "orchestrator",
                    "agent": "Orchestrator",
                    "progress": 90.0,
                    "completed_agents": list(agent_results.keys()) + ["orchestrator"],
                    "pending_agents": [],
                    "findings": [f"Resolved {len(orchestrator.conflict_resolutions)} conflicts"],
                    "timestamp": datetime.utcnow().isoformat()
                })

            # Record debates to blockchain
            for session in orchestrator.debate_sessions:
                for arg in session.arguments:
                    record_debate_argument(
                        agent_id=arg.agent_name,
                        company_ticker=ticker,
                        debate_round=arg.round_number,
                        stance=arg.stance.value,
                        argument=arg.argument[:200],
                        confidence=arg.confidence
                    )

            # Record greenwashing alerts
            for signal in orchestrator.greenwashing_signals:
                if signal.severity in ["high", "critical"]:
                    record_greenwashing_alert(
                        company_ticker=ticker,
                        alert_data={
                            "signal_type": signal.signal_type,
                            "description": signal.description
                        },
                        severity=signal.severity.upper()
                    )

            # Record consensus
            if orch_report.findings:
                record_consensus(
                    company_ticker=ticker,
                    consensus_data={
                        "debates_completed": len(orchestrator.debate_sessions),
                        "conflicts_resolved": len(orchestrator.conflict_resolutions)
                    },
                    participating_agents=list(agent_results.keys())
                )

            # Serialize debate sessions for frontend
            debate_sessions = []
            for session in orchestrator.debate_sessions:
                debate_sessions.append({
                    "topic": session.topic,
                    "rounds": session.rounds,
                    "consensus_reached": session.consensus_reached,
                    "final_confidence": session.final_confidence,
                    "resolution": session.resolution,
                    "arguments": [
                        {
                            "agent_name": arg.agent_name,
                            "stance": arg.stance.value if hasattr(arg.stance, 'value') else str(arg.stance),
                            "round": arg.round_number,
                            "argument": arg.argument,
                            "confidence": arg.confidence,
                            "evidence": [str(e) for e in arg.supporting_evidence[:2]] if arg.supporting_evidence else []
                        }
                        for arg in session.arguments
                    ]
                })

            # Serialize greenwashing signals for frontend
            greenwashing_signals = [
                {
                    "signal_type": signal.signal_type,
                    "severity": signal.severity,
                    "description": signal.description,
                    "confidence": signal.confidence,
                    "indicators": [str(e) for e in signal.evidence[:3]] if signal.evidence else []
                }
                for signal in orchestrator.greenwashing_signals
            ]

            return {
                "status": "completed",
                "total_debates": len(orchestrator.debate_sessions),
                "conflicts_resolved": len(orchestrator.conflict_resolutions),
                "greenwashing_signals_count": len(orchestrator.greenwashing_signals),
                "debate_sessions": debate_sessions,
                "greenwashing_signals": greenwashing_signals,
                "findings": [
                    {"title": f.title, "description": f.description, "severity": f.severity}
                    for f in orch_report.findings
                ],
                "metadata": orch_report.metadata,
                "completed_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error("orchestrator_error", error=str(e))
            return {"status": "error", "error": str(e)}

    async def _generate_final_assessment(
        self,
        analysis_id: str,
        ticker: str,
        company_name: Optional[str],
        agent_results: Dict[str, Any],
        orchestrator_result: Dict[str, Any],
        connection_manager
    ) -> Dict[str, Any]:
        """Generate final ESG/SDG assessment with AI synthesis."""
        logger.info("generating_ai_final_assessment", analysis_id=analysis_id)

        self.active_analyses[analysis_id].update({
            "status": "final_assessment",
            "current_stage": "AI synthesis",
            "progress": 90.0,
            "updated_at": datetime.utcnow()
        })

        if connection_manager:
            await connection_manager.send_message(analysis_id, {
                "type": "stage",
                "stage": "assessment",
                "progress": 90.0,
                "message": "Generating AI-synthesized final assessment",
                "timestamp": datetime.utcnow().isoformat()
            })

        # Calculate scores from agent results
        scores = []
        for name, data in agent_results.items():
            if isinstance(data, dict) and "score" in data:
                scores.append(data["score"])

        overall_score = sum(scores) / len(scores) if scores else 50.0

        # Adjust for greenwashing
        greenwashing_signals = orchestrator_result.get("greenwashing_signals", [])
        greenwashing_count = len(greenwashing_signals) if isinstance(greenwashing_signals, list) else greenwashing_signals
        if greenwashing_count > 2:
            overall_score -= greenwashing_count * 3

        overall_score = max(0, min(100, overall_score))

        # Determine risk level
        risk_level = self._calculate_risk_level(overall_score)

        # Extract findings for SWOT
        all_findings = []
        for name, data in agent_results.items():
            if isinstance(data, dict) and "findings" in data:
                all_findings.extend(data["findings"])

        swot = self._generate_swot_from_findings(all_findings)

        return {
            "overall_score": round(overall_score, 2),
            "risk_level": risk_level,
            "recommendation": RISK_LEVELS.get(risk_level, {}).get("action", "Monitor"),
            "ai_synthesis": True,
            "esg_scores": {
                "environmental": agent_results.get("sentinel", {}).get("score", 50),
                "social": agent_results.get("nexus", {}).get("score", 50),
                "governance": agent_results.get("regulus", {}).get("score", 50),
                "overall": round(overall_score, 2)
            },
            "greenwashing_risk": min(100, greenwashing_count * 15),
            "strengths": swot["strengths"],
            "weaknesses": swot["weaknesses"],
            "opportunities": swot["opportunities"],
            "threats": swot["threats"]
        }

    def _calculate_risk_level(self, score: float) -> str:
        """Calculate risk level from overall score."""
        if score >= 80:
            return "LOW"
        elif score >= 60:
            return "MODERATE"
        elif score >= 40:
            return "ELEVATED"
        elif score >= 20:
            return "HIGH"
        else:
            return "CRITICAL"

    def _generate_swot_from_findings(self, findings: List[Dict]) -> Dict[str, List[str]]:
        """Generate SWOT from AI findings."""
        strengths = []
        weaknesses = []
        threats = []

        for f in findings[:15]:
            severity = f.get("severity", "INFO")
            desc = f.get("description", "")[:150]

            if severity in ["LOW", "INFO"]:
                strengths.append(desc)
            elif severity == "MEDIUM":
                weaknesses.append(desc)
            else:
                threats.append(desc)

        opportunities = [
            "Leverage AI-identified strengths for ESG improvement",
            "Address identified weaknesses proactively",
            "Enhance sustainability reporting transparency"
        ]

        return {
            "strengths": strengths[:5],
            "weaknesses": weaknesses[:5],
            "opportunities": opportunities[:5],
            "threats": threats[:5]
        }

    async def _update_agent_progress(
        self,
        analysis_id: str,
        agent_name: str,
        progress: float,
        connection_manager
    ):
        """Update analysis progress after agent completion."""
        if analysis_id in self.active_analyses:
            state = self.active_analyses[analysis_id]
            if agent_name not in state["completed_agents"]:
                state["completed_agents"].append(agent_name)
            if agent_name in state["pending_agents"]:
                state["pending_agents"].remove(agent_name)
            state["progress"] = progress
            state["updated_at"] = datetime.utcnow()

            if connection_manager:
                await connection_manager.send_message(analysis_id, {
                    "type": "agent_complete",
                    "agent_id": agent_name,
                    "agent": agent_name,
                    "progress": progress,
                    "completed_agents": state["completed_agents"],
                    "pending_agents": state["pending_agents"],
                    "findings": [],  # Can be populated with finding summaries
                    "timestamp": datetime.utcnow().isoformat()
                })

    async def get_analysis_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an analysis."""
        now = datetime.utcnow()

        if analysis_id in self.active_analyses:
            state = self.active_analyses[analysis_id]
            return {
                "analysis_id": analysis_id,
                "status": state.get("status", "in_progress"),
                "progress": state.get("progress", 0),
                "current_stage": state.get("current_stage", "analyzing"),
                "completed_agents": state.get("completed_agents", []),
                "pending_agents": state.get("pending_agents", []),
                "created_at": state.get("created_at", now),
                "updated_at": state.get("updated_at", now)
            }
        elif analysis_id in self.completed_analyses:
            results = self.completed_analyses[analysis_id]
            completed_at = results.get("completed_at", now.isoformat())
            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "progress": 100.0,
                "current_stage": "completed",
                "completed_agents": ["sentinel", "veritas", "pulse", "regulus", "impact", "nexus", "orchestrator"],
                "pending_agents": [],
                "results": results,
                "created_at": now,
                "updated_at": now,
                "completed_at": now
            }
        return None

    async def get_analysis_results(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get complete results of a completed analysis."""
        return self.completed_analyses.get(analysis_id)

    async def cancel_analysis(self, analysis_id: str) -> bool:
        """Cancel an ongoing analysis."""
        if analysis_id in self.active_analyses:
            del self.active_analyses[analysis_id]
            return True
        return False

    # Placeholder methods for companies and SDG endpoints
    async def list_companies(self, **kwargs) -> Tuple[List[Dict], int]:
        return [], 0

    async def get_company_details(self, ticker: str, **kwargs) -> Optional[Dict]:
        return None

    async def search_companies(self, query: str, **kwargs) -> List[Dict]:
        return []

    async def get_company_timeline(self, ticker: str, **kwargs) -> Optional[Dict]:
        return None

    async def compare_companies(self, ticker: str, compare_with: List[str], **kwargs) -> Dict:
        return {}

    async def get_company_peers(self, ticker: str, **kwargs) -> List[Dict]:
        return []

    async def delete_company(self, ticker: str) -> bool:
        return False

    async def get_satellite_data(self, ticker: str, **kwargs) -> Optional[Dict]:
        return None

    async def get_sdg_impact(self, ticker: str, **kwargs) -> Optional[Dict]:
        return None

    async def analyze_portfolio_sdg(self, tickers: List[str], weights: Dict) -> Dict:
        return {}

    async def get_sdg_goal_detail(self, ticker: str, sdg_number: int) -> Optional[Dict]:
        return None

    async def get_sdg_timeline(self, ticker: str, **kwargs) -> Optional[Dict]:
        return None

    async def get_sector_sdg_impact(self, sector: str, **kwargs) -> Optional[Dict]:
        return None

    async def get_sdg_benchmarks(self, **kwargs) -> Dict:
        return {}

    async def get_sdg_recommendations(self, ticker: str) -> Optional[Dict]:
        return None

    async def compare_sdg_impacts(self, tickers: List[str], **kwargs) -> Dict:
        return {}


# Singleton for dependency injection
_analysis_service = None


def get_analysis_service() -> AnalysisService:
    """Get or create analysis service instance (singleton)."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service
