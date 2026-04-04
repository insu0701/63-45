from pydantic import BaseModel


class OverviewSummaryData(BaseModel):
    total_equity_value_base: float
    total_cash_base: float
    total_nav_base: float
    total_unrealized_pnl_base: float
    total_unrealized_return_pct: float
    kr_equity_value_base: float
    us_equity_value_base: float
    krw_cash_base: float
    usd_cash_base: float


class TopHoldingItem(BaseModel):
    symbol: str
    security_name: str
    sleeve: str
    country: str
    market_value_base: float
    cost_basis_base: float
    unrealized_pnl_base: float
    unrealized_return_pct: float
    weight_of_total_nav: float


class ConcentrationData(BaseModel):
    top1_pct: float
    top3_pct: float
    top5_pct: float
    largest_sector_pct: float
    largest_sleeve_pct: float