"""
GAIA Blockchain Audit Trail Simulation
Simulates immutable audit trail for agent decisions and evidence
"""

import hashlib
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import uuid


class TransactionType(Enum):
    """Types of blockchain transactions."""
    AGENT_FINDING = "agent_finding"
    EVIDENCE_SUBMISSION = "evidence_submission"
    CHALLENGE_ISSUED = "challenge_issued"
    CHALLENGE_RESPONSE = "challenge_response"
    CONSENSUS_REACHED = "consensus_reached"
    ASSESSMENT_FINALIZED = "assessment_finalized"
    GREENWASHING_ALERT = "greenwashing_alert"


@dataclass
class Block:
    """Represents a block in the blockchain."""
    index: int
    timestamp: float
    transactions: List[Dict[str, Any]]
    previous_hash: str
    nonce: int = 0
    hash: str = field(default="", init=False)

    def __post_init__(self):
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate SHA-256 hash of block contents."""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary."""
        return asdict(self)


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

    def __post_init__(self):
        self.signature = self._generate_signature()

    def _generate_signature(self) -> str:
        """Generate transaction signature."""
        content = f"{self.tx_id}{self.agent_id}{self.company_ticker}{json.dumps(self.data, sort_keys=True)}{self.timestamp}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary."""
        return {
            "tx_id": self.tx_id,
            "tx_type": self.tx_type.value,
            "agent_id": self.agent_id,
            "company_ticker": self.company_ticker,
            "data": self.data,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat()
        }


class GAIABlockchain:
    """
    Simulated blockchain for GAIA audit trail.
    Provides immutable record of all agent decisions and evidence.
    """

    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = 2  # Number of leading zeros required in hash
        self._create_genesis_block()

    def _create_genesis_block(self) -> None:
        """Create the genesis (first) block."""
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[{
                "message": "GAIA Genesis Block - Sustainable Finance Truth Engine",
                "created": datetime.now().isoformat()
            }],
            previous_hash="0" * 64
        )
        self.chain.append(genesis_block)

    def get_latest_block(self) -> Block:
        """Get the most recent block in the chain."""
        return self.chain[-1]

    def add_transaction(
        self,
        tx_type: TransactionType,
        agent_id: str,
        company_ticker: str,
        data: Dict[str, Any]
    ) -> Transaction:
        """Add a new transaction to pending transactions."""
        transaction = Transaction(
            tx_id=str(uuid.uuid4()),
            tx_type=tx_type,
            agent_id=agent_id,
            company_ticker=company_ticker,
            data=data,
            timestamp=time.time()
        )
        self.pending_transactions.append(transaction)
        return transaction

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

        # Simple proof of work (simulated)
        while not new_block.hash.startswith("0" * self.difficulty):
            new_block.nonce += 1
            new_block.hash = new_block.calculate_hash()

        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def verify_chain(self) -> bool:
        """Verify the integrity of the blockchain."""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Verify hash
            if current_block.hash != current_block.calculate_hash():
                return False

            # Verify chain linkage
            if current_block.previous_hash != previous_block.hash:
                return False

        return True

    def get_transactions_by_company(self, ticker: str) -> List[Dict[str, Any]]:
        """Get all transactions for a specific company."""
        transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if isinstance(tx, dict) and tx.get("company_ticker") == ticker:
                    transactions.append(tx)
        return transactions

    def get_transactions_by_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get all transactions by a specific agent."""
        transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if isinstance(tx, dict) and tx.get("agent_id") == agent_id:
                    transactions.append(tx)
        return transactions

    def get_audit_trail(self, company_ticker: str) -> Dict[str, Any]:
        """Get complete audit trail for a company analysis."""
        transactions = self.get_transactions_by_company(company_ticker)

        return {
            "company_ticker": company_ticker,
            "total_transactions": len(transactions),
            "blockchain_verified": self.verify_chain(),
            "transactions": sorted(transactions, key=lambda x: x.get("timestamp", 0)),
            "chain_length": len(self.chain),
            "latest_block_hash": self.get_latest_block().hash
        }

    def export_chain(self) -> List[Dict[str, Any]]:
        """Export the entire blockchain."""
        return [block.to_dict() for block in self.chain]


# Global blockchain instance
_blockchain_instance: Optional[GAIABlockchain] = None


def get_blockchain() -> GAIABlockchain:
    """Get or create the global blockchain instance."""
    global _blockchain_instance
    if _blockchain_instance is None:
        _blockchain_instance = GAIABlockchain()
    return _blockchain_instance


def record_agent_finding(
    agent_id: str,
    company_ticker: str,
    finding_type: str,
    finding_data: Dict[str, Any],
    confidence: float
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
    consensus_data: Dict[str, Any]
) -> Transaction:
    """Record consensus reached to the blockchain."""
    blockchain = get_blockchain()
    return blockchain.add_transaction(
        tx_type=TransactionType.CONSENSUS_REACHED,
        agent_id="orchestrator",
        company_ticker=company_ticker,
        data=consensus_data
    )


def record_greenwashing_alert(
    company_ticker: str,
    alert_data: Dict[str, Any]
) -> Transaction:
    """Record a greenwashing alert to the blockchain."""
    blockchain = get_blockchain()
    return blockchain.add_transaction(
        tx_type=TransactionType.GREENWASHING_ALERT,
        agent_id="orchestrator",
        company_ticker=company_ticker,
        data=alert_data
    )


def finalize_assessment(
    company_ticker: str,
    assessment_data: Dict[str, Any]
) -> str:
    """Finalize assessment and mine the block."""
    blockchain = get_blockchain()
    blockchain.add_transaction(
        tx_type=TransactionType.ASSESSMENT_FINALIZED,
        agent_id="orchestrator",
        company_ticker=company_ticker,
        data=assessment_data
    )
    block = blockchain.mine_block()
    return block.hash if block else ""
