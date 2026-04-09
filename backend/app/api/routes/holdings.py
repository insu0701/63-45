from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.api.response import build_response
from backend.app.services.exposure_service import ExposureService
from backend.app.services.valuation_service import ValuationService

router = APIRouter(prefix="/api/v1/holdings", tags=["holdings"])


def _to_float(value) -> float:
    return float(value or 0)


@router.get("")
def get_holdings(
    sleeve: str | None = Query(default=None),
    sector: str | None = Query(default=None),
    search: str | None = Query(default=None),
    winners_only: bool = Query(default=False),
    losers_only: bool = Query(default=False),
    min_weight: float | None = Query(default=None, ge=0),
    db: Session = Depends(get_db),
):
    valuation = ValuationService(db)
    exposure = ExposureService(db)

    holdings = valuation.get_latest_holdings()
    summary = valuation.get_portfolio_summary()
    sleeve_exposures = exposure.get_sleeve_exposures()

    total_nav = summary.total_nav_base
    sleeve_nav_map = {row.sleeve: row.equity_value_base for row in sleeve_exposures}

    items = []
    for row in holdings:
        market_value_base = Decimal(row.market_value_base or 0)
        sleeve_nav = Decimal(sleeve_nav_map.get(row.sleeve) or 0)

        weight_of_total_nav = Decimal("0") if total_nav == 0 else market_value_base / total_nav
        weight_of_sleeve = Decimal("0") if sleeve_nav == 0 else market_value_base / sleeve_nav
        unrealized_pnl_base = Decimal(row.unrealized_pnl_base or 0)

        item = {
            "symbol": row.symbol,
            "security_name": row.security_name,
            "sleeve": row.sleeve,
            "country": row.country,
            "sector": row.sector,
            "industry": row.industry,
            "market": row.market,
            "currency": row.currency,
            "quantity": _to_float(row.quantity),
            "avg_cost_native": _to_float(row.avg_cost_native) if row.avg_cost_native is not None else None,
            "current_price_native": _to_float(row.current_price_native) if row.current_price_native is not None else None,
            "cost_basis_base": _to_float(row.cost_basis_base) if row.cost_basis_base is not None else None,
            "market_value_base": _to_float(row.market_value_base) if row.market_value_base is not None else None,
            "unrealized_pnl_base": _to_float(row.unrealized_pnl_base) if row.unrealized_pnl_base is not None else None,
            "unrealized_return_pct": _to_float(row.unrealized_return_pct) if row.unrealized_return_pct is not None else None,
            "weight_of_total_nav": _to_float(weight_of_total_nav),
            "weight_of_sleeve": _to_float(weight_of_sleeve),
            "price_timestamp": row.price_timestamp.isoformat() if row.price_timestamp else None,
            "source_type": row.source_type,
        }

        if sleeve and row.sleeve != sleeve:
            continue
        if sector and (row.sector or "") != sector:
            continue
        if search:
            search_lower = search.lower()
            if search_lower not in row.symbol.lower() and search_lower not in row.security_name.lower():
                continue
        if winners_only and unrealized_pnl_base <= 0:
            continue
        if losers_only and unrealized_pnl_base >= 0:
            continue
        if min_weight is not None and float(weight_of_total_nav) < min_weight:
            continue

        items.append(item)

    items.sort(key=lambda x: x["market_value_base"] or 0, reverse=True)

    snapshot_time = valuation.get_latest_holdings_snapshot_time()
    return build_response(data=items, snapshot_time=snapshot_time)


@router.get("/{symbol}")
def get_holding_detail(symbol: str, db: Session = Depends(get_db)):
    valuation = ValuationService(db)
    holdings = valuation.get_latest_holdings()

    matched = None
    for row in holdings:
        if row.symbol.upper() == symbol.upper():
            matched = row
            break

    if matched is None:
        raise HTTPException(status_code=404, detail=f"Holding '{symbol}' not found.")

    item = {
        "symbol": matched.symbol,
        "security_name": matched.security_name,
        "sleeve": matched.sleeve,
        "country": matched.country,
        "sector": matched.sector,
        "industry": matched.industry,
        "market": matched.market,
        "currency": matched.currency,
        "quantity": _to_float(matched.quantity),
        "avg_cost_native": _to_float(matched.avg_cost_native) if matched.avg_cost_native is not None else None,
        "current_price_native": _to_float(matched.current_price_native) if matched.current_price_native is not None else None,
        "cost_basis_native": _to_float(matched.cost_basis_native) if matched.cost_basis_native is not None else None,
        "market_value_native": _to_float(matched.market_value_native) if matched.market_value_native is not None else None,
        "unrealized_pnl_native": _to_float(matched.unrealized_pnl_native) if matched.unrealized_pnl_native is not None else None,
        "unrealized_return_pct": _to_float(matched.unrealized_return_pct) if matched.unrealized_return_pct is not None else None,
        "fx_rate_to_base": _to_float(matched.fx_rate_to_base) if matched.fx_rate_to_base is not None else None,
        "cost_basis_base": _to_float(matched.cost_basis_base) if matched.cost_basis_base is not None else None,
        "market_value_base": _to_float(matched.market_value_base) if matched.market_value_base is not None else None,
        "unrealized_pnl_base": _to_float(matched.unrealized_pnl_base) if matched.unrealized_pnl_base is not None else None,
        "price_timestamp": matched.price_timestamp.isoformat() if matched.price_timestamp else None,
        "snapshot_time": matched.snapshot_time.isoformat(),
        "source_type": matched.source_type,
    }

    snapshot_time = valuation.get_latest_holdings_snapshot_time()
    return build_response(data=item, snapshot_time=snapshot_time)