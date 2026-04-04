from pydantic import BaseModel


class SleeveAllocationItem(BaseModel):
    sleeve: str
    market_value_base: float
    weight_of_total_nav: float
    position_count: int
    unrealized_pnl_base: float


class CountryAllocationItem(BaseModel):
    country: str
    market_value_base: float
    weight_of_total_nav: float


class SectorAllocationItem(BaseModel):
    sector: str
    market_value_base: float
    weight_of_total_nav: float


class CurrencyAllocationItem(BaseModel):
    currency: str
    total_base_value: float
    weight_of_total_nav: float