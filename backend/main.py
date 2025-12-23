"""
GAIA - Global AI-powered Impact Assessment
FastAPI Main Application
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import structlog
import time
from typing import Dict, Any

from config import get_settings
from routes import router

# Configure structured logging
logger = structlog.get_logger()

# Get settings
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info(
        "starting_application",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT
    )

    # Initialize services
    try:
        # Initialize database connection pool
        logger.info("initializing_database")

        # Initialize Redis connection
        logger.info("initializing_redis")

        # Initialize AI model connections
        logger.info("initializing_ai_models")

        # Initialize blockchain connection if enabled
        if settings.BLOCKCHAIN_ENABLED:
            logger.info("initializing_blockchain", network=settings.BLOCKCHAIN_NETWORK)

        logger.info("application_startup_complete")

    except Exception as e:
        logger.error("startup_error", error=str(e), exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("shutting_down_application")

    try:
        # Close database connections
        logger.info("closing_database_connections")

        # Close Redis connections
        logger.info("closing_redis_connections")

        # Cleanup AI model resources
        logger.info("cleaning_up_ai_resources")

        logger.info("application_shutdown_complete")

    except Exception as e:
        logger.error("shutdown_error", error=str(e), exc_info=True)


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Global AI-powered Impact Assessment System for ESG and SDG analysis",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# CORS Middleware Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing information."""
    start_time = time.time()

    # Log request
    logger.info(
        "incoming_request",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None
    )

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log response
    logger.info(
        "request_completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=f"{duration:.3f}s"
    )

    # Add custom headers
    response.headers["X-Process-Time"] = str(duration)

    return response


# Exception Handlers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed error messages."""
    logger.warning(
        "validation_error",
        path=request.url.path,
        errors=exc.errors()
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Request validation failed",
            "details": exc.errors(),
            "timestamp": time.time()
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        error=str(exc),
        exc_info=True
    )

    # Don't expose internal errors in production
    error_message = str(exc) if settings.DEBUG else "Internal server error"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": error_message,
            "timestamp": time.time()
        }
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle value errors (invalid input)."""
    logger.warning(
        "value_error",
        path=request.url.path,
        error=str(exc)
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "message": str(exc),
            "timestamp": time.time()
        }
    )


@app.exception_handler(PermissionError)
async def permission_error_handler(request: Request, exc: PermissionError):
    """Handle permission errors."""
    logger.warning(
        "permission_error",
        path=request.url.path,
        error=str(exc)
    )

    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "Forbidden",
            "message": str(exc),
            "timestamp": time.time()
        }
    )


# Include routers
app.include_router(router, prefix=settings.API_PREFIX)


# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        Dictionary with health status and system information
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": time.time()
    }


# Root Endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """
    Root endpoint with API information.

    Returns:
        Dictionary with API information
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "Global AI-powered Impact Assessment System",
        "documentation": "/docs",
        "health": "/health",
        "api_prefix": settings.API_PREFIX
    }


# Metrics endpoint (for Prometheus)
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Prometheus metrics endpoint.

    Returns:
        Metrics in Prometheus format
    """
    # This would integrate with prometheus_client
    # For now, return basic info
    return {
        "status": "metrics_endpoint",
        "note": "Integrate with prometheus_client for production"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )
