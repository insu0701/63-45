from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.services.exposure_service import ExposureService
from backend.app.services.valuation_service import ValuationService


@dataclass
class ConcentrationMetrics:
    top1_pct: Decimal
    top3_pct: Decimal
    top5_pct: Decimal
    largest_sector_pct: Decimal
    largest_sleeve_pct: Decimal


class ConcentrationService:
    def __init__(self, db: Session):
        self.db = db
        self.valuation_service = ValuationService(db)
        self.exposure_service = ExposureService(db)

    def get_metrics(self) -> ConcentrationMetrics:
        summary = self.valuation_service.get_portfolio_summary()
        positions = self.valuation_service.get_position_valuations()
        sector_exposures = self.exposure_service.get_sector_exposures()
        sleeve_exposures = self.exposure_service.get_sleeve_exposures()

        total_nav = summary.total_nav_base or Decimal("0")

        if total_nav == 0:
            return ConcentrationMetrics(
                top1_pct=Decimal("0"),
                top3_pct=Decimal("0"),
                top5_pct=Decimal("0"),
                largest_sector_pct=Decimal("0"),
                largest_sleeve_pct=Decimal("0"),
            )

        position_weights = sorted(
            [(p.market_value_base / total_nav) for p in positions],
            reverse=True,
        )

        top1_pct = sum(position_weights[:1], Decimal("0"))
        top3_pct = sum(position_weights[:3], Decimal("0"))
        top5_pct = sum(position_weights[:5], Decimal("0"))

        largest_sector_pct = sector_exposures[0].weight_of_total_nav if sector_exposures else Decimal("0")
        largest_sleeve_pct = sleeve_exposures[0].weight_of_total_nav if sleeve_exposures else Decimal("0")

        return ConcentrationMetrics(
            top1_pct=top1_pct,
            top3_pct=top3_pct,
            top5_pct=top5_pct,
            largest_sector_pct=largest_sector_pct,
            largest_sleeve_pct=largest_sleeve_pct,
        )