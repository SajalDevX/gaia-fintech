"""
Veritas Agent - Supply Chain Verification
Analyzes supply chains, verifies blockchain records, checks supplier certifications,
analyzes shipping manifests, and cross-references public records.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum

from .base_agent import (
    BaseAgent,
    AgentReport,
    Finding,
    Evidence,
    EvidenceType,
)


class CertificationStatus(Enum):
    """Status of supplier certifications."""
    VALID = "valid"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    NOT_FOUND = "not_found"


@dataclass
class Supplier:
    """Supplier information."""
    id: str
    name: str
    country: str
    tier: int  # 1 = direct, 2 = indirect, etc.
    risk_score: float
    certifications: List[str]
    last_audit_date: Optional[datetime]


@dataclass
class BlockchainRecord:
    """Simulated blockchain verification record."""
    transaction_hash: str
    timestamp: datetime
    record_type: str
    data: Dict[str, Any]
    verified: bool
    confirmations: int


@dataclass
class ShippingManifest:
    """Shipping manifest data."""
    manifest_id: str
    origin: str
    destination: str
    carrier: str
    declared_goods: List[str]
    declared_value: float
    shipping_date: datetime
    customs_cleared: bool


class VeritasAgent(BaseAgent):
    """
    Veritas Agent - Supply Chain Verification and Transparency

    Capabilities:
    - Supply chain mapping and tier analysis
    - Blockchain record verification (simulated)
    - Supplier certification validation
    - Shipping manifest analysis
    - Cross-referencing with public records
    - Conflict mineral detection
    - Forced labor risk assessment
    """

    def __init__(
        self,
        name: str = "Veritas",
        timeout_seconds: int = 60,
        max_retries: int = 3,
        enable_debug: bool = False,
    ):
        super().__init__(
            name=name,
            agent_type="supply_chain_verification",
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            enable_debug=enable_debug,
        )

        # High-risk countries for various issues
        self.high_risk_countries = {
            "forced_labor": ["North Korea", "Eritrea", "Mauritania", "Turkmenistan"],
            "conflict_minerals": ["DRC", "South Sudan", "CAR", "Burundi"],
            "environmental": ["Bangladesh", "India", "China"],
        }

        # Recognized certifications
        self.valid_certifications = [
            "ISO 9001",
            "ISO 14001",
            "SA8000",
            "Fair Trade",
            "B Corp",
            "FSC",
            "LEED",
            "RJC",
            "BSCI",
            "SMETA",
        ]

    async def analyze(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentReport:
        """
        Perform comprehensive supply chain verification.

        Args:
            target_entity: Company name to analyze
            context: Optional context including industry, products, etc.

        Returns:
            AgentReport with supply chain findings
        """
        report = AgentReport(
            agent_name=self.name,
            agent_type=self.agent_type,
            target_entity=target_entity,
        )

        try:
            industry = context.get("industry", "manufacturing") if context else "manufacturing"
            product_categories = context.get("products", []) if context else []

            # Parallel analysis tasks
            analysis_tasks = [
                self._analyze_supply_chain_transparency(target_entity, industry),
                self._verify_blockchain_records(target_entity),
                self._verify_supplier_certifications(target_entity),
                self._analyze_shipping_manifests(target_entity),
                self._check_conflict_minerals(target_entity, product_categories),
                self._assess_labor_risks(target_entity),
                self._cross_reference_public_records(target_entity),
            ]

            results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    self.logger.warning(
                        "verification_task_failed",
                        error=str(result),
                    )
                    report.errors.append(f"Task failed: {str(result)}")
                elif isinstance(result, Finding):
                    report.add_finding(result)

            # Add metadata
            report.metadata = {
                "industry": industry,
                "product_categories": product_categories,
                "verification_timestamp": datetime.utcnow().isoformat(),
                "blockchain_enabled": True,
            }

        except Exception as e:
            self.logger.error(
                "veritas_analysis_error",
                target=target_entity,
                error=str(e),
            )
            report.errors.append(f"Analysis error: {str(e)}")

        return report

    async def collect_data(
        self,
        target_entity: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Evidence]:
        """
        Collect supply chain data and evidence.

        Args:
            target_entity: Entity to collect data for
            context: Additional context

        Returns:
            List of Evidence objects
        """
        evidence_list = []

        try:
            # Collect supplier data
            suppliers = await self._fetch_supplier_network(target_entity)
            for supplier in suppliers:
                evidence = Evidence(
                    type=EvidenceType.PUBLIC_RECORD,
                    source="Supplier Database",
                    description=f"Supplier: {supplier.name} (Tier {supplier.tier})",
                    data={
                        "supplier_id": supplier.id,
                        "name": supplier.name,
                        "country": supplier.country,
                        "tier": supplier.tier,
                        "risk_score": supplier.risk_score,
                        "certifications": supplier.certifications,
                    },
                    confidence=0.85,
                )
                evidence_list.append(evidence)

            # Collect blockchain records
            blockchain_records = await self._fetch_blockchain_records(target_entity)
            for record in blockchain_records:
                evidence = Evidence(
                    type=EvidenceType.BLOCKCHAIN_RECORD,
                    source="Blockchain Network",
                    description=f"Blockchain record: {record.record_type}",
                    data={
                        "transaction_hash": record.transaction_hash,
                        "verified": record.verified,
                        "confirmations": record.confirmations,
                        "record_type": record.record_type,
                    },
                    timestamp=record.timestamp,
                    confidence=0.95 if record.verified else 0.3,
                )
                evidence_list.append(evidence)

            # Collect shipping data
            manifests = await self._fetch_shipping_manifests(target_entity)
            for manifest in manifests:
                evidence = Evidence(
                    type=EvidenceType.SHIPPING_MANIFEST,
                    source="Customs Database",
                    description=f"Shipment from {manifest.origin} to {manifest.destination}",
                    data={
                        "manifest_id": manifest.manifest_id,
                        "origin": manifest.origin,
                        "destination": manifest.destination,
                        "goods": manifest.declared_goods,
                        "customs_cleared": manifest.customs_cleared,
                    },
                    timestamp=manifest.shipping_date,
                    confidence=0.88,
                )
                evidence_list.append(evidence)

        except Exception as e:
            self.logger.error("data_collection_error", error=str(e))

        return evidence_list

    def calculate_confidence(
        self,
        evidence: List[Evidence],
        context: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Calculate confidence based on verification completeness.

        Args:
            evidence: List of collected evidence
            context: Additional context

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if not evidence:
            return 0.0

        # Base confidence on evidence quality
        avg_confidence = sum(e.confidence for e in evidence) / len(evidence)

        # Bonus for blockchain verification
        blockchain_evidence = [e for e in evidence if e.type == EvidenceType.BLOCKCHAIN_RECORD]
        blockchain_bonus = min(0.15, len(blockchain_evidence) * 0.05)

        # Bonus for multiple certification sources
        cert_evidence = [e for e in evidence if e.type == EvidenceType.CERTIFICATION]
        cert_bonus = min(0.1, len(cert_evidence) * 0.03)

        final_confidence = min(1.0, avg_confidence + blockchain_bonus + cert_bonus)
        return final_confidence

    # Private analysis methods

    async def _analyze_supply_chain_transparency(
        self,
        target_entity: str,
        industry: str,
    ) -> Finding:
        """Analyze supply chain transparency and mapping."""
        finding = Finding(
            agent_name=self.name,
            finding_type="supply_chain_transparency",
            title="Supply Chain Transparency Assessment",
        )

        try:
            # Fetch supplier network
            suppliers = await self._fetch_supplier_network(target_entity)

            # Calculate transparency metrics
            tier_coverage = len(set(s.tier for s in suppliers))
            avg_risk_score = sum(s.risk_score for s in suppliers) / len(suppliers) if suppliers else 50.0
            certified_suppliers = len([s for s in suppliers if s.certifications])
            transparency_score = min(100, tier_coverage * 20 + (certified_suppliers / len(suppliers) * 40) if suppliers else 0)

            evidence = Evidence(
                type=EvidenceType.PUBLIC_RECORD,
                source="Supply Chain Database",
                description="Supply chain mapping and transparency analysis",
                data={
                    "total_suppliers": len(suppliers),
                    "tier_coverage": tier_coverage,
                    "certified_suppliers": certified_suppliers,
                    "avg_risk_score": round(avg_risk_score, 2),
                    "transparency_score": round(transparency_score, 2),
                    "supplier_countries": list(set(s.country for s in suppliers)),
                },
                confidence=0.82,
            )
            finding.add_evidence(evidence)

            # Determine severity
            if transparency_score < 40:
                finding.severity = "HIGH"
                finding.description = (
                    f"Low supply chain transparency for {target_entity}. "
                    f"Only {tier_coverage} tier(s) mapped, {certified_suppliers}/{len(suppliers)} "
                    f"suppliers certified. Significant visibility gaps present."
                )
            elif transparency_score < 60:
                finding.severity = "MEDIUM"
                finding.description = (
                    f"Moderate supply chain transparency for {target_entity}. "
                    f"Transparency score: {transparency_score:.0f}/100. "
                    f"Some visibility gaps in supply chain."
                )
            else:
                finding.severity = "LOW"
                finding.description = (
                    f"Good supply chain transparency for {target_entity}. "
                    f"Transparency score: {transparency_score:.0f}/100. "
                    f"{tier_coverage} tiers mapped with {certified_suppliers} certified suppliers."
                )

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to complete transparency analysis: {str(e)}"

        return finding

    async def _verify_blockchain_records(
        self,
        target_entity: str,
    ) -> Finding:
        """Verify blockchain records for supply chain traceability."""
        finding = Finding(
            agent_name=self.name,
            finding_type="blockchain_verification",
            title="Blockchain Traceability Verification",
        )

        try:
            # Fetch blockchain records
            records = await self._fetch_blockchain_records(target_entity)

            verified_count = len([r for r in records if r.verified])
            verification_rate = (verified_count / len(records) * 100) if records else 0

            evidence = Evidence(
                type=EvidenceType.BLOCKCHAIN_RECORD,
                source="Blockchain Network",
                description="Blockchain record verification",
                data={
                    "total_records": len(records),
                    "verified_records": verified_count,
                    "verification_rate": round(verification_rate, 2),
                    "avg_confirmations": round(sum(r.confirmations for r in records) / len(records), 2) if records else 0,
                },
                confidence=0.91,
            )
            finding.add_evidence(evidence)

            if verification_rate < 50:
                finding.severity = "HIGH"
                finding.description = (
                    f"Low blockchain verification rate for {target_entity}. "
                    f"Only {verification_rate:.0f}% of supply chain records verified on blockchain. "
                    f"Traceability concerns present."
                )
            elif verification_rate < 80:
                finding.severity = "MEDIUM"
                finding.description = (
                    f"Partial blockchain verification for {target_entity}. "
                    f"{verification_rate:.0f}% of records verified."
                )
            else:
                finding.severity = "LOW"
                finding.description = (
                    f"Strong blockchain verification for {target_entity}. "
                    f"{verification_rate:.0f}% of supply chain records verified on blockchain."
                )

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to verify blockchain records: {str(e)}"

        return finding

    async def _verify_supplier_certifications(
        self,
        target_entity: str,
    ) -> Finding:
        """Verify supplier certifications and compliance."""
        finding = Finding(
            agent_name=self.name,
            finding_type="supplier_certifications",
            title="Supplier Certification Verification",
        )

        try:
            suppliers = await self._fetch_supplier_network(target_entity)

            cert_status = {}
            expired_certs = 0
            valid_certs = 0

            for supplier in suppliers:
                for cert in supplier.certifications:
                    status = self._check_certification_status(cert, supplier)
                    if status == CertificationStatus.VALID:
                        valid_certs += 1
                    elif status == CertificationStatus.EXPIRED:
                        expired_certs += 1
                    cert_status[f"{supplier.name}:{cert}"] = status.value

            total_certs = len(cert_status)
            validity_rate = (valid_certs / total_certs * 100) if total_certs > 0 else 0

            evidence = Evidence(
                type=EvidenceType.CERTIFICATION,
                source="Certification Verification Database",
                description="Supplier certification verification",
                data={
                    "total_certifications": total_certs,
                    "valid_certifications": valid_certs,
                    "expired_certifications": expired_certs,
                    "validity_rate": round(validity_rate, 2),
                    "certification_breakdown": cert_status,
                },
                confidence=0.87,
            )
            finding.add_evidence(evidence)

            if validity_rate < 60 or expired_certs > total_certs * 0.3:
                finding.severity = "HIGH"
                finding.description = (
                    f"Certification compliance issues for {target_entity} suppliers. "
                    f"Only {validity_rate:.0f}% certifications valid, {expired_certs} expired."
                )
            elif validity_rate < 85:
                finding.severity = "MEDIUM"
                finding.description = (
                    f"Some certification gaps in {target_entity} supply chain. "
                    f"{validity_rate:.0f}% certifications valid."
                )
            else:
                finding.severity = "LOW"
                finding.description = (
                    f"Strong certification compliance for {target_entity}. "
                    f"{validity_rate:.0f}% of supplier certifications valid and current."
                )

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to verify certifications: {str(e)}"

        return finding

    async def _analyze_shipping_manifests(
        self,
        target_entity: str,
    ) -> Finding:
        """Analyze shipping manifests for anomalies."""
        finding = Finding(
            agent_name=self.name,
            finding_type="shipping_analysis",
            title="Shipping Manifest Analysis",
        )

        try:
            manifests = await self._fetch_shipping_manifests(target_entity)

            # Analyze for anomalies
            high_risk_routes = 0
            customs_issues = 0
            value_discrepancies = 0

            for manifest in manifests:
                # Check for high-risk origin countries
                if any(country in manifest.origin for country in ["Unknown", "Unspecified"]):
                    high_risk_routes += 1

                if not manifest.customs_cleared:
                    customs_issues += 1

                # Check for value anomalies (simplified)
                if manifest.declared_value < 1000 or manifest.declared_value > 10000000:
                    value_discrepancies += 1

            anomaly_rate = ((high_risk_routes + customs_issues + value_discrepancies) /
                           (len(manifests) * 3) * 100) if manifests else 0

            evidence = Evidence(
                type=EvidenceType.SHIPPING_MANIFEST,
                source="Customs and Trade Database",
                description="Shipping manifest analysis",
                data={
                    "total_manifests": len(manifests),
                    "high_risk_routes": high_risk_routes,
                    "customs_issues": customs_issues,
                    "value_discrepancies": value_discrepancies,
                    "anomaly_rate": round(anomaly_rate, 2),
                },
                confidence=0.84,
            )
            finding.add_evidence(evidence)

            if anomaly_rate > 20:
                finding.severity = "HIGH"
                finding.description = (
                    f"Significant shipping anomalies detected for {target_entity}. "
                    f"{anomaly_rate:.0f}% anomaly rate with {customs_issues} customs issues."
                )
            elif anomaly_rate > 10:
                finding.severity = "MEDIUM"
                finding.description = (
                    f"Some shipping irregularities for {target_entity}. "
                    f"{anomaly_rate:.0f}% anomaly rate."
                )
            else:
                finding.severity = "LOW"
                finding.description = (
                    f"Shipping manifests appear normal for {target_entity}. "
                    f"Low anomaly rate: {anomaly_rate:.0f}%"
                )

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to analyze shipping manifests: {str(e)}"

        return finding

    async def _check_conflict_minerals(
        self,
        target_entity: str,
        product_categories: List[str],
    ) -> Finding:
        """Check for conflict mineral risks."""
        finding = Finding(
            agent_name=self.name,
            finding_type="conflict_minerals",
            title="Conflict Minerals Assessment",
        )

        try:
            # Check if products likely contain conflict minerals
            high_risk_products = ["electronics", "jewelry", "automotive", "aerospace"]
            uses_conflict_minerals = any(cat.lower() in high_risk_products
                                        for cat in product_categories)

            suppliers = await self._fetch_supplier_network(target_entity)
            conflict_region_suppliers = [
                s for s in suppliers
                if any(region in s.country for region in self.high_risk_countries["conflict_minerals"])
            ]

            risk_score = len(conflict_region_suppliers) / len(suppliers) * 100 if suppliers else 0

            evidence = Evidence(
                type=EvidenceType.PUBLIC_RECORD,
                source="Conflict Minerals Database",
                description="Conflict minerals risk assessment",
                data={
                    "high_risk_suppliers": len(conflict_region_suppliers),
                    "total_suppliers": len(suppliers),
                    "risk_score": round(risk_score, 2),
                    "uses_conflict_minerals": uses_conflict_minerals,
                    "high_risk_countries": [s.country for s in conflict_region_suppliers],
                },
                confidence=0.78,
            )
            finding.add_evidence(evidence)

            if uses_conflict_minerals and risk_score > 10:
                finding.severity = "CRITICAL"
                finding.description = (
                    f"High conflict minerals risk for {target_entity}. "
                    f"{len(conflict_region_suppliers)} suppliers in conflict regions. "
                    f"Enhanced due diligence required."
                )
            elif risk_score > 5:
                finding.severity = "MEDIUM"
                finding.description = (
                    f"Some conflict minerals exposure for {target_entity}. "
                    f"{len(conflict_region_suppliers)} suppliers in high-risk regions."
                )
            else:
                finding.severity = "LOW"
                finding.description = (
                    f"Low conflict minerals risk for {target_entity}. "
                    f"Minimal supply chain exposure to conflict regions."
                )

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to assess conflict minerals: {str(e)}"

        return finding

    async def _assess_labor_risks(
        self,
        target_entity: str,
    ) -> Finding:
        """Assess forced labor and human rights risks."""
        finding = Finding(
            agent_name=self.name,
            finding_type="labor_rights",
            title="Labor Rights Risk Assessment",
        )

        try:
            suppliers = await self._fetch_supplier_network(target_entity)

            high_risk_labor = [
                s for s in suppliers
                if any(country in s.country for country in self.high_risk_countries["forced_labor"])
            ]

            # Check audit status
            unaudited_suppliers = [s for s in suppliers if not s.last_audit_date]
            outdated_audits = [
                s for s in suppliers
                if s.last_audit_date and (datetime.utcnow() - s.last_audit_date).days > 365
            ]

            risk_score = (
                (len(high_risk_labor) / len(suppliers) * 50) +
                (len(unaudited_suppliers) / len(suppliers) * 30) +
                (len(outdated_audits) / len(suppliers) * 20)
            ) if suppliers else 0

            evidence = Evidence(
                type=EvidenceType.PUBLIC_RECORD,
                source="Labor Rights Database",
                description="Labor rights risk assessment",
                data={
                    "high_risk_countries_count": len(high_risk_labor),
                    "unaudited_suppliers": len(unaudited_suppliers),
                    "outdated_audits": len(outdated_audits),
                    "risk_score": round(risk_score, 2),
                    "total_suppliers": len(suppliers),
                },
                confidence=0.81,
            )
            finding.add_evidence(evidence)

            if risk_score > 40:
                finding.severity = "CRITICAL"
                finding.description = (
                    f"Critical labor rights risks for {target_entity}. "
                    f"{len(high_risk_labor)} suppliers in high-risk countries, "
                    f"{len(unaudited_suppliers)} unaudited suppliers."
                )
            elif risk_score > 20:
                finding.severity = "HIGH"
                finding.description = (
                    f"Elevated labor rights risks for {target_entity}. "
                    f"Risk score: {risk_score:.0f}/100"
                )
            else:
                finding.severity = "LOW"
                finding.description = (
                    f"Manageable labor rights risks for {target_entity}. "
                    f"Risk score: {risk_score:.0f}/100"
                )

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to assess labor risks: {str(e)}"

        return finding

    async def _cross_reference_public_records(
        self,
        target_entity: str,
    ) -> Finding:
        """Cross-reference with public records and sanctions lists."""
        finding = Finding(
            agent_name=self.name,
            finding_type="public_records",
            title="Public Records Cross-Reference",
        )

        try:
            # Simulate checking various public databases
            sanctions_match = random.random() < 0.05  # 5% chance
            legal_issues = random.randint(0, 3)
            regulatory_violations = random.randint(0, 5)

            evidence = Evidence(
                type=EvidenceType.PUBLIC_RECORD,
                source="Public Records Database",
                description="Cross-reference with public records",
                data={
                    "sanctions_list_match": sanctions_match,
                    "legal_issues_count": legal_issues,
                    "regulatory_violations": regulatory_violations,
                    "databases_checked": [
                        "OFAC Sanctions",
                        "EU Sanctions",
                        "UN Sanctions",
                        "Legal Records",
                        "Regulatory Filings",
                    ],
                },
                confidence=0.89,
            )
            finding.add_evidence(evidence)

            if sanctions_match:
                finding.severity = "CRITICAL"
                finding.description = (
                    f"CRITICAL: {target_entity} or suppliers match sanctions lists. "
                    f"Immediate review required."
                )
            elif legal_issues > 2 or regulatory_violations > 3:
                finding.severity = "HIGH"
                finding.description = (
                    f"Multiple legal/regulatory issues found for {target_entity}. "
                    f"{legal_issues} legal issues, {regulatory_violations} violations."
                )
            elif legal_issues > 0 or regulatory_violations > 0:
                finding.severity = "MEDIUM"
                finding.description = (
                    f"Some regulatory issues for {target_entity}. "
                    f"{legal_issues} legal issues, {regulatory_violations} violations."
                )
            else:
                finding.severity = "LOW"
                finding.description = (
                    f"No significant public record issues for {target_entity}. "
                    f"Clean record across major databases."
                )

        except Exception as e:
            finding.severity = "INFO"
            finding.description = f"Unable to cross-reference public records: {str(e)}"

        return finding

    # Helper methods

    async def _fetch_supplier_network(
        self,
        target_entity: str,
    ) -> List[Supplier]:
        """Simulate fetching supplier network data."""
        await asyncio.sleep(0.1)  # Simulate API call

        suppliers = []
        num_suppliers = random.randint(5, 15)

        countries = [
            "China", "Vietnam", "India", "Bangladesh", "Thailand",
            "Germany", "USA", "Japan", "South Korea", "Taiwan",
            "Mexico", "Brazil", "Turkey", "Poland", "Italy"
        ]

        for i in range(num_suppliers):
            tier = random.choice([1, 1, 2, 2, 3])  # More tier 1 and 2
            num_certs = random.randint(0, 4)

            supplier = Supplier(
                id=f"SUP_{i:04d}",
                name=f"Supplier {i+1} Ltd",
                country=random.choice(countries),
                tier=tier,
                risk_score=random.uniform(20, 80),
                certifications=random.sample(self.valid_certifications, num_certs) if num_certs > 0 else [],
                last_audit_date=datetime.utcnow() - timedelta(days=random.randint(0, 730))
                    if random.random() > 0.2 else None,
            )
            suppliers.append(supplier)

        return suppliers

    async def _fetch_blockchain_records(
        self,
        target_entity: str,
    ) -> List[BlockchainRecord]:
        """Simulate fetching blockchain verification records."""
        await asyncio.sleep(0.1)

        records = []
        num_records = random.randint(10, 30)

        record_types = [
            "raw_material_origin",
            "manufacturing_process",
            "quality_inspection",
            "shipping_transfer",
            "customs_clearance",
        ]

        for i in range(num_records):
            verified = random.random() > 0.2  # 80% verification rate

            record = BlockchainRecord(
                transaction_hash=f"0x{random.randint(10**63, 10**64-1):064x}",
                timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 365)),
                record_type=random.choice(record_types),
                data={"details": "Blockchain verified transaction"},
                verified=verified,
                confirmations=random.randint(0, 100) if verified else 0,
            )
            records.append(record)

        return records

    async def _fetch_shipping_manifests(
        self,
        target_entity: str,
    ) -> List[ShippingManifest]:
        """Simulate fetching shipping manifest data."""
        await asyncio.sleep(0.1)

        manifests = []
        num_manifests = random.randint(15, 40)

        origins = ["China", "Vietnam", "India", "Germany", "Mexico", "Taiwan"]
        destinations = ["USA", "UK", "Germany", "France", "Canada"]
        carriers = ["Maersk", "MSC", "CMA CGM", "COSCO", "Hapag-Lloyd"]
        goods_types = ["Electronics", "Textiles", "Raw Materials", "Components", "Finished Goods"]

        for i in range(num_manifests):
            manifest = ShippingManifest(
                manifest_id=f"MAN_{i:06d}",
                origin=random.choice(origins),
                destination=random.choice(destinations),
                carrier=random.choice(carriers),
                declared_goods=random.sample(goods_types, random.randint(1, 3)),
                declared_value=random.uniform(5000, 500000),
                shipping_date=datetime.utcnow() - timedelta(days=random.randint(0, 180)),
                customs_cleared=random.random() > 0.1,  # 90% cleared
            )
            manifests.append(manifest)

        return manifests

    def _check_certification_status(
        self,
        certification: str,
        supplier: Supplier,
    ) -> CertificationStatus:
        """Check the status of a certification."""
        if certification not in self.valid_certifications:
            return CertificationStatus.NOT_FOUND

        # Simulate certification status
        rand = random.random()
        if rand < 0.75:
            return CertificationStatus.VALID
        elif rand < 0.90:
            return CertificationStatus.EXPIRED
        elif rand < 0.95:
            return CertificationStatus.SUSPENDED
        else:
            return CertificationStatus.REVOKED
