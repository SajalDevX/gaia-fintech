"""
Multi-Agent Communication and Consensus Models
GAIA - Global AI-powered Impact Assessment System
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class AgentType(str, Enum):
    """Types of AI agents in the system."""
    ENVIRONMENTAL_ANALYST = "environmental_analyst"
    SOCIAL_ANALYST = "social_analyst"
    GOVERNANCE_ANALYST = "governance_analyst"
    SDG_SPECIALIST = "sdg_specialist"
    GREENWASHING_DETECTOR = "greenwashing_detector"
    FINANCIAL_ANALYST = "financial_analyst"
    DATA_VALIDATOR = "data_validator"
    SATELLITE_ANALYST = "satellite_analyst"
    ADVERSARIAL_CRITIC = "adversarial_critic"
    CONSENSUS_COORDINATOR = "consensus_coordinator"


class AgentRole(str, Enum):
    """Role of agent in debate process."""
    PROPOSER = "proposer"
    CHALLENGER = "challenger"
    VALIDATOR = "validator"
    SYNTHESIZER = "synthesizer"
    MODERATOR = "moderator"


class ConfidenceLevel(str, Enum):
    """Confidence levels for agent findings."""
    VERY_HIGH = "very_high"  # 90-100%
    HIGH = "high"  # 70-90%
    MEDIUM = "medium"  # 50-70%
    LOW = "low"  # 30-50%
    VERY_LOW = "very_low"  # 0-30%


class FindingType(str, Enum):
    """Types of findings that agents can report."""
    STRENGTH = "strength"
    WEAKNESS = "weakness"
    RISK = "risk"
    OPPORTUNITY = "opportunity"
    CONCERN = "concern"
    ACHIEVEMENT = "achievement"
    DISCREPANCY = "discrepancy"
    VERIFICATION = "verification"


class ChallengeType(str, Enum):
    """Types of adversarial challenges."""
    DATA_QUALITY = "data_quality"
    METHODOLOGY = "methodology"
    LOGIC = "logic"
    EVIDENCE = "evidence"
    BIAS = "bias"
    ASSUMPTION = "assumption"
    COMPLETENESS = "completeness"
    INTERPRETATION = "interpretation"


class AgentFinding(BaseModel):
    """Individual finding or discovery by an agent."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "finding_id": "ENV-001-TSLA",
            "agent_type": "environmental_analyst",
            "finding_type": "strength",
            "category": "carbon_emissions",
            "title": "Strong Carbon Reduction Performance",
            "description": "Company achieved 35% carbon reduction vs 2020 baseline",
            "evidence": [],
            "confidence_score": 88.5,
            "confidence_level": "high",
            "impact_score": 85.0,
            "relevance_score": 92.0,
            "created_at": "2025-12-23T10:30:00Z"
        }
    })

    # Identification
    finding_id: str = Field(..., description="Unique finding identifier")
    agent_type: AgentType = Field(..., description="Type of agent that made the finding")
    agent_id: Optional[str] = Field(None, description="Specific agent instance ID")

    # Finding Details
    finding_type: FindingType = Field(..., description="Type of finding")
    category: str = Field(..., description="ESG category or subcategory")
    title: str = Field(..., description="Brief title of the finding", max_length=255)
    description: str = Field(..., description="Detailed description of the finding")

    # Evidence
    evidence: List[str] = Field(default_factory=list, description="Supporting evidence for the finding")
    data_sources: List[str] = Field(default_factory=list, description="Data sources used")
    citations: List[str] = Field(default_factory=list, description="Specific citations or references")

    # Confidence and Impact
    confidence_score: float = Field(..., ge=0, le=100, description="Confidence in finding (0-100)")
    confidence_level: ConfidenceLevel = Field(..., description="Confidence level category")
    impact_score: float = Field(..., ge=0, le=100, description="Impact/importance of finding")
    relevance_score: float = Field(..., ge=0, le=100, description="Relevance to overall assessment")

    # Quantitative Data
    quantitative_value: Optional[float] = Field(None, description="Quantitative value if applicable")
    quantitative_unit: Optional[str] = Field(None, description="Unit of measurement")
    baseline_comparison: Optional[float] = Field(None, description="Comparison to baseline or benchmark")

    # Context
    time_period: Optional[str] = Field(None, description="Time period of finding")
    geographic_scope: Optional[str] = Field(None, description="Geographic scope")

    # Implications
    implications: List[str] = Field(default_factory=list, description="Key implications of this finding")
    recommendations: List[str] = Field(default_factory=list, description="Agent recommendations")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Finding creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")

    @field_validator('confidence_score', 'impact_score', 'relevance_score')
    @classmethod
    def validate_scores(cls, v: float) -> float:
        """Validate scores are in valid range."""
        if not 0 <= v <= 100:
            raise ValueError("Scores must be between 0 and 100")
        return round(v, 2)


