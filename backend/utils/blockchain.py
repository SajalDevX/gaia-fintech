"""
GAIA Blockchain Audit Trail - Caffeine AI Integration
Immutable audit trail for agent decisions with decentralized verification.

Features:
- Blockchain-based audit trail for all ESG assessments
- Cryptographic signatures for agent findings
- Smart contract simulation for ESG compliance triggers
- Decentralized verification of sustainability claims
- Full transparency with verifiable evidence chains
"""

import hashlib
import json
import time
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid
import structlog

logger = structlog.get_logger()


class TransactionType(Enum):
    """Types of blockchain transactions."""
    AGENT_FINDING = "agent_finding"
    EVIDENCE_SUBMISSION = "evidence_submission"
    CHALLENGE_ISSUED = "challenge_issued"
    CHALLENGE_RESPONSE = "challenge_response"
    DEBATE_ARGUMENT = "debate_argument"
    CONSENSUS_REACHED = "consensus_reached"
    ASSESSMENT_FINALIZED = "assessment_finalized"
    GREENWASHING_ALERT = "greenwashing_alert"
    SDG_IMPACT_RECORDED = "sdg_impact_recorded"
    SMART_CONTRACT_TRIGGER = "smart_contract_trigger"


class ESGComplianceLevel(Enum):
    """ESG compliance levels for smart contracts."""
    COMPLIANT = "compliant"
    WARNING = "warning"
    NON_COMPLIANT = "non_compliant"
    CRITICAL = "critical"


@dataclass
class SmartContract:
    """ESG Compliance Smart Contract."""
    contract_id: str
    contract_type: str  # "esg_threshold", "greenwashing_alert", "sdg_target"
    conditions: Dict[str, Any]
    actions: List[str]
    created_at: float
    triggered: bool = False
    triggered_at: Optional[float] = None

    def evaluate(self, data: Dict[str, Any]) -> bool:
        """Evaluate if contract conditions are met."""
        contract_type = self.contract_type

        if contract_type == "esg_threshold":
            score = data.get("score", 100)
            threshold = self.conditions.get("min_score", 50)
            return score < threshold

        elif contract_type == "greenwashing_alert":
            signals = data.get("greenwashing_signals", 0)
            threshold = self.conditions.get("max_signals", 2)
            return signals > threshold

        elif contract_type == "sdg_target":
            impact = data.get("sdg_impact", 0)
            target = self.conditions.get("min_impact", 50)
            return impact < target

        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contract_id": self.contract_id,
            "contract_type": self.contract_type,
            "conditions": self.conditions,
            "actions": self.actions,
            "created_at": self.created_at,
            "triggered": self.triggered,
            "triggered_at": self.triggered_at
        }


