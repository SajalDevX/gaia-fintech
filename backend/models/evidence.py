"""
Evidence Trail and Verification Models
GAIA - Global AI-powered Impact Assessment System
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class EvidenceType(str, Enum):
    """Types of evidence that can be collected."""
    DOCUMENT = "document"
    REPORT = "report"
    SATELLITE_DATA = "satellite_data"
    SENSOR_DATA = "sensor_data"
    NEWS_ARTICLE = "news_article"
    REGULATORY_FILING = "regulatory_filing"
    FINANCIAL_STATEMENT = "financial_statement"
    SUSTAINABILITY_REPORT = "sustainability_report"
    THIRD_PARTY_AUDIT = "third_party_audit"
    ACADEMIC_RESEARCH = "academic_research"
    SOCIAL_MEDIA = "social_media"
    INTERVIEW = "interview"
    OBSERVATION = "observation"
    DATABASE_RECORD = "database_record"
    API_DATA = "api_data"
    OTHER = "other"


class SourceType(str, Enum):
    """Source types for evidence."""
    PRIMARY = "primary"  # First-hand data from company
    SECONDARY = "secondary"  # Reports about the company
    TERTIARY = "tertiary"  # Aggregated or summarized data
    REMOTE_SENSING = "remote_sensing"  # Satellite/sensor data
    CROWDSOURCED = "crowdsourced"  # Public contributions
    EXPERT_OPINION = "expert_opinion"  # Expert analysis


class VerificationStatus(str, Enum):
    """Verification status of evidence."""
    VERIFIED = "verified"  # Fully verified
    PARTIALLY_VERIFIED = "partially_verified"  # Some aspects verified
    UNVERIFIED = "unverified"  # Not yet verified
    DISPUTED = "disputed"  # Conflicting information exists
    REJECTED = "rejected"  # Determined to be invalid


class DataQuality(str, Enum):
    """Data quality rating."""
    EXCELLENT = "excellent"  # High quality, authoritative source
    GOOD = "good"  # Reliable, minor limitations
    FAIR = "fair"  # Usable but with notable limitations
    POOR = "poor"  # Significant quality concerns
    UNRELIABLE = "unreliable"  # Not trustworthy


class EvidenceSource(BaseModel):
    """Source information for evidence."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "source_id": "SRC-001",
            "source_name": "Tesla 2023 Impact Report",
            "source_type": "primary",
            "source_url": "https://www.tesla.com/impact-report/2023",
            "publisher": "Tesla, Inc.",
            "publication_date": "2024-04-15",
            "accessed_date": "2025-12-23T10:30:00Z",
            "credibility_score": 88.5,
            "is_official": True
        }
    })

    source_id: str = Field(..., description="Unique source identifier")
    source_name: str = Field(..., description="Name or title of source", max_length=500)
    source_type: SourceType = Field(..., description="Type of source")

    # Source Details
    source_url: Optional[str] = Field(None, description="URL to source document/data")
    publisher: Optional[str] = Field(None, description="Publisher or author")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    accessed_date: datetime = Field(default_factory=datetime.utcnow, description="Date accessed")

    # Credibility
    credibility_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Credibility score of source (0-100)"
    )
    is_official: bool = Field(default=False, description="Whether this is an official company source")
    is_third_party_verified: bool = Field(default=False, description="Whether third-party verified")

    # Classification
    peer_reviewed: bool = Field(default=False, description="Whether peer-reviewed")
    regulatory_filing: bool = Field(default=False, description="Whether regulatory filing")

    # Additional Info
    doi: Optional[str] = Field(None, description="Digital Object Identifier if applicable")
    isbn: Optional[str] = Field(None, description="ISBN if applicable")
    citation: Optional[str] = Field(None, description="Full citation format")

    @field_validator('credibility_score')
    @classmethod
    def validate_credibility(cls, v: float) -> float:
        """Validate credibility score."""
        if not 0 <= v <= 100:
            raise ValueError("Credibility score must be between 0 and 100")
        return round(v, 2)


