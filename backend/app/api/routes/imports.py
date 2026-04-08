from decimal import Decimal, InvalidOperation

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from backend.app.api.deps import get_db
from backend.app.api.response import build_response
from backend.app.services.imports.us_holdings_csv_import_service import UsHoldingsCsvImportService

router = APIRouter(prefix="/api/v1/import", tags=["import"])


US_HOLDINGS_TEMPLATE = """symbol,security_name,quantity,avg_cost_usd,current_price_usd,market,sector,industry
AAPL,Apple Inc.,45,190,215,NASDAQ,Information Technology,Consumer Electronics
MSFT,Microsoft Corp.,20,380,425,NASDAQ,Information Technology,Software
"""


@router.get("/us-holdings/template")
def get_us_holdings_template():
    return PlainTextResponse(
        content=US_HOLDINGS_TEMPLATE,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="us_holdings_template.csv"'},
    )


@router.post("/us-holdings")
async def import_us_holdings_csv(
    file: UploadFile = File(...),
    usd_cash: str = Form(...),
    db: Session = Depends(get_db),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file.")

    try:
        usd_cash_decimal = Decimal(usd_cash)
    except InvalidOperation as exc:
        raise HTTPException(status_code=400, detail="usd_cash must be a valid decimal.") from exc

    if usd_cash_decimal < 0:
        raise HTTPException(status_code=400, detail="usd_cash must be non-negative.")

    file_bytes = await file.read()
    service = UsHoldingsCsvImportService(db)
    result = service.run(file_bytes=file_bytes, usd_cash=usd_cash_decimal)

    data = {
        "sync_run_id": result.sync_run_id,
        "snapshot_time": result.snapshot_time.isoformat(),
        "holdings_written": result.holdings_written,
        "cash_rows_written": result.cash_rows_written,
        "prices_written": result.prices_written,
        "carry_forward_holdings": result.carry_forward_holdings,
        "carry_forward_cash": result.carry_forward_cash,
        "warning_count": result.warning_count,
        "error_count": result.error_count,
        "imported_symbols": result.imported_symbols,
    }

    return build_response(data=data, snapshot_time=result.snapshot_time)