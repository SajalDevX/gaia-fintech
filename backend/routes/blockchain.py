"""
GAIA Blockchain API Routes
Caffeine AI-powered audit trail and verification endpoints.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
import structlog

from utils.blockchain import (
    get_blockchain,
    get_audit_trail,
    verify_transaction
)

logger = structlog.get_logger()
router = APIRouter()


@router.get("/status", summary="Get blockchain status")
async def get_blockchain_status() -> Dict[str, Any]:
    """
    Get the current status of the GAIA blockchain.

    Returns blockchain statistics including chain length,
    transaction counts, and smart contract status.
    """
    blockchain = get_blockchain()
    return blockchain.get_stats()


@router.get("/chain", summary="Export full blockchain")
async def export_blockchain() -> Dict[str, Any]:
    """
    Export the entire blockchain with all blocks and transactions.

    Used for auditing and external verification.
    """
    blockchain = get_blockchain()
    return blockchain.export_chain()


@router.get("/verify", summary="Verify blockchain integrity")
async def verify_blockchain() -> Dict[str, Any]:
    """
    Verify the integrity of the entire blockchain.

    Checks hash validity, chain linkage, and Merkle roots.
    """
    blockchain = get_blockchain()
    return blockchain.verify_chain()


@router.get("/audit/{ticker}", summary="Get company audit trail")
async def get_company_audit(ticker: str) -> Dict[str, Any]:
    """
    Get the complete blockchain audit trail for a company.

    Args:
        ticker: Company stock ticker symbol

    Returns:
        Complete audit trail with all transactions, debates,
        and smart contract triggers for the company.
    """
    try:
        audit = get_audit_trail(ticker.upper())
        if not audit or audit.get("total_transactions", 0) == 0:
            return {
                "company_ticker": ticker.upper(),
                "message": "No blockchain records found for this company",
                "total_transactions": 0
            }
        return audit
    except Exception as e:
        logger.error("audit_trail_error", ticker=ticker, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tx/{transaction_id}", summary="Verify transaction")
async def verify_tx(transaction_id: str) -> Dict[str, Any]:
    """
    Verify a specific transaction and get its cryptographic proof.

    Args:
        transaction_id: UUID of the transaction

    Returns:
        Transaction verification proof including block hash,
        Merkle root, and verification URLs.
    """
    proof = verify_transaction(transaction_id)
    if not proof:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction {transaction_id} not found"
        )
    return proof


@router.get("/agent/{agent_id}", summary="Get agent activity")
async def get_agent_blockchain_activity(agent_id: str) -> Dict[str, Any]:
    """
    Get all blockchain activity for a specific agent.

    Args:
        agent_id: Agent identifier (e.g., 'sentinel', 'pulse')

    Returns:
        All transactions created by the agent.
    """
    blockchain = get_blockchain()
    return blockchain.get_agent_activity(agent_id)


@router.get("/contracts", summary="List smart contracts")
async def list_smart_contracts() -> Dict[str, Any]:
    """
    List all registered ESG compliance smart contracts.

    Returns:
        List of smart contracts with their conditions,
        actions, and trigger status.
    """
    blockchain = get_blockchain()
    return {
        "contracts": [c.to_dict() for c in blockchain.smart_contracts.values()],
        "total": len(blockchain.smart_contracts),
        "triggered": sum(1 for c in blockchain.smart_contracts.values() if c.triggered)
    }


@router.get("/block/{block_index}", summary="Get block by index")
async def get_block(block_index: int) -> Dict[str, Any]:
    """
    Get a specific block by its index.

    Args:
        block_index: Block number in the chain

    Returns:
        Block details including transactions and hash.
    """
    blockchain = get_blockchain()
    if block_index < 0 or block_index >= len(blockchain.chain):
        raise HTTPException(
            status_code=404,
            detail=f"Block {block_index} not found. Chain length: {len(blockchain.chain)}"
        )
    return blockchain.chain[block_index].to_dict()


@router.get("/latest", summary="Get latest block")
async def get_latest_block() -> Dict[str, Any]:
    """
    Get the most recent block in the chain.

    Returns:
        Latest block with all its details.
    """
    blockchain = get_blockchain()
    return blockchain.get_latest_block().to_dict()