class EvidenceItem(BaseModel):
    """Individual piece of evidence in the assessment."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "evidence_id": "EVD-001-TSLA",
            "evidence_type": "sustainability_report",
            "title": "2023 Carbon Emissions Data",
            "description": "Reported 35% reduction in carbon emissions vs 2020 baseline",
            "content_summary": "Total emissions: 6.5M tons CO2e, down from 10M tons in 2020",
            "source": {},
            "confidence_score": 85.0,
            "relevance_score": 92.0,
            "verification_status": "verified",
            "data_quality": "excellent",
            "created_at": "2025-12-23T10:30:00Z"
        }
    })

    # Identification
    evidence_id: str = Field(..., description="Unique evidence identifier")
    evidence_type: EvidenceType = Field(..., description="Type of evidence")

    # Content
    title: str = Field(..., description="Brief title of evidence", max_length=500)
    description: str = Field(..., description="Detailed description of evidence")
    content_summary: Optional[str] = Field(None, description="Summary of key content")
    full_content: Optional[str] = Field(None, description="Full content if applicable")

    # Source
    source: EvidenceSource = Field(..., description="Source information")
    additional_sources: List[EvidenceSource] = Field(
        default_factory=list,
        description="Additional corroborating sources"
    )

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Classification tags")
    keywords: List[str] = Field(default_factory=list, description="Keywords for searchability")

    # Geographic/Temporal Context
    geographic_scope: Optional[str] = Field(None, description="Geographic scope of evidence")
    time_period_start: Optional[datetime] = Field(None, description="Start of time period covered")
    time_period_end: Optional[datetime] = Field(None, description="End of time period covered")

    # Quantitative Data
    quantitative_values: Dict[str, Any] = Field(
        default_factory=dict,
        description="Quantitative values extracted from evidence"
    )

    # Scores
    confidence_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Confidence in this evidence (0-100)"
    )
    relevance_score: float = Field(
        ...,
        ge=0,
        le=100,
        description="Relevance to assessment (0-100)"
    )
    impact_score: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Impact on overall assessment"
    )

    # Verification
    verification_status: VerificationStatus = Field(..., description="Verification status")
    verified_by: Optional[str] = Field(None, description="Who/what verified this evidence")
    verification_date: Optional[datetime] = Field(None, description="When verification occurred")
    verification_notes: Optional[str] = Field(None, description="Notes on verification process")

    # Quality
    data_quality: DataQuality = Field(..., description="Data quality rating")
    quality_issues: List[str] = Field(default_factory=list, description="Known quality issues")
    limitations: List[str] = Field(default_factory=list, description="Known limitations of evidence")

    # Relationships
    supports_finding_ids: List[str] = Field(
        default_factory=list,
        description="IDs of findings this evidence supports"
    )
    contradicts_finding_ids: List[str] = Field(
        default_factory=list,
        description="IDs of findings this evidence contradicts"
    )
    related_evidence_ids: List[str] = Field(
        default_factory=list,
        description="IDs of related evidence items"
    )

    # AI Analysis
    ai_extracted: bool = Field(default=False, description="Whether extracted by AI")
    ai_confidence: Optional[float] = Field(None, ge=0, le=100, description="AI extraction confidence")
    nlp_entities: List[str] = Field(default_factory=list, description="Entities extracted by NLP")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Evidence added timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @field_validator('confidence_score', 'relevance_score')
    @classmethod
    def validate_scores(cls, v: float) -> float:
        """Validate scores are in valid range."""
        if not 0 <= v <= 100:
            raise ValueError("Scores must be between 0 and 100")
        return round(v, 2)


class BlockchainRecord(BaseModel):
    """Blockchain record for evidence verification (simulated or real)."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "record_id": "BLK-001-EVD-001",
            "evidence_id": "EVD-001-TSLA",
            "blockchain_hash": "0x1234567890abcdef1234567890abcdef12345678",
            "transaction_id": "0xabcdef1234567890abcdef1234567890abcdef12",
            "block_number": 12345678,
            "timestamp": "2025-12-23T10:30:00Z",
            "network": "ethereum-sepolia",
            "verification_url": "https://sepolia.etherscan.io/tx/0xabc..."
        }
    })

    # Identification
    record_id: str = Field(..., description="Unique blockchain record identifier")
    evidence_id: str = Field(..., description="Evidence item being recorded")

    # Blockchain Details
    blockchain_hash: str = Field(..., description="Hash of evidence on blockchain")
    transaction_id: Optional[str] = Field(None, description="Blockchain transaction ID")
    block_number: Optional[int] = Field(None, ge=0, description="Block number")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of record")

    # Network Information
    network: str = Field(default="testnet", description="Blockchain network used")
    chain_id: Optional[int] = Field(None, description="Chain ID if applicable")
    contract_address: Optional[str] = Field(None, description="Smart contract address if applicable")

    # Verification
    verification_url: Optional[str] = Field(None, description="URL to verify on blockchain explorer")
    verified: bool = Field(default=False, description="Whether blockchain record is verified")

    # Metadata
    data_hash: str = Field(..., description="Hash of the evidence data")
    metadata_hash: Optional[str] = Field(None, description="Hash of metadata")

    # Status
    status: str = Field(default="pending", description="Status: pending, confirmed, failed")
    confirmations: int = Field(default=0, ge=0, description="Number of confirmations")

    # Cost and Gas (for real blockchain)
    gas_used: Optional[int] = Field(None, ge=0, description="Gas used for transaction")
    transaction_fee: Optional[float] = Field(None, ge=0, description="Transaction fee in native currency")

    @field_validator('blockchain_hash', 'data_hash')
    @classmethod
    def validate_hash_format(cls, v: str) -> str:
        """Validate hash format (basic check)."""
        if not v:
            raise ValueError("Hash cannot be empty")
        return v.lower()


class EvidenceTrail(BaseModel):
    """Complete evidence trail for an assessment."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "trail_id": "TRAIL-TSLA-20251223",
            "assessment_id": "TSLA-US-20251223-001",
            "company_id": "TSLA-US",
            "evidence_items": [],
            "total_evidence_count": 42,
            "verified_count": 38,
            "blockchain_records": [],
            "overall_confidence": 86.5,
            "data_quality_score": 88.0,
            "created_at": "2025-12-23T10:30:00Z"
        }
    })

    # Identification
    trail_id: str = Field(..., description="Unique trail identifier")
    assessment_id: str = Field(..., description="Related assessment ID")
    company_id: str = Field(..., description="Company being assessed")

    # Evidence Collection
    evidence_items: List[EvidenceItem] = Field(default_factory=list, description="All evidence items")
    total_evidence_count: int = Field(default=0, ge=0, description="Total number of evidence items")

    # Verification Statistics
    verified_count: int = Field(default=0, ge=0, description="Number of verified items")
    unverified_count: int = Field(default=0, ge=0, description="Number of unverified items")
    disputed_count: int = Field(default=0, ge=0, description="Number of disputed items")

    # Blockchain Records
    blockchain_records: List[BlockchainRecord] = Field(
        default_factory=list,
        description="Blockchain verification records"
    )
    blockchain_enabled: bool = Field(default=True, description="Whether blockchain verification is enabled")

    # Source Diversity
    unique_sources: int = Field(default=0, ge=0, description="Number of unique sources")
    source_types: Dict[str, int] = Field(
        default_factory=dict,
        description="Count by source type"
    )
    evidence_types: Dict[str, int] = Field(
        default_factory=dict,
        description="Count by evidence type"
    )

    # Quality Metrics
    overall_confidence: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Overall confidence in evidence trail"
    )
    data_quality_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Overall data quality score"
    )
    completeness_score: float = Field(
        default=50.0,
        ge=0,
        le=100,
        description="Evidence completeness score"
    )

    # Coverage Analysis
    esg_categories_covered: List[str] = Field(
        default_factory=list,
        description="ESG categories with evidence"
    )
    coverage_gaps: List[str] = Field(
        default_factory=list,
        description="Areas lacking evidence"
    )

    # Provenance
    collection_methodology: Optional[str] = Field(None, description="How evidence was collected")
    collection_agents: List[str] = Field(
        default_factory=list,
        description="Agents that collected evidence"
    )

    # Timeline
    earliest_evidence_date: Optional[datetime] = Field(None, description="Earliest evidence date")
    latest_evidence_date: Optional[datetime] = Field(None, description="Latest evidence date")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Trail creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    finalized: bool = Field(default=False, description="Whether trail is finalized")
    finalized_at: Optional[datetime] = Field(None, description="Finalization timestamp")

    # Audit Trail
    audit_log: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Audit log of changes to evidence trail"
    )

    @field_validator('overall_confidence', 'data_quality_score', 'completeness_score')
    @classmethod
    def validate_scores(cls, v: float) -> float:
        """Validate scores are in valid range."""
        if not 0 <= v <= 100:
            raise ValueError("Scores must be between 0 and 100")
        return round(v, 2)


class ProvenanceRecord(BaseModel):
    """Detailed provenance record for data lineage."""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "provenance_id": "PROV-001-EVD-001",
            "evidence_id": "EVD-001-TSLA",
            "origin_description": "Extracted from Tesla 2023 Impact Report, page 42",
            "collection_method": "automated_extraction",
            "collector": "data_validator_agent",
            "transformations": ["PDF extraction", "Data validation", "Unit normalization"],
            "verification_chain": [],
            "created_at": "2025-12-23T10:30:00Z"
        }
    })

    # Identification
    provenance_id: str = Field(..., description="Unique provenance record identifier")
    evidence_id: str = Field(..., description="Evidence item this tracks")

    # Origin
    origin_description: str = Field(..., description="Description of data origin")
    original_source: Optional[str] = Field(None, description="Original source identifier")
    collection_method: str = Field(..., description="How data was collected")

    # Collection Details
    collector: Optional[str] = Field(None, description="Who/what collected the data")
    collection_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When collected")
    collection_location: Optional[str] = Field(None, description="Where collected (if applicable)")

    # Data Lineage
    parent_records: List[str] = Field(
        default_factory=list,
        description="Parent provenance records if derived"
    )
    transformations: List[str] = Field(
        default_factory=list,
        description="Transformations applied to data"
    )
    processing_steps: List[str] = Field(
        default_factory=list,
        description="Processing steps applied"
    )

    # Verification Chain
    verification_chain: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Chain of verification steps"
    )

    # Quality Assurance
    quality_checks: List[str] = Field(
        default_factory=list,
        description="Quality checks performed"
    )
    anomalies_detected: List[str] = Field(
        default_factory=list,
        description="Anomalies detected during processing"
    )

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Record creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
