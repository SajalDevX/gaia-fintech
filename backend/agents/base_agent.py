"""
Base Agent Module for GAIA
Abstract base class for all specialized AI agents in the system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, TypeVar, Generic
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import logging
import uuid
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
import structlog

logger = structlog.get_logger(__name__)


class ConfidenceLevel(Enum):
    """Confidence levels for agent findings."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class EvidenceType(Enum):
    """Types of evidence that can be collected."""
    SATELLITE_IMAGE = "satellite_image"
    DOCUMENT = "document"
    NEWS_ARTICLE = "news_article"
    SOCIAL_MEDIA = "social_media"
    BLOCKCHAIN_RECORD = "blockchain_record"
    SENSOR_DATA = "sensor_data"
    PUBLIC_RECORD = "public_record"
    CERTIFICATION = "certification"
    SHIPPING_MANIFEST = "shipping_manifest"
    API_RESPONSE = "api_response"


@dataclass
class Evidence:
    """Represents a single piece of evidence collected by an agent."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: EvidenceType = EvidenceType.API_RESPONSE
    source: str = ""
    description: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence: float = 0.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert evidence to dictionary."""
        return {
            "id": self.id,
            "type": self.type.value,
            "source": self.source,
            "description": self.description,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class Finding:
    """Represents a finding from an agent's analysis."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = ""
    finding_type: str = ""
    severity: str = "INFO"  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    title: str = ""
    description: str = ""
    confidence_score: float = 0.0  # 0.0 to 1.0
    evidence_trail: List[Evidence] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_confidence_level(self) -> ConfidenceLevel:
        """Convert numeric confidence to level."""
        if self.confidence_score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif self.confidence_score >= 0.75:
            return ConfidenceLevel.HIGH
        elif self.confidence_score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif self.confidence_score >= 0.3:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence to the finding."""
        self.evidence_trail.append(evidence)
        # Recalculate confidence based on evidence
        if self.evidence_trail:
            avg_confidence = sum(e.confidence for e in self.evidence_trail) / len(self.evidence_trail)
            self.confidence_score = (self.confidence_score + avg_confidence) / 2

    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "finding_type": self.finding_type,
            "severity": self.severity,
            "title": self.title,
            "description": self.description,
            "confidence_score": self.confidence_score,
            "confidence_level": self.get_confidence_level().value,
            "evidence_trail": [e.to_dict() for e in self.evidence_trail],
            "evidence_count": len(self.evidence_trail),
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class AgentReport:
    """Complete report from an agent's analysis."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str = ""
    agent_type: str = ""
    target_entity: str = ""
    findings: List[Finding] = field(default_factory=list)
    overall_risk_score: float = 0.0  # 0.0 to 100.0
    execution_time_seconds: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_finding(self, finding: Finding) -> None:
        """Add a finding to the report."""
        self.findings.append(finding)
        self._recalculate_risk_score()

    def _recalculate_risk_score(self) -> None:
        """Recalculate overall risk score based on findings."""
        if not self.findings:
            self.overall_risk_score = 50.0  # Neutral
            return

        severity_weights = {
            "CRITICAL": 1.0,
            "HIGH": 0.8,
            "MEDIUM": 0.5,
            "LOW": 0.3,
            "INFO": 0.1,
        }

        total_weighted_score = 0.0
        total_weight = 0.0

        for finding in self.findings:
            weight = severity_weights.get(finding.severity, 0.1)
            # Lower confidence in negative findings = higher risk score
            risk_contribution = (1 - finding.confidence_score) * 100 * weight
            total_weighted_score += risk_contribution
            total_weight += weight

        if total_weight > 0:
            self.overall_risk_score = min(100.0, total_weighted_score / total_weight)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "agent_type": self.agent_type,
            "target_entity": self.target_entity,
            "findings": [f.to_dict() for f in self.findings],
            "findings_count": len(self.findings),
            "overall_risk_score": self.overall_risk_score,
            "execution_time_seconds": self.execution_time_seconds,
            "timestamp": self.timestamp.isoformat(),
            "errors": self.errors,
            "metadata": self.metadata,
        }


class BaseAgent(ABC):
    """
    Abstract base class for all GAIA agents.

    All specialized agents (Sentinel, Veritas, Pulse, etc.) inherit from this class
    and implement the required abstract methods.
    """

    def __init__(
        self,
        name: str,
        agent_type: str,
        timeout_seconds: int = 60,
        max_retries: int = 3,
        enable_debug: bool = False,
    ):
        """
        Initialize the base agent.

        Args:
            name: Human-readable name for the agent
            agent_type: Type/category of the agent
            timeout_seconds: Maximum execution time before timeout
            max_retries: Maximum number of retries on failure
            enable_debug: Enable debug logging
        """
        self.name = name
        self.agent_type = agent_type
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.enable_debug = enable_debug

        self.logger = structlog.get_logger(self.__class__.__name__)

        # Performance metrics
        self.total_executions = 0
        self.successful_executions = 0
        self.failed_executions = 0

    @abstractmethod
    async def analyze(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentReport:
        """
        Perform analysis on the target entity.

        Args:
            target_entity: The entity to analyze (company name, product, etc.)
            context: Additional context for the analysis

        Returns:
            AgentReport containing findings and evidence
        """
        pass

    @abstractmethod
    async def collect_data(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Evidence]:
        """
        Collect data/evidence for the target entity.

        Args:
            target_entity: The entity to collect data for
            context: Additional context for data collection

        Returns:
            List of Evidence objects
        """
        pass

    @abstractmethod
    def calculate_confidence(
        self,
        evidence: List[Evidence],
        context: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Calculate confidence score based on collected evidence.

        Args:
            evidence: List of evidence collected
            context: Additional context

        Returns:
            Confidence score between 0.0 and 1.0
        """
        pass

    async def execute_with_timeout(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentReport:
        """
        Execute analysis with timeout protection.

        Args:
            target_entity: The entity to analyze
            context: Additional context

        Returns:
            AgentReport

        Raises:
            asyncio.TimeoutError: If execution exceeds timeout
        """
        start_time = datetime.utcnow()

        try:
            self.total_executions += 1

            self.logger.info(
                "agent_execution_started",
                agent=self.name,
                target=target_entity,
            )

            # Execute with timeout
            report = await asyncio.wait_for(
                self.analyze(target_entity, context),
                timeout=self.timeout_seconds,
            )

            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            report.execution_time_seconds = execution_time

            self.successful_executions += 1

            self.logger.info(
                "agent_execution_completed",
                agent=self.name,
                target=target_entity,
                execution_time=execution_time,
                findings_count=len(report.findings),
                risk_score=report.overall_risk_score,
            )

            return report

        except asyncio.TimeoutError:
            self.failed_executions += 1
            self.logger.error(
                "agent_execution_timeout",
                agent=self.name,
                target=target_entity,
                timeout=self.timeout_seconds,
            )

            # Return partial report with timeout error
            report = AgentReport(
                agent_name=self.name,
                agent_type=self.agent_type,
                target_entity=target_entity,
                errors=[f"Execution timeout after {self.timeout_seconds} seconds"],
            )
            report.execution_time_seconds = (datetime.utcnow() - start_time).total_seconds()
            return report

        except Exception as e:
            self.failed_executions += 1
            self.logger.error(
                "agent_execution_error",
                agent=self.name,
                target=target_entity,
                error=str(e),
                exc_info=True,
            )

            # Return error report
            report = AgentReport(
                agent_name=self.name,
                agent_type=self.agent_type,
                target_entity=target_entity,
                errors=[f"Execution error: {str(e)}"],
            )
            report.execution_time_seconds = (datetime.utcnow() - start_time).total_seconds()
            return report

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError)),
    )
    async def fetch_with_retry(
        self,
        fetch_func,
        *args,
        **kwargs,
    ) -> Any:
        """
        Execute a fetch function with automatic retry logic.

        Args:
            fetch_func: The async function to execute
            *args: Positional arguments for fetch_func
            **kwargs: Keyword arguments for fetch_func

        Returns:
            Result from fetch_func
        """
        try:
            return await fetch_func(*args, **kwargs)
        except Exception as e:
            self.logger.warning(
                "fetch_retry_attempt",
                agent=self.name,
                error=str(e),
            )
            raise

    async def challenge_finding(
        self,
        finding: Finding,
        counter_evidence: List[Evidence],
    ) -> Dict[str, Any]:
        """
        Challenge a finding with counter-evidence (adversarial debate).

        Args:
            finding: The finding to challenge
            counter_evidence: Evidence that contradicts the finding

        Returns:
            Dictionary with challenge results
        """
        self.logger.info(
            "challenging_finding",
            agent=self.name,
            finding_id=finding.id,
            original_confidence=finding.confidence_score,
        )

        # Calculate strength of counter-evidence
        if not counter_evidence:
            return {
                "challenged": False,
                "original_confidence": finding.confidence_score,
                "adjusted_confidence": finding.confidence_score,
                "reason": "No counter-evidence provided",
            }

        counter_avg_confidence = sum(e.confidence for e in counter_evidence) / len(counter_evidence)

        # Adjust confidence based on counter-evidence strength
        adjustment_factor = counter_avg_confidence * 0.5  # Counter-evidence can reduce confidence by up to 50%
        adjusted_confidence = max(0.0, finding.confidence_score - adjustment_factor)

        return {
            "challenged": True,
            "original_confidence": finding.confidence_score,
            "adjusted_confidence": adjusted_confidence,
            "counter_evidence_count": len(counter_evidence),
            "counter_evidence_strength": counter_avg_confidence,
            "adjustment_factor": adjustment_factor,
            "reason": f"Challenged with {len(counter_evidence)} pieces of counter-evidence",
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics."""
        success_rate = (
            self.successful_executions / self.total_executions
            if self.total_executions > 0
            else 0.0
        )

        return {
            "agent_name": self.name,
            "agent_type": self.agent_type,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "failed_executions": self.failed_executions,
            "success_rate": success_rate,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', type='{self.agent_type}')"
