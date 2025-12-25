"""
GAIA Analysis Routes
Main analysis endpoints with WebSocket support for real-time updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import structlog
import asyncio
import json
from uuid import uuid4

from services.analysis_service import AnalysisService, get_analysis_service
from config import get_settings

logger = structlog.get_logger()
settings = get_settings()

router = APIRouter()


# Request/Response Models

class AnalysisRequest(BaseModel):
    """Request model for company analysis."""
    ticker: str = Field(..., description="Company stock ticker symbol", min_length=1, max_length=10)
    company_name: Optional[str] = Field(None, description="Company name (optional)")
    include_satellite: bool = Field(True, description="Include satellite imagery analysis")
    include_sentiment: bool = Field(True, description="Include sentiment analysis")
    include_supply_chain: bool = Field(True, description="Include supply chain analysis")
    debate_rounds: Optional[int] = Field(None, description="Number of adversarial debate rounds", ge=1, le=10)

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "include_satellite": True,
                "include_sentiment": True,
                "include_supply_chain": True,
                "debate_rounds": 3
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for analysis initiation."""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    status: str = Field(..., description="Current status of analysis")
    ticker: str = Field(..., description="Company ticker")
    message: str = Field(..., description="Status message")
    websocket_url: str = Field(..., description="WebSocket URL for real-time updates")
    estimated_duration: int = Field(..., description="Estimated duration in seconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnalysisStatus(BaseModel):
    """Status model for ongoing analysis."""
    analysis_id: str
    status: str
    progress: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    current_stage: str
    completed_agents: List[str] = Field(default_factory=list)
    pending_agents: List[str] = Field(default_factory=list)
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class AnalysisResult(BaseModel):
    """Complete analysis result."""
    analysis_id: str
    ticker: str
    company_name: str
    status: str
    overall_score: float = Field(..., ge=0.0, le=100.0)
    risk_level: str
    recommendation: str

    # ESG Scores
    esg_scores: Dict[str, float]
    environmental_score: float
    social_score: float
    governance_score: float

    # SDG Impact
    sdg_impact: Dict[int, float]
    top_sdgs: List[Dict[str, Any]]

    # Agent Results
    agent_results: Dict[str, Any]

    # Adversarial Debate
    debate_summary: Dict[str, Any]

    # Final Assessment
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]

    # Metadata
    created_at: datetime
    completed_at: datetime
    processing_time: float


# WebSocket Connection Manager

class ConnectionManager:
    """Manage WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, analysis_id: str, websocket: WebSocket):
        """Accept and store WebSocket connection."""
        await websocket.accept()
        if analysis_id not in self.active_connections:
            self.active_connections[analysis_id] = []
        self.active_connections[analysis_id].append(websocket)
        logger.info("websocket_connected", analysis_id=analysis_id)

    def disconnect(self, analysis_id: str, websocket: WebSocket):
        """Remove WebSocket connection."""
        if analysis_id in self.active_connections:
            self.active_connections[analysis_id].remove(websocket)
            if not self.active_connections[analysis_id]:
                del self.active_connections[analysis_id]
        logger.info("websocket_disconnected", analysis_id=analysis_id)

    def _serialize_for_json(self, obj: Any) -> Any:
        """Recursively serialize objects for JSON, handling datetime."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._serialize_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_for_json(item) for item in obj]
        return obj

    async def send_message(self, analysis_id: str, message: Dict[str, Any]):
        """Send message to all connections for an analysis."""
        if analysis_id in self.active_connections:
            # Serialize datetime objects before sending
            serialized_message = self._serialize_for_json(message)
            disconnected = []
            for connection in self.active_connections[analysis_id]:
                try:
                    await connection.send_json(serialized_message)
                except Exception as e:
                    logger.warning("websocket_send_error", error=str(e))
                    disconnected.append(connection)

            # Remove disconnected connections
            for connection in disconnected:
                self.disconnect(analysis_id, connection)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all active connections."""
        for analysis_id in list(self.active_connections.keys()):
            await self.send_message(analysis_id, message)


manager = ConnectionManager()


# Routes

@router.post("", response_model=AnalysisResponse, status_code=201)
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Start a new company ESG/SDG analysis.

    This endpoint initiates a comprehensive analysis of a company using multiple AI agents
    and adversarial debate methodology. The analysis runs asynchronously in the background.

    Args:
        request: Analysis request parameters
        background_tasks: FastAPI background tasks
        analysis_service: Injected analysis service

    Returns:
        AnalysisResponse with analysis ID and WebSocket URL for real-time updates

    Raises:
        HTTPException: If ticker is invalid or service is unavailable
    """
    try:
        logger.info(
            "starting_analysis",
            ticker=request.ticker,
            company_name=request.company_name
        )

        # Validate ticker format
        ticker = request.ticker.upper().strip()
        if not ticker:
            raise ValueError("Ticker symbol is required")

        # Generate unique analysis ID
        analysis_id = str(uuid4())

        # Determine debate rounds (use config default if not specified)
        debate_rounds = request.debate_rounds or settings.ADVERSARIAL_DEBATE_ROUNDS

        # Estimate duration (rough estimate based on agents and debate rounds)
        estimated_duration = 30 + (debate_rounds * 10)  # seconds

        # Create analysis task
        background_tasks.add_task(
            analysis_service.run_analysis,
            analysis_id=analysis_id,
            ticker=ticker,
            company_name=request.company_name,
            include_satellite=request.include_satellite,
            include_sentiment=request.include_sentiment,
            include_supply_chain=request.include_supply_chain,
            debate_rounds=debate_rounds,
            connection_manager=manager
        )

        # Construct WebSocket URL
        websocket_url = f"/ws/analyze/{analysis_id}"

        logger.info(
            "analysis_started",
            analysis_id=analysis_id,
            ticker=ticker
        )

        return AnalysisResponse(
            analysis_id=analysis_id,
            status="started",
            ticker=ticker,
            message=f"Analysis started for {ticker}",
            websocket_url=websocket_url,
            estimated_duration=estimated_duration
        )

    except ValueError as e:
        logger.warning("invalid_request", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error("analysis_start_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to start analysis. Please try again."
        )


@router.get("/{analysis_id}", response_model=AnalysisStatus)
async def get_analysis_status(
    analysis_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get the current status of an analysis.

    Args:
        analysis_id: Unique analysis identifier
        analysis_service: Injected analysis service

    Returns:
        AnalysisStatus with current progress and results (if completed)

    Raises:
        HTTPException: If analysis ID not found
    """
    try:
        logger.info("fetching_analysis_status", analysis_id=analysis_id)

        status = await analysis_service.get_analysis_status(analysis_id)

        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis {analysis_id} not found"
            )

        return status

    except HTTPException:
        raise

    except Exception as e:
        logger.error("status_fetch_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch analysis status"
        )


@router.get("/{analysis_id}/results", response_model=AnalysisResult)
async def get_analysis_results(
    analysis_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get the complete results of a completed analysis.

    Args:
        analysis_id: Unique analysis identifier
        analysis_service: Injected analysis service

    Returns:
        AnalysisResult with complete analysis data

    Raises:
        HTTPException: If analysis not found or not completed
    """
    try:
        logger.info("fetching_analysis_results", analysis_id=analysis_id)

        results = await analysis_service.get_analysis_results(analysis_id)

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis {analysis_id} not found"
            )

        if results.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Analysis {analysis_id} is not yet completed. Current status: {results.get('status')}"
            )

        return results

    except HTTPException:
        raise

    except Exception as e:
        logger.error("results_fetch_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch analysis results"
        )


@router.delete("/{analysis_id}", status_code=204)
async def cancel_analysis(
    analysis_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Cancel an ongoing analysis.

    Args:
        analysis_id: Unique analysis identifier
        analysis_service: Injected analysis service

    Raises:
        HTTPException: If analysis not found or already completed
    """
    try:
        logger.info("canceling_analysis", analysis_id=analysis_id)

        success = await analysis_service.cancel_analysis(analysis_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis {analysis_id} not found or already completed"
            )

        # Notify WebSocket clients
        await manager.send_message(
            analysis_id,
            {
                "type": "status",
                "status": "cancelled",
                "message": "Analysis cancelled by user"
            }
        )

        logger.info("analysis_cancelled", analysis_id=analysis_id)

    except HTTPException:
        raise

    except Exception as e:
        logger.error("cancel_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to cancel analysis"
        )


@router.websocket("/ws/{analysis_id}")
async def websocket_analysis_updates(
    websocket: WebSocket,
    analysis_id: str
):
    """
    WebSocket endpoint for real-time analysis updates.

    Clients connect to this endpoint to receive live updates about analysis progress,
    agent completions, debate results, and final assessment.

    Args:
        websocket: WebSocket connection
        analysis_id: Unique analysis identifier

    Message Types:
        - status: Status updates (started, in_progress, completed, failed)
        - progress: Progress percentage updates
        - agent_complete: Individual agent completion
        - debate_update: Adversarial debate round updates
        - result: Final analysis results
        - error: Error messages
    """
    await manager.connect(analysis_id, websocket)

    try:
        logger.info("websocket_session_started", analysis_id=analysis_id)

        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "analysis_id": analysis_id,
            "message": "Connected to analysis updates",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Keep connection alive and handle client messages
        while True:
            try:
                # Receive messages from client (e.g., ping/pong)
                data = await websocket.receive_text()

                # Handle client messages
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await websocket.send_json({
                            "type": "pong",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                except json.JSONDecodeError:
                    logger.warning("invalid_websocket_message", data=data)

            except WebSocketDisconnect:
                logger.info("websocket_client_disconnected", analysis_id=analysis_id)
                break

            except Exception as e:
                logger.error("websocket_error", error=str(e), exc_info=True)
                break

    except Exception as e:
        logger.error("websocket_session_error", error=str(e), exc_info=True)

    finally:
        manager.disconnect(analysis_id, websocket)
        logger.info("websocket_session_ended", analysis_id=analysis_id)


@router.get("/{analysis_id}/export/{format}")
async def export_analysis(
    analysis_id: str,
    format: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Export analysis results in various formats.

    Args:
        analysis_id: Unique analysis identifier
        format: Export format (json, pdf, csv, xlsx)
        analysis_service: Injected analysis service

    Returns:
        File download response

    Raises:
        HTTPException: If analysis not found or format not supported
    """
    try:
        logger.info("exporting_analysis", analysis_id=analysis_id, format=format)

        if format not in ["json", "pdf", "csv", "xlsx"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported export format: {format}"
            )

        # Get analysis results
        results = await analysis_service.get_analysis_results(analysis_id)

        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis {analysis_id} not found"
            )

        # For now, return JSON
        # TODO: Implement PDF, CSV, XLSX export
        if format == "json":
            return JSONResponse(content=results)
        else:
            raise HTTPException(
                status_code=501,
                detail=f"Export format {format} not yet implemented"
            )

    except HTTPException:
        raise

    except Exception as e:
        logger.error("export_error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to export analysis"
        )
