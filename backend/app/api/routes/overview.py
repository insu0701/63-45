from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.api.response import build_response
from backend.app.services.concentration_service import ConcentrationService
from backend.app.services.exposure_service import ExposureService
from backend.app.services.valuation_service import ValuationService

router = APIRouter(prefix="/api/v1/overview", tags=["overview"])


def _to_float(value: Decimal | None) -> float:
    return float(value or 0)


@router.get("")
def get_overview(db: Session = Depends(get_db)):
    valuation = ValuationService(db)
    exposure = ExposureService(db)

    summary = valuation.get_portfolio_summary()
    sleeve_exposures = exposure.get_sleeve_exposures()
    cash_rows = valuation.get_cash_valuations()

    sleeve_map = {row.sleeve: row for row in sleeve_exposures}
    cash_map = {row.currency: row for row in cash_rows}

    data = {
        "total_equity_value_base": _to_float(summary.total_equity_value_base),
        "total_cash_base": _to_float(summary.total_cash_base),
        "total_nav_base": _to_float(summary.total_nav_base),
        "total_unrealized_pnl_base": _to_float(summary.total_unrealized_pnl_base),
        "total_unrealized_return_pct": _to_float(summary.total_unrealized_return_pct),
        "kr_equity_value_base": _to_float(sleeve_map.get("KR").market_value_base if sleeve_map.get("KR") else 0),
        "us_equity_value_base": _to_float(sleeve_map.get("US").market_value_base if sleeve_map.get("US") else 0),
        "krw_cash_base": _to_float(cash_map.get("KRW").amount_base if cash_map.get("KRW") else 0),
        "usd_cash_base": _to_float(cash_map.get("USD").amount_base if cash_map.get("USD") else 0),
    }

    snapshot_time = valuation.get_latest_holdings_snapshot_time() or valuation.get_latest_cash_snapshot_time()
    return build_response(data=data, snapshot_time=snapshot_time)


@router.get("/top-holdings")
def get_top_holdings(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    valuation = ValuationService(db)
    summary = valuation.get_portfolio_summary()
    positions = valuation.get_position_valuations()

    total_nav = summary.total_nav_base
    items = []

    for p in positions[:limit]:
        weight = Decimal("0") if total_nav == 0 else p.market_value_base / total_nav
        items.append(
            {
                "symbol": p.symbol,
                "security_name": p.security_name,
                "sleeve": p.sleeve,
                "country": p.country,
                "market_value_base": _to_float(p.market_value_base),
                "cost_basis_base": _to_float(p.cost_basis_base),
                "unrealized_pnl_base": _to_float(p.unrealized_pnl_base),
                "unrealized_return_pct": _to_float(p.unrealized_return_pct),
                "weight_of_total_nav": _to_float(weight),
            }
        )

    snapshot_time = valuation.get_latest_holdings_snapshot_time()
    return build_response(data=items, snapshot_time=snapshot_time)


@router.get("/concentration")
def get_concentration(db: Session = Depends(get_db)):
    valuation = ValuationService(db)
    concentration = ConcentrationService(db)
    metrics = concentration.get_metrics()

    data = {
        "top1_pct": _to_float(metrics.top1_pct),
        "top3_pct": _to_float(metrics.top3_pct),
        "top5_pct": _to_float(metrics.top5_pct),
        "largest_sector_pct": _to_float(metrics.largest_sector_pct),
        "largest_sleeve_pct": _to_float(metrics.largest_sleeve_pct),
    }

    snapshot_time = valuation.get_latest_holdings_snapshot_time()
    return build_response(data=data, snapshot_time=snapshot_time)