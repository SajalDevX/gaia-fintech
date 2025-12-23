"""
GAIA Routes Module
Router configuration and initialization
"""

from fastapi import APIRouter
from routes.analysis import router as analysis_router
from routes.companies import router as companies_router
from routes.sdg import router as sdg_router
from routes.inclusion import router as inclusion_router

# Create main router
router = APIRouter()

# Include all sub-routers
router.include_router(
    analysis_router,
    prefix="/analyze",
    tags=["Analysis"]
)

router.include_router(
    companies_router,
    prefix="/companies",
    tags=["Companies"]
)

router.include_router(
    sdg_router,
    prefix="/sdg",
    tags=["SDG"]
)

router.include_router(
    inclusion_router,
    prefix="/inclusion",
    tags=["Financial Inclusion"]
)

__all__ = ["router"]