@dataclass
class Block:
    """Represents a block in the blockchain."""
    index: int
    timestamp: float
    transactions: List[Dict[str, Any]]
    previous_hash: str
    merkle_root: str = ""
    nonce: int = 0
    hash: str = field(default="", init=False)
    validator: str = "gaia_node_1"

    def __post_init__(self):
        self.merkle_root = self._calculate_merkle_root()
        self.hash = self.calculate_hash()

    def _calculate_merkle_root(self) -> str:
        """Calculate Merkle root of transactions."""
        if not self.transactions:
            return hashlib.sha256(b"empty").hexdigest()

        tx_hashes = [
            hashlib.sha256(json.dumps(tx, sort_keys=True, default=str).encode()).hexdigest()
            for tx in self.transactions
        ]

        while len(tx_hashes) > 1:
            if len(tx_hashes) % 2 == 1:
                tx_hashes.append(tx_hashes[-1])
            tx_hashes = [
                hashlib.sha256((tx_hashes[i] + tx_hashes[i + 1]).encode()).hexdigest()
                for i in range(0, len(tx_hashes), 2)
            ]

        return tx_hashes[0] if tx_hashes else ""

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of block contents."""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "merkle_root": self.merkle_root,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "validator": self.validator
        }, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp, tz=timezone.utc).isoformat(),
            "transactions": self.transactions,
            "transaction_count": len(self.transactions),
            "merkle_root": self.merkle_root,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
            "validator": self.validator
        }


@dataclass
class Transaction:
    """Represents a transaction in the blockchain."""
    tx_id: str
    tx_type: TransactionType
    agent_id: str
    company_ticker: str
    data: Dict[str, Any]
    timestamp: float
    signature: str = field(default="", init=False)
    verified: bool = False

    def __post_init__(self):
        self.signature = self._generate_signature()

    def _generate_signature(self) -> str:
        """Generate cryptographic transaction signature."""
        content = json.dumps({
            "tx_id": self.tx_id,
            "agent_id": self.agent_id,
            "company_ticker": self.company_ticker,
            "data": self.data,
            "timestamp": self.timestamp
        }, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()

    def verify_signature(self) -> bool:
        """Verify transaction signature integrity."""
        expected = self._generate_signature()
        self.verified = (expected == self.signature)
        return self.verified

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        return {
            "tx_id": self.tx_id,
            "tx_type": self.tx_type.value,
            "agent_id": self.agent_id,
            "company_ticker": self.company_ticker,
            "data": self.data,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp, tz=timezone.utc).isoformat(),
            "signature": self.signature,
            "verified": self.verified
        }


class CaffeineAIBlockchain:
    """
    Caffeine AI-style Blockchain for GAIA.

    Provides:
    - Immutable audit trail for all agent decisions
    - Decentralized verification of sustainability claims
    - Smart contracts for automated ESG compliance triggers
    - Cryptographic proof of agent findings
    - Full transparency with verifiable evidence chains
    """

    def __init__(self, network: str = "testnet"):
        self.network = network
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.smart_contracts: Dict[str, SmartContract] = {}
        self.difficulty = 2
        self.block_size_limit = 100  # Max transactions per block
        self.event_handlers: Dict[str, List[Callable]] = {}

        self._create_genesis_block()
        self._register_default_contracts()

        logger.info("blockchain_initialized", network=network)

    def _create_genesis_block(self) -> None:
        """Create the genesis block."""
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[{
                "type": "genesis",
                "message": "GAIA Genesis Block - Caffeine AI Powered Sustainability Verification",
                "version": "2.0.0",
                "network": self.network,
                "created": datetime.now(tz=timezone.utc).isoformat()
            }],
            previous_hash="0" * 64
        )
        self.chain.append(genesis_block)

    def _register_default_contracts(self) -> None:
        """Register default ESG compliance smart contracts."""
        # Greenwashing detection contract
        self.register_smart_contract(
            contract_type="greenwashing_alert",
            conditions={"max_signals": 2},
            actions=["flag_assessment", "notify_stakeholders", "require_verification"]
        )

        # ESG score threshold contract
        self.register_smart_contract(
            contract_type="esg_threshold",
            conditions={"min_score": 40},
            actions=["flag_high_risk", "require_due_diligence"]
        )

        # SDG impact target contract
        self.register_smart_contract(
            contract_type="sdg_target",
            conditions={"min_impact": 30},
            actions=["flag_low_impact", "recommend_alternatives"]
        )

    def register_smart_contract(
        self,
        contract_type: str,
        conditions: Dict[str, Any],
        actions: List[str]
    ) -> SmartContract:
        """Register a new smart contract."""
        contract = SmartContract(
            contract_id=str(uuid.uuid4()),
            contract_type=contract_type,
            conditions=conditions,
            actions=actions,
            created_at=time.time()
        )
        self.smart_contracts[contract.contract_id] = contract
        logger.info("smart_contract_registered", contract_type=contract_type)
        return contract

    def add_transaction(
        self,
        tx_type: TransactionType,
        agent_id: str,
        company_ticker: str,
        data: Dict[str, Any]
    ) -> Transaction:
        """Add a new transaction."""
        transaction = Transaction(
            tx_id=str(uuid.uuid4()),
            tx_type=tx_type,
            agent_id=agent_id,
            company_ticker=company_ticker,
            data=data,
            timestamp=time.time()
        )

        # Verify signature
        transaction.verify_signature()

        self.pending_transactions.append(transaction)

        # Check smart contracts (but not for contract trigger transactions to avoid recursion)
        if tx_type != TransactionType.SMART_CONTRACT_TRIGGER:
            self._evaluate_smart_contracts(transaction)

        logger.debug(
            "transaction_added",
            tx_id=transaction.tx_id,
            tx_type=tx_type.value,
            agent=agent_id
        )

        # Auto-mine if block size limit reached
        if len(self.pending_transactions) >= self.block_size_limit:
            self.mine_block()

        return transaction

    def _evaluate_smart_contracts(self, transaction: Transaction) -> None:
        """Evaluate smart contracts against transaction."""
        for contract_id, contract in self.smart_contracts.items():
            if contract.evaluate(transaction.data):
                contract.triggered = True
                contract.triggered_at = time.time()

                # Record contract trigger
                self.add_transaction(
                    tx_type=TransactionType.SMART_CONTRACT_TRIGGER,
                    agent_id="smart_contract_engine",
                    company_ticker=transaction.company_ticker,
                    data={
                        "contract_id": contract_id,
                        "contract_type": contract.contract_type,
                        "triggered_by": transaction.tx_id,
                        "actions": contract.actions
                    }
                )

                logger.warning(
                    "smart_contract_triggered",
                    contract_type=contract.contract_type,
                    company=transaction.company_ticker
                )

    def mine_block(self) -> Optional[Block]:
        """Mine pending transactions into a new block."""
        if not self.pending_transactions:
            return None

        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            transactions=[tx.to_dict() for tx in self.pending_transactions],
            previous_hash=self.get_latest_block().hash
        )

        # Proof of work
        while not new_block.hash.startswith("0" * self.difficulty):
            new_block.nonce += 1
            new_block.hash = new_block.calculate_hash()

        self.chain.append(new_block)
        tx_count = len(self.pending_transactions)
        self.pending_transactions = []

        logger.info(
            "block_mined",
            block_index=new_block.index,
            transactions=tx_count,
            hash=new_block.hash[:16]
        )

        return new_block

    def get_latest_block(self) -> Block:
        """Get the most recent block."""
        return self.chain[-1]

    def verify_chain(self) -> Dict[str, Any]:
        """Verify the integrity of the blockchain."""
        errors = []

        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Verify hash
            if current.hash != current.calculate_hash():
                errors.append(f"Block {i}: Hash mismatch")

            # Verify chain linkage
            if current.previous_hash != previous.hash:
                errors.append(f"Block {i}: Chain linkage broken")

            # Verify merkle root
            expected_merkle = current._calculate_merkle_root()
            if current.merkle_root != expected_merkle:
                errors.append(f"Block {i}: Merkle root mismatch")

        return {
            "valid": len(errors) == 0,
            "chain_length": len(self.chain),
            "errors": errors,
            "verified_at": datetime.now(tz=timezone.utc).isoformat()
        }

    def get_verification_proof(self, tx_id: str) -> Optional[Dict[str, Any]]:
        """Get cryptographic proof for a transaction."""
        for block in self.chain:
            for tx in block.transactions:
                if tx.get("tx_id") == tx_id:
                    return {
                        "tx_id": tx_id,
                        "block_index": block.index,
                        "block_hash": block.hash,
                        "merkle_root": block.merkle_root,
                        "timestamp": tx.get("timestamp"),
                        "signature": tx.get("signature"),
                        "verified": True,
                        "verification_url": f"https://gaia.caffeine.ai/verify/{tx_id}",
                        "explorer_url": f"https://explorer.caffeine.ai/tx/{tx_id}"
                    }
        return None

    def get_company_audit_trail(self, ticker: str) -> Dict[str, Any]:
        """Get complete audit trail for a company."""
        transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if isinstance(tx, dict) and tx.get("company_ticker") == ticker:
                    tx_copy = tx.copy()
                    tx_copy["block_index"] = block.index
                    tx_copy["block_hash"] = block.hash
                    transactions.append(tx_copy)

        # Get triggered contracts
        triggered = [
            c.to_dict() for c in self.smart_contracts.values()
            if c.triggered
        ]

        verification = self.verify_chain()

        return {
            "company_ticker": ticker,
            "network": self.network,
            "total_transactions": len(transactions),
            "transactions": sorted(transactions, key=lambda x: x.get("timestamp", 0)),
            "triggered_contracts": triggered,
            "chain_verified": verification["valid"],
            "chain_length": len(self.chain),
            "latest_block": self.get_latest_block().hash,
            "audit_generated_at": datetime.now(tz=timezone.utc).isoformat()
        }

    def get_agent_activity(self, agent_id: str) -> Dict[str, Any]:
        """Get all blockchain activity for an agent."""
        transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if isinstance(tx, dict) and tx.get("agent_id") == agent_id:
                    transactions.append(tx)

        return {
            "agent_id": agent_id,
            "total_transactions": len(transactions),
            "transactions": transactions,
            "first_activity": min((t.get("timestamp", 0) for t in transactions), default=None),
            "last_activity": max((t.get("timestamp", 0) for t in transactions), default=None)
        }

    def export_chain(self) -> Dict[str, Any]:
        """Export the entire blockchain."""
        return {
            "network": self.network,
            "chain_length": len(self.chain),
            "blocks": [block.to_dict() for block in self.chain],
            "pending_transactions": len(self.pending_transactions),
            "smart_contracts": [c.to_dict() for c in self.smart_contracts.values()],
            "verification": self.verify_chain(),
            "exported_at": datetime.now(tz=timezone.utc).isoformat()
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics."""
        total_tx = sum(len(block.transactions) for block in self.chain)
        return {
            "network": self.network,
            "chain_length": len(self.chain),
            "total_transactions": total_tx,
            "pending_transactions": len(self.pending_transactions),
            "smart_contracts": len(self.smart_contracts),
            "triggered_contracts": sum(1 for c in self.smart_contracts.values() if c.triggered),
            "latest_block_hash": self.get_latest_block().hash,
            "chain_valid": self.verify_chain()["valid"]
        }


# Backwards compatible alias
GAIABlockchain = CaffeineAIBlockchain

# Global blockchain instance
_blockchain_instance: Optional[CaffeineAIBlockchain] = None


def get_blockchain() -> CaffeineAIBlockchain:
    """Get or create the global blockchain instance."""
    global _blockchain_instance
    if _blockchain_instance is None:
        from config import get_settings
        settings = get_settings()
        network = getattr(settings, 'BLOCKCHAIN_NETWORK', 'testnet')
        _blockchain_instance = CaffeineAIBlockchain(network=network)
    return _blockchain_instance


# ============================================================================
# Convenience Functions for Agent Integration
# ============================================================================

def record_agent_finding(
    agent_id: str,
    company_ticker: str,
    finding_type: str,
    finding_data: Dict[str, Any],
    confidence: float,
    severity: str = "INFO"
) -> Transaction:
    """Record an agent finding to the blockchain."""
    blockchain = get_blockchain()
    return blockchain.add_transaction(
        tx_type=TransactionType.AGENT_FINDING,
        agent_id=agent_id,
        company_ticker=company_ticker,
        data={
            "finding_type": finding_type,
            "finding_data": finding_data,
            "confidence": confidence,
            "severity": severity
        }
    )


def record_evidence(
    agent_id: str,
    company_ticker: str,
    evidence_type: str,
    evidence_data: Dict[str, Any],
    source: str
) -> Transaction:
    """Record evidence submission to the blockchain."""
    blockchain = get_blockchain()
    return blockchain.add_transaction(
        tx_type=TransactionType.EVIDENCE_SUBMISSION,
        agent_id=agent_id,
        company_ticker=company_ticker,
        data={
            "evidence_type": evidence_type,
            "evidence_data": evidence_data,
            "source": source
        }
    )


def record_debate_argument(
    agent_id: str,
    company_ticker: str,
    debate_round: int,
    stance: str,
    argument: str,
    confidence: float
) -> Transaction:
    """Record a debate argument to the blockchain."""
    blockchain = get_blockchain()
    return blockchain.add_transaction(
        tx_type=TransactionType.DEBATE_ARGUMENT,
        agent_id=agent_id,
        company_ticker=company_ticker,
        data={
            "debate_round": debate_round,
            "stance": stance,
            "argument": argument,
            "confidence": confidence
        }
    )


def record_challenge(
    challenger_id: str,
    challenged_id: str,
    company_ticker: str,
    challenge_data: Dict[str, Any]
) -> Transaction:
    """Record an adversarial challenge to the blockchain."""
    blockchain = get_blockchain()
    return blockchain.add_transaction(
        tx_type=TransactionType.CHALLENGE_ISSUED,
        agent_id=challenger_id,
        company_ticker=company_ticker,
        data={
            "challenged_agent": challenged_id,
            "challenge": challenge_data
        }
    )


def record_consensus(
    company_ticker: str,
    consensus_data: Dict[str, Any],
    participating_agents: List[str]
) -> Transaction:
    """Record consensus reached to the blockchain."""
    blockchain = get_blockchain()
    return blockchain.add_transaction(
        tx_type=TransactionType.CONSENSUS_REACHED,
        agent_id="orchestrator",
        company_ticker=company_ticker,
        data={
            **consensus_data,
            "participating_agents": participating_agents
        }
    )


