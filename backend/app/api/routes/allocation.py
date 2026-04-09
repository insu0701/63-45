from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.api.response import build_response
from backend.app.services.exposure_service import ExposureService
from backend.app.services.valuation_service import ValuationService

router = APIRouter(prefix="/api/v1/allocation", tags=["allocation"])


def _to_float(value) -> float:
    return float(value or 0)


def _latest_allocation_snapshot_time(valuation: ValuationService):
    timestamps = [
        ts
        for ts in [
            valuation.get_latest_holdings_snapshot_time(),
            valuation.get_latest_cash_snapshot_time(),
        ]
        if ts is not None
    ]
    return max(timestamps) if timestamps else None


@router.get("/sleeve")
def get_sleeve_allocation(db: Session = Depends(get_db)):
    valuation = ValuationService(db)
    exposure = ExposureService(db)
    rows = exposure.get_sleeve_exposures()

    data = [
        {
            "sleeve": row.sleeve,
            "equity_value_base": _to_float(row.equity_value_base),
            "cash_value_base": _to_float(row.cash_value_base),
            "total_base_value": _to_float(row.total_base_value),
            "weight_of_total_nav": _to_float(row.weight_of_total_nav),
            "position_count": row.position_count,
            "unrealized_pnl_base": _to_float(row.unrealized_pnl_base),
        }
        for row in rows
    ]

    snapshot_time = _latest_allocation_snapshot_time(valuation)
    return build_response(data=data, snapshot_time=snapshot_time)


@router.get("/country")
def get_country_allocation(db: Session = Depends(get_db)):
    valuation = ValuationService(db)
    exposure = ExposureService(db)
    rows = exposure.get_country_exposures()

    data = [
        {
            "country": row.country,
            "market_value_base": _to_float(row.market_value_base),
            "weight_of_total_nav": _to_float(row.weight_of_total_nav),
        }
        for row in rows
    ]

    snapshot_time = valuation.get_latest_holdings_snapshot_time()
    return build_response(data=data, snapshot_time=snapshot_time)


@router.get("/sector")
def get_sector_allocation(db: Session = Depends(get_db)):
    valuation = ValuationService(db)
    exposure = ExposureService(db)
    rows = exposure.get_sector_exposures()

    data = [
        {
            "sector": row.sector,
            "market_value_base": _to_float(row.market_value_base),
            "weight_of_total_nav": _to_float(row.weight_of_total_nav),
        }
        for row in rows
    ]

    snapshot_time = valuation.get_latest_holdings_snapshot_time()
    return build_response(data=data, snapshot_time=snapshot_time)


@router.get("/currency")
def get_currency_allocation(db: Session = Depends(get_db)):
    valuation = ValuationService(db)
    exposure = ExposureService(db)
    rows = exposure.get_currency_exposures()

    data = [
        {
            "currency": row.currency,
            "total_base_value": _to_float(row.total_base_value),
            "weight_of_total_nav": _to_float(row.weight_of_total_nav),
        }
        for row in rows
    ]

    snapshot_time = _latest_allocation_snapshot_time(valuation)
    return build_response(data=data, snapshot_time=snapshot_time)