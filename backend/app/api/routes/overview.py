from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.api.response import build_response
from backend.app.core.config import settings
from backend.app.db.models import FxRateSnapshot
from backend.app.services.concentration_service import ConcentrationService
from backend.app.services.exposure_service import ExposureService
from backend.app.services.health_service import HealthService
from backend.app.services.valuation_service import ValuationService

router = APIRouter(prefix="/api/v1/overview", tags=["overview"])


def _to_float(value: Decimal | None) -> float:
    return float(value or 0)


def _latest_fx_row_for_base(db: Session, base_currency: str) -> FxRateSnapshot | None:
    if base_currency == "KRW":
        return None

    stmt = (
        select(FxRateSnapshot)
        .where(FxRateSnapshot.base_currency == "KRW")
        .where(FxRateSnapshot.quote_currency == base_currency)
        .order_by(FxRateSnapshot.rate_timestamp.desc(), FxRateSnapshot.id.desc())
        .limit(1)
    )
    return db.scalar(stmt)


@router.get("")
def get_overview(db: Session = Depends(get_db)):
    valuation = ValuationService(db)
    exposure = ExposureService(db)
    concentration = ConcentrationService(db)
    health = HealthService(db)

    summary = valuation.get_portfolio_summary()
    sleeve_exposures = exposure.get_sleeve_exposures()
    cash_rows = valuation.get_cash_valuations()
    source_statuses = health.get_data_source_statuses()

    sleeve_map = {row.sleeve: row for row in sleeve_exposures}
    cash_map = {row.currency: row for row in cash_rows}
    source_map = {row.source_key: row for row in source_statuses}

    base_currency = settings.base_currency.upper()
    fx_row = _latest_fx_row_for_base(db, base_currency)

    if base_currency == "KRW":
        fx_rate_krw_to_base = 1.0
        fx_rate_base_to_krw = 1.0
        fx_rate_timestamp = None
    else:
        fx_rate_krw_to_base = _to_float(fx_row.rate) if fx_row else 0.0
        fx_rate_base_to_krw = (
            float(Decimal("1") / fx_row.rate)
            if fx_row and fx_row.rate not in (None, 0)
            else 0.0
        )
        fx_rate_timestamp = (
            fx_row.rate_timestamp.isoformat()
            if fx_row and fx_row.rate_timestamp
            else (
                source_map["fx"].last_timestamp.isoformat()
                if source_map.get("fx") and source_map["fx"].last_timestamp
                else None
            )
        )

    data = {
        "total_equity_value_base": _to_float(summary.total_equity_value_base),
        "total_cash_base": _to_float(summary.total_cash_base),
        "total_nav_base": _to_float(summary.total_nav_base),
        "total_unrealized_pnl_base": _to_float(summary.total_unrealized_pnl_base),
        "total_unrealized_return_pct": _to_float(summary.total_unrealized_return_pct),
        "kr_equity_value_base": _to_float(
            sleeve_map.get("KR").equity_value_base if sleeve_map.get("KR") else 0
        ),
        "us_equity_value_base": _to_float(
            sleeve_map.get("US").equity_value_base if sleeve_map.get("US") else 0
        ),
        "krw_cash_base": _to_float(
            cash_map.get("KRW").amount_base if cash_map.get("KRW") else 0
        ),
        "usd_cash_base": _to_float(
            cash_map.get("USD").amount_base if cash_map.get("USD") else 0
        ),
        "cash_currency": {
            "base_currency": base_currency,
            "krw_cash_native": _to_float(
                cash_map.get("KRW").amount_native if cash_map.get("KRW") else 0
            ),
            "krw_cash_base": _to_float(
                cash_map.get("KRW").amount_base if cash_map.get("KRW") else 0
            ),
            "usd_cash_native": _to_float(
                cash_map.get("USD").amount_native if cash_map.get("USD") else 0
            ),
            "usd_cash_base": _to_float(
                cash_map.get("USD").amount_base if cash_map.get("USD") else 0
            ),
            "total_cash_base": _to_float(summary.total_cash_base),
            "fx_rate_krw_to_base": fx_rate_krw_to_base,
            "fx_rate_base_to_krw": fx_rate_base_to_krw,
            "fx_rate_timestamp": fx_rate_timestamp,
        },
        "snapshot_metadata": {
            "holdings_snapshot_time": (
                source_map["holdings"].last_timestamp.isoformat()
                if source_map.get("holdings") and source_map["holdings"].last_timestamp
                else None
            ),
            "cash_snapshot_time": (
                source_map["cash"].last_timestamp.isoformat()
                if source_map.get("cash") and source_map["cash"].last_timestamp
                else None
            ),
            "price_snapshot_time": (
                source_map["prices"].last_timestamp.isoformat()
                if source_map.get("prices") and source_map["prices"].last_timestamp
                else None
            ),
            "fx_snapshot_time": (
                source_map["fx"].last_timestamp.isoformat()
                if source_map.get("fx") and source_map["fx"].last_timestamp
                else None
            ),
            "holdings_source_type": (
                source_map["holdings"].source_type if source_map.get("holdings") else None
            ),
            "cash_source_type": (
                source_map["cash"].source_type if source_map.get("cash") else None
            ),
            "price_source_type": (
                source_map["prices"].source_type if source_map.get("prices") else None
            ),
            "fx_source_type": (
                source_map["fx"].source_type if source_map.get("fx") else None
            ),
            "holdings_detail": (
                source_map["holdings"].detail if source_map.get("holdings") else None
            ),
            "cash_detail": source_map["cash"].detail if source_map.get("cash") else None,
            "price_detail": (
                source_map["prices"].detail if source_map.get("prices") else None
            ),
            "fx_detail": source_map["fx"].detail if source_map.get("fx") else None,
        },
    }

    snapshot_time = health.get_latest_relevant_timestamp()
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