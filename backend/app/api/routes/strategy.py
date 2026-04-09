from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.api.response import build_response
from backend.app.core.strategy_options import (
    BUY_LIST_STATUS_OPTIONS,
    ELIGIBILITY_STATUS_OPTIONS,
    REASON_CODE_OPTIONS,
    STRATEGY_STATE_OPTIONS,
    TARGET_STATE_OPTIONS,
)
from backend.app.schemas.strategy import ManualStrategyOverlayUpsertRequest
from backend.app.services.manual_strategy_service import ManualStrategyService
from backend.app.services.strategy_overlay_service import StrategyOverlayService

router = APIRouter(prefix="/api/v1/strategy", tags=["strategy"])


def _to_float(value: Decimal | None) -> float | None:
    if value is None:
        return None
    return float(value)


@router.get("/options")
def get_strategy_options():
    data = {
        "strategy_state_options": STRATEGY_STATE_OPTIONS,
        "target_state_options": TARGET_STATE_OPTIONS,
        "eligibility_status_options": ELIGIBILITY_STATUS_OPTIONS,
        "buy_list_status_options": BUY_LIST_STATUS_OPTIONS,
        "reason_codes": REASON_CODE_OPTIONS,
    }
    return build_response(data=data, snapshot_time=None)


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


@router.get("/review")
def get_strategy_review(
    sleeve: str | None = Query(default=None),
    min_abs_delta: float = Query(default=1000, ge=0),
    limit: int = Query(default=25, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = StrategyOverlayService(db)
    metrics, candidates = service.get_review_metrics_and_candidates(
        sleeve=sleeve,
        min_abs_delta=Decimal(str(min_abs_delta)),
        limit=limit,
    )

    data = {
        "metrics": {
            "overlay_row_count": metrics.overlay_row_count,
            "rows_with_target": metrics.rows_with_target,
            "rows_without_target": metrics.rows_without_target,
            "rows_with_delta": metrics.rows_with_delta,
            "on_target_count": metrics.on_target_count,
            "add_count": metrics.add_count,
            "trim_count": metrics.trim_count,
            "exit_count": metrics.exit_count,
            "gross_abs_delta_dollars": float(metrics.gross_abs_delta_dollars),
            "net_delta_dollars": float(metrics.net_delta_dollars),
        },
        "candidates": [
            {
                "symbol": row.symbol,
                "security_name": row.security_name,
                "sleeve": row.sleeve,
                "market": row.market,
                "country": row.country,
                "current_market_value_base": float(row.current_market_value_base),
                "target_dollars": float(row.target_dollars),
                "actual_vs_target_delta": float(row.actual_vs_target_delta),
                "abs_delta_dollars": float(row.abs_delta_dollars),
                "current_weight_of_nav": float(row.current_weight_of_nav),
                "target_weight": _to_float(row.target_weight),
                "strategy_state": row.strategy_state,
                "target_state": row.target_state,
                "reason_code": row.reason_code,
                "suggested_action": row.suggested_action,
            }
            for row in candidates
        ],
    }

    return build_response(data=data, snapshot_time=None)


@router.post("/overlay/manual")
def upsert_manual_strategy_overlay(
    payload: ManualStrategyOverlayUpsertRequest,
    db: Session = Depends(get_db),
):
    service = ManualStrategyService(db)
    result = service.upsert_overlay(
        symbol=payload.symbol,
        sleeve=payload.sleeve,
        strategy_state=payload.strategy_state,
        target_state=payload.target_state,
        target_weight=payload.target_weight,
        target_dollars=payload.target_dollars,
        eligibility_status=payload.eligibility_status,
        buy_list_status=payload.buy_list_status,
        reason_code=payload.reason_code,
        notes=payload.notes,
        append_decision_log=payload.append_decision_log,
    )

    data = {
        "overlay_id": result.overlay_id,
        "symbol": result.symbol,
        "sleeve": result.sleeve,
        "as_of_date": result.as_of_date.isoformat(),
        "reason_code": result.reason_code,
        "actual_position_dollars": float(result.actual_position_dollars),
        "target_dollars": _to_float(result.target_dollars),
        "actual_vs_target_delta": _to_float(result.actual_vs_target_delta),
        "decision_log_written": result.decision_log_written,
    }

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