from backend.app.db.session import SessionLocal
from backend.app.services.concentration_service import ConcentrationService
from backend.app.services.exposure_service import ExposureService
from backend.app.services.valuation_service import ValuationService


def pct(x) -> str:
    return f"{float(x) * 100:.2f}%"


def main() -> None:
    db = SessionLocal()
    try:
        valuation = ValuationService(db)
        exposure = ExposureService(db)
        concentration = ConcentrationService(db)

        summary = valuation.get_portfolio_summary()
        positions = valuation.get_position_valuations()
        cash_rows = valuation.get_cash_valuations()
        sleeve_exposures = exposure.get_sleeve_exposures()
        country_exposures = exposure.get_country_exposures()
        sector_exposures = exposure.get_sector_exposures()
        currency_exposures = exposure.get_currency_exposures()
        concentration_metrics = concentration.get_metrics()

        print("\n=== PORTFOLIO SUMMARY ===")
        print(f"Total Equity Value (base): {summary.total_equity_value_base}")
        print(f"Total Cash (base):        {summary.total_cash_base}")
        print(f"Total NAV (base):         {summary.total_nav_base}")
        print(f"Total Unrealized P&L:     {summary.total_unrealized_pnl_base}")
        print(f"Total Unrealized Return:  {pct(summary.total_unrealized_return_pct)}")

        print("\n=== CASH ===")
        for c in cash_rows:
            print(f"{c.currency}: native={c.amount_native}, base={c.amount_base}")

        print("\n=== POSITIONS ===")
        for p in positions:
            print(
                f"{p.symbol:>6} | {p.sleeve} | MV={p.market_value_base} | "
                f"Cost={p.cost_basis_base} | UPNL={p.unrealized_pnl_base} | "
                f"Return={pct(p.unrealized_return_pct)}"
            )

        print("\n=== SLEEVE EXPOSURE ===")
        for s in sleeve_exposures:
            print(
                f"{s.sleeve}: value={s.market_value_base}, "
                f"weight={pct(s.weight_of_total_nav)}, "
                f"positions={s.position_count}, upnl={s.unrealized_pnl_base}"
            )

        print("\n=== COUNTRY EXPOSURE ===")
        for c in country_exposures:
            print(f"{c.country}: value={c.market_value_base}, weight={pct(c.weight_of_total_nav)}")

        print("\n=== SECTOR EXPOSURE ===")
        for s in sector_exposures:
            print(f"{s.sector}: value={s.market_value_base}, weight={pct(s.weight_of_total_nav)}")

        print("\n=== CURRENCY EXPOSURE ===")
        for c in currency_exposures:
            print(f"{c.currency}: value={c.total_base_value}, weight={pct(c.weight_of_total_nav)}")

        print("\n=== CONCENTRATION ===")
        print(f"Top 1:           {pct(concentration_metrics.top1_pct)}")
        print(f"Top 3:           {pct(concentration_metrics.top3_pct)}")
        print(f"Top 5:           {pct(concentration_metrics.top5_pct)}")
        print(f"Largest sector:  {pct(concentration_metrics.largest_sector_pct)}")
        print(f"Largest sleeve:  {pct(concentration_metrics.largest_sleeve_pct)}")

    finally:
        db.close()


if __name__ == "__main__":
    main()