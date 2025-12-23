"""
GAIA Agent System
Exports all specialized AI agents for the Global AI-powered Impact Assessment system.
"""

from .base_agent import (
    BaseAgent,
    AgentReport,
    Finding,
    Evidence,
    EvidenceType,
    ConfidenceLevel,
)

from .sentinel_agent import SentinelAgent
from .veritas_agent import VeritasAgent
from .pulse_agent import PulseAgent

# Import other agents if they exist
try:
    from .regulus_agent import RegulusAgent
    REGULUS_AVAILABLE = True
except ImportError:
    REGULUS_AVAILABLE = False

try:
    from .impact_agent import ImpactAgent
    IMPACT_AVAILABLE = True
except ImportError:
    IMPACT_AVAILABLE = False

try:
    from .orchestrator_agent import OrchestratorAgent
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False

try:
    from .nexus_agent import NexusAgent
    NEXUS_AVAILABLE = True
except ImportError:
    NEXUS_AVAILABLE = False


__all__ = [
    # Base classes
    "BaseAgent",
    "AgentReport",
    "Finding",
    "Evidence",
    "EvidenceType",
    "ConfidenceLevel",

    # Core specialized agents
    "SentinelAgent",
    "VeritasAgent",
    "PulseAgent",
]

# Add optional agents to exports if available
if REGULUS_AVAILABLE:
    __all__.append("RegulusAgent")
if IMPACT_AVAILABLE:
    __all__.append("ImpactAgent")
if ORCHESTRATOR_AVAILABLE:
    __all__.append("OrchestratorAgent")
if NEXUS_AVAILABLE:
    __all__.append("NexusAgent")


# Agent registry for easy instantiation
AGENT_REGISTRY = {
    "sentinel": SentinelAgent,
    "veritas": VeritasAgent,
    "pulse": PulseAgent,
}

# Add optional agents to registry if available
if REGULUS_AVAILABLE:
    AGENT_REGISTRY["regulus"] = RegulusAgent
if IMPACT_AVAILABLE:
    AGENT_REGISTRY["impact"] = ImpactAgent
if ORCHESTRATOR_AVAILABLE:
    AGENT_REGISTRY["orchestrator"] = OrchestratorAgent
if NEXUS_AVAILABLE:
    AGENT_REGISTRY["nexus"] = NexusAgent


def get_agent(agent_type: str, **kwargs):
    """
    Factory function to instantiate agents by type.

    Args:
        agent_type: Type of agent to create (regulus, impact, orchestrator)
        **kwargs: Additional arguments to pass to agent constructor

    Returns:
        Instantiated agent

    Raises:
        ValueError: If agent_type is not recognized

    Example:
        >>> regulus = get_agent("regulus", timeout_seconds=120)
        >>> impact = get_agent("impact", enable_debug=True)
    """
    if agent_type not in AGENT_REGISTRY:
        available = ", ".join(AGENT_REGISTRY.keys())
        raise ValueError(
            f"Unknown agent type: {agent_type}. "
            f"Available types: {available}"
        )

    agent_class = AGENT_REGISTRY[agent_type]
    return agent_class(**kwargs)


def get_all_agents(**kwargs):
    """
    Get instances of all available agents.

    Args:
        **kwargs: Arguments to pass to all agent constructors

    Returns:
        Dictionary mapping agent type to agent instance

    Example:
        >>> agents = get_all_agents(timeout_seconds=90)
        >>> regulus_report = await agents["regulus"].analyze("Company XYZ")
    """
    return {
        agent_type: agent_class(**kwargs)
        for agent_type, agent_class in AGENT_REGISTRY.items()
    }