class AgentChallenge(BaseModel):
    """Adversarial challenge to a finding or claim."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "challenge_id": "CHAL-001-ENV-001",
            "finding_id": "ENV-001-TSLA",
            "challenger_agent_type": "adversarial_critic",
            "challenge_type": "evidence",
            "title": "Question Scope 3 Emissions Completeness",
            "description": "Carbon reduction figures may exclude significant Scope 3 emissions",
            "specific_concerns": ["Incomplete supply chain emissions data"],
            "severity": "medium",
            "confidence_score": 75.0,
            "created_at": "2025-12-23T10:31:00Z"
        }
    })

    # Identification
    challenge_id: str = Field(..., description="Unique challenge identifier")
    finding_id: Optional[str] = Field(None, description="Finding being challenged")
    response_id: Optional[str] = Field(None, description="Response being challenged")

    # Challenger Information
    challenger_agent_type: AgentType = Field(..., description="Type of challenging agent")
    challenger_agent_id: Optional[str] = Field(None, description="Specific challenger agent ID")

    # Challenge Details
    challenge_type: ChallengeType = Field(..., description="Type of challenge")
    title: str = Field(..., description="Brief title of challenge", max_length=255)
    description: str = Field(..., description="Detailed description of the challenge")

    # Specific Concerns
    specific_concerns: List[str] = Field(default_factory=list, description="Specific points of concern")
    questioned_assumptions: List[str] = Field(default_factory=list, description="Assumptions being questioned")
    alternative_interpretations: List[str] = Field(
        default_factory=list,
        description="Alternative interpretations suggested"
    )

    # Supporting Evidence
    counter_evidence: List[str] = Field(default_factory=list, description="Counter-evidence presented")
    alternative_sources: List[str] = Field(default_factory=list, description="Alternative data sources")

    # Severity and Impact
    severity: str = Field(
        ...,
        description="Challenge severity: critical, high, medium, low"
    )
    potential_impact: Optional[str] = Field(
        None,
        description="Potential impact on finding if challenge is valid"
    )

    # Confidence
    confidence_score: float = Field(..., ge=0, le=100, description="Confidence in challenge validity")

    # Resolution
    resolved: bool = Field(default=False, description="Whether challenge has been resolved")
    resolution_status: Optional[str] = Field(
        None,
        description="Resolution status: accepted, rejected, partially_accepted, pending"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Challenge creation timestamp")
    resolved_at: Optional[datetime] = Field(None, description="Resolution timestamp")


class AgentResponse(BaseModel):
    """Response to an adversarial challenge."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "response_id": "RESP-001-CHAL-001",
            "challenge_id": "CHAL-001-ENV-001",
            "finding_id": "ENV-001-TSLA",
            "responder_agent_type": "environmental_analyst",
            "response_type": "defense",
            "description": "Scope 3 emissions are disclosed in separate sustainability report",
            "acknowledgments": ["Agree Scope 3 disclosure could be more prominent"],
            "rebuttals": ["Data is available though not in main report"],
            "revised_confidence_score": 82.0,
            "created_at": "2025-12-23T10:32:00Z"
        }
    })

    # Identification
    response_id: str = Field(..., description="Unique response identifier")
    challenge_id: str = Field(..., description="Challenge being responded to")
    finding_id: Optional[str] = Field(None, description="Original finding ID")

    # Responder Information
    responder_agent_type: AgentType = Field(..., description="Type of responding agent")
    responder_agent_id: Optional[str] = Field(None, description="Specific responder agent ID")

    # Response Details
    response_type: str = Field(
        ...,
        description="Response type: defense, concession, clarification, revision"
    )
    description: str = Field(..., description="Detailed response to the challenge")

    # Response Components
    acknowledgments: List[str] = Field(default_factory=list, description="Acknowledged points from challenge")
    rebuttals: List[str] = Field(default_factory=list, description="Rebuttal points")
    clarifications: List[str] = Field(default_factory=list, description="Clarifications provided")

    # Additional Evidence
    additional_evidence: List[str] = Field(default_factory=list, description="Additional supporting evidence")
    additional_sources: List[str] = Field(default_factory=list, description="Additional data sources")

    # Revisions
    finding_revised: bool = Field(default=False, description="Whether finding was revised")
    revisions_made: List[str] = Field(default_factory=list, description="Specific revisions made")
    revised_confidence_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Revised confidence score if applicable"
    )

    # Impact Assessment
    impact_on_finding: Optional[str] = Field(
        None,
        description="Impact of challenge on original finding"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Response creation timestamp")


class DebateRound(BaseModel):
    """Complete round of adversarial debate on a topic."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "round_id": "ROUND-001-TSLA",
            "round_number": 1,
            "topic": "Environmental Performance Assessment",
            "findings": [],
            "challenges": [],
            "responses": [],
            "findings_count": 12,
            "challenges_count": 5,
            "responses_count": 5,
            "consensus_reached": False,
            "started_at": "2025-12-23T10:30:00Z",
            "completed_at": "2025-12-23T10:35:00Z"
        }
    })

    # Identification
    round_id: str = Field(..., description="Unique round identifier")
    round_number: int = Field(..., ge=1, description="Round number in debate sequence")
    topic: str = Field(..., description="Topic or focus of this round")

    # Participants
    participating_agents: List[AgentType] = Field(
        default_factory=list,
        description="Agents participating in this round"
    )

    # Round Content
    findings: List[AgentFinding] = Field(default_factory=list, description="Findings presented in this round")
    challenges: List[AgentChallenge] = Field(default_factory=list, description="Challenges raised in this round")
    responses: List[AgentResponse] = Field(default_factory=list, description="Responses provided in this round")

    # Statistics
    findings_count: int = Field(default=0, ge=0, description="Number of findings")
    challenges_count: int = Field(default=0, ge=0, description="Number of challenges")
    responses_count: int = Field(default=0, ge=0, description="Number of responses")

    # Consensus Metrics
    consensus_reached: bool = Field(default=False, description="Whether consensus was reached")
    consensus_score: Optional[float] = Field(None, ge=0, le=100, description="Degree of consensus (0-100)")
    unresolved_challenges: int = Field(default=0, ge=0, description="Number of unresolved challenges")

    # Round Summary
    key_agreements: List[str] = Field(default_factory=list, description="Key points of agreement")
    key_disagreements: List[str] = Field(default_factory=list, description="Key points of disagreement")
    emerging_insights: List[str] = Field(default_factory=list, description="New insights that emerged")

    # Quality Metrics
    average_confidence: Optional[float] = Field(None, ge=0, le=100, description="Average confidence across findings")
    data_quality_score: Optional[float] = Field(None, ge=0, le=100, description="Data quality score for round")

    # Metadata
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Round start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Round completion timestamp")
    duration_seconds: Optional[float] = Field(None, ge=0, description="Round duration in seconds")


class ConsensusResult(BaseModel):
    """Final consensus result after all debate rounds."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "consensus_id": "CONSENSUS-TSLA-20251223",
            "company_id": "TSLA-US",
            "total_rounds": 3,
            "consensus_achieved": True,
            "consensus_score": 85.5,
            "final_findings": [],
            "validated_findings": [],
            "rejected_findings": [],
            "consensus_narrative": "High agreement on strong environmental performance",
            "areas_of_agreement": [],
            "areas_of_disagreement": [],
            "created_at": "2025-12-23T10:45:00Z"
        }
    })

    # Identification
    consensus_id: str = Field(..., description="Unique consensus identifier")
    company_id: str = Field(..., description="Company being assessed")
    assessment_id: Optional[str] = Field(None, description="Related assessment ID")

    # Debate Summary
    total_rounds: int = Field(..., ge=1, description="Total number of debate rounds")
    debate_rounds: List[DebateRound] = Field(default_factory=list, description="All debate rounds")

    # Consensus Status
    consensus_achieved: bool = Field(..., description="Whether consensus was achieved")
    consensus_score: float = Field(..., ge=0, le=100, description="Overall consensus strength (0-100)")
    consensus_quality: Optional[str] = Field(
        None,
        description="Consensus quality: strong, moderate, weak"
    )

    # Final Findings
    final_findings: List[AgentFinding] = Field(default_factory=list, description="All final findings")
    validated_findings: List[AgentFinding] = Field(
        default_factory=list,
        description="Findings that survived challenges"
    )
    rejected_findings: List[str] = Field(
        default_factory=list,
        description="Finding IDs that were rejected"
    )
    revised_findings: List[str] = Field(
        default_factory=list,
        description="Finding IDs that were revised"
    )

    # Synthesis
    consensus_narrative: str = Field(..., description="Narrative summary of consensus")
    key_insights: List[str] = Field(default_factory=list, description="Key insights from debate process")
    areas_of_agreement: List[str] = Field(default_factory=list, description="Areas of strong agreement")
    areas_of_disagreement: List[str] = Field(default_factory=list, description="Areas of disagreement")
    remaining_uncertainties: List[str] = Field(default_factory=list, description="Remaining uncertainties")

    # Confidence Metrics
    overall_confidence: float = Field(..., ge=0, le=100, description="Overall confidence in consensus")
    confidence_by_category: Dict[str, float] = Field(
        default_factory=dict,
        description="Confidence scores by ESG category"
    )

    # Quality Metrics
    evidence_quality_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Quality of supporting evidence"
    )
    debate_rigor_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Rigor of debate process"
    )
    data_coverage_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Data coverage completeness"
    )

    # Agent Participation
    participating_agents: List[AgentType] = Field(
        default_factory=list,
        description="All agents that participated"
    )
    agent_contributions: Dict[str, int] = Field(
        default_factory=dict,
        description="Number of contributions by each agent type"
    )

    # Recommendations
    recommendations: List[str] = Field(default_factory=list, description="Final recommendations")
    further_investigation_needed: List[str] = Field(
        default_factory=list,
        description="Areas needing further investigation"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Consensus creation timestamp")
    processing_time_seconds: Optional[float] = Field(None, ge=0, description="Total processing time")

    @field_validator('consensus_score', 'overall_confidence')
    @classmethod
    def validate_scores(cls, v: float) -> float:
        """Validate scores are in valid range."""
        if not 0 <= v <= 100:
            raise ValueError("Scores must be between 0 and 100")
        return round(v, 2)