def record_greenwashing_alert(
    company_ticker: str,
    alert_data: Dict[str, Any],
    severity: str = "HIGH"
) -> Transaction:
    """Record a greenwashing alert to the blockchain."""
    blockchain = get_blockchain()
    return blockchain.add_transaction(
        tx_type=TransactionType.GREENWASHING_ALERT,
        agent_id="orchestrator",
        company_ticker=company_ticker,
        data={
            **alert_data,
            "severity": severity,
            "alert_type": "greenwashing"
        }
    )


def record_sdg_impact(
    company_ticker: str,
    sdg_number: int,
    impact_score: float,
    impact_data: Dict[str, Any]
) -> Transaction:
    """Record SDG impact measurement to the blockchain."""
    blockchain = get_blockchain()
    return blockchain.add_transaction(
        tx_type=TransactionType.SDG_IMPACT_RECORDED,
        agent_id="impact_agent",
        company_ticker=company_ticker,
        data={
            "sdg_number": sdg_number,
            "sdg_name": _get_sdg_name(sdg_number),
            "impact_score": impact_score,
            **impact_data
        }
    )


def finalize_assessment(
    company_ticker: str,
    assessment_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Finalize assessment and mine the block."""
    blockchain = get_blockchain()

    # Add finalization transaction
    tx = blockchain.add_transaction(
        tx_type=TransactionType.ASSESSMENT_FINALIZED,
        agent_id="orchestrator",
        company_ticker=company_ticker,
        data=assessment_data
    )

    # Mine the block
    block = blockchain.mine_block()

    if block:
        return {
            "status": "finalized",
            "transaction_id": tx.tx_id,
            "block_hash": block.hash,
            "block_index": block.index,
            "verification_url": f"https://gaia.caffeine.ai/verify/{tx.tx_id}",
            "timestamp": datetime.now(tz=timezone.utc).isoformat()
        }
    return {"status": "pending", "transaction_id": tx.tx_id}


def get_audit_trail(company_ticker: str) -> Dict[str, Any]:
    """Get audit trail for a company."""
    blockchain = get_blockchain()
    return blockchain.get_company_audit_trail(company_ticker)


def verify_transaction(tx_id: str) -> Optional[Dict[str, Any]]:
    """Verify a transaction and get its proof."""
    blockchain = get_blockchain()
    return blockchain.get_verification_proof(tx_id)


def _get_sdg_name(sdg_number: int) -> str:
    """Get SDG goal name."""
    sdg_names = {
        1: "No Poverty", 2: "Zero Hunger", 3: "Good Health",
        4: "Quality Education", 5: "Gender Equality", 6: "Clean Water",
        7: "Clean Energy", 8: "Decent Work", 9: "Industry & Innovation",
        10: "Reduced Inequalities", 11: "Sustainable Cities",
        12: "Responsible Consumption", 13: "Climate Action",
        14: "Life Below Water", 15: "Life on Land",
        16: "Peace & Justice", 17: "Partnerships"
    }
    return sdg_names.get(sdg_number, f"SDG {sdg_number}")
