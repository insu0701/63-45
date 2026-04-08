from fastapi import APIRouter

from backend.app.api.routes.allocation import router as allocation_router
from backend.app.api.routes.holdings import router as holdings_router
from backend.app.api.routes.imports import router as imports_router
from backend.app.api.routes.overview import router as overview_router
from backend.app.api.routes.strategy import router as strategy_router
from backend.app.api.routes.sync import router as sync_router

api_router = APIRouter()
api_router.include_router(overview_router)
api_router.include_router(holdings_router)
api_router.include_router(allocation_router)
api_router.include_router(sync_router)
api_router.include_router(imports_router)
api_router.include_router(strategy_router)