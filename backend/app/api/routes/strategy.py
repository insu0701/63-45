from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.api.response import build_response
from backend.app.services.strategy_overlay_service import StrategyOverlayService

router = APIRouter(prefix="/api/v1/strategy", tags=["strategy"])


def _to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


@router.get("/overlay")
def get_strategy_overlay(
    sleeve: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = StrategyOverlayService(db)
    rows = service.get_overlay_rows(sleeve=sleeve)

    data = [
        {
            "symbol": row.symbol,
            "security_name": row.security_name,
            "sleeve": row.sleeve,
            "market": row.market,
            "country": row.country,
            "current_market_value_base": _to_float(row.current_market_value_base) or 0.0,
            "current_weight_of_nav": _to_float(row.current_weight_of_nav) or 0.0,
            "strategy_state": row.strategy_state,
            "target_state": row.target_state,
            "target_weight": _to_float(row.target_weight),
            "target_dollars": _to_float(row.target_dollars),
            "actual_position_dollars": _to_float(row.actual_position_dollars),
            "actual_vs_target_delta": _to_float(row.actual_vs_target_delta),
            "eligibility_status": row.eligibility_status,
            "buy_list_status": row.buy_list_status,
            "reason_code": row.reason_code,
            "as_of_date": row.as_of_date.isoformat() if row.as_of_date else None,
        }
        for row in rows
    ]

    return build_response(data=data, snapshot_time=None)


@router.get("/decision-log")
def get_decision_log(
    limit: int = Query(default=50, ge=1, le=500),
    sleeve: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    service = StrategyOverlayService(db)
    rows = service.get_recent_decision_logs(limit=limit, sleeve=sleeve)

    data = [
        {
            "decision_date": row.decision_date.isoformat(),
            "symbol": row.symbol,
            "market": row.market,
            "sleeve": row.sleeve,
            "sector": row.sector,
            "eligibility_status": row.eligibility_status,
            "buy_list_status": row.buy_list_status,
            "current_state": row.current_state,
            "target_state": row.target_state,
            "current_position_dollars": _to_float(row.current_position_dollars),
            "target_position_dollars": _to_float(row.target_position_dollars),
            "generated_order_quantity": _to_float(row.generated_order_quantity),
            "fill_quantity": _to_float(row.fill_quantity),
            "rejection_status": row.rejection_status,
            "reason_code": row.reason_code,
            "decision_timestamp": row.decision_timestamp.isoformat() if row.decision_timestamp else None,
        }
        for row in rows
    ]

    return build_response(data=data, snapshot_time=None)