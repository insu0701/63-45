from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any


MONEY_QUANT = Decimal("0.0001")
PERCENT_DIVISOR = Decimal("100")


def parse_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None

    text = str(value).strip()
    if text == "":
        return None

    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def parse_percent_as_fraction(value: Any) -> Decimal | None:
    raw = parse_decimal(value)
    if raw is None:
        return None
    return raw / PERCENT_DIVISOR


def quantize_money(value: Decimal | None) -> Decimal | None:
    if value is None:
        return None
    return value.quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def normalize_kr_stock_code(raw_code: str) -> str:
    code = raw_code.strip()
    if code.startswith("A") and len(code) >= 7:
        return code[1:]
    return code


@dataclass
class NormalizedCashRow:
    currency: str
    amount_native: Decimal
    fx_rate_to_base: Decimal | None
    amount_base: Decimal | None


@dataclass
class NormalizedHoldingRow:
    symbol: str
    security_name: str
    quantity: Decimal
    avg_cost_native: Decimal | None
    current_price_native: Decimal | None
    cost_basis_native: Decimal | None
    market_value_native: Decimal | None
    unrealized_pnl_native: Decimal | None
    unrealized_return_pct: Decimal | None
    fx_rate_to_base: Decimal | None
    cost_basis_base: Decimal | None
    market_value_base: Decimal | None
    unrealized_pnl_base: Decimal | None


def normalize_krw_cash_payload(
    payload: dict[str, Any],
    fx_rate_to_base: Decimal,
) -> NormalizedCashRow:
    entr = parse_decimal(payload.get("entr")) or Decimal("0")

    return NormalizedCashRow(
        currency="KRW",
        amount_native=entr,
        fx_rate_to_base=fx_rate_to_base,
        amount_base=quantize_money(entr * fx_rate_to_base),
    )


def normalize_holdings_payload(
    payload: dict[str, Any],
    fx_rate_to_base: Decimal,
) -> tuple[dict[str, Decimal | None], list[NormalizedHoldingRow]]:
    pages = payload.get("pages", [])
    if not pages:
        return (
            {
                "tot_pur_amt": None,
                "tot_evlt_amt": None,
                "tot_evlt_pl": None,
                "tot_prft_rt": None,
                "prsm_dpst_aset_amt": None,
            },
            [],
        )

    first_page = pages[0]
    body = first_page.get("body", {})

    totals = {
        "tot_pur_amt": parse_decimal(body.get("tot_pur_amt")),
        "tot_evlt_amt": parse_decimal(body.get("tot_evlt_amt")),
        "tot_evlt_pl": parse_decimal(body.get("tot_evlt_pl")),
        "tot_prft_rt": parse_percent_as_fraction(body.get("tot_prft_rt")),
        "prsm_dpst_aset_amt": parse_decimal(body.get("prsm_dpst_aset_amt")),
    }

    rows: list[NormalizedHoldingRow] = []

    for item in body.get("acnt_evlt_remn_indv_tot", []):
        cost_basis_native = parse_decimal(item.get("pur_amt"))
        market_value_native = parse_decimal(item.get("evlt_amt"))
        unrealized_pnl_native = parse_decimal(item.get("evltv_prft"))

        rows.append(
            NormalizedHoldingRow(
                symbol=normalize_kr_stock_code(item.get("stk_cd", "")),
                security_name=str(item.get("stk_nm", "")).strip(),
                quantity=parse_decimal(item.get("rmnd_qty")) or Decimal("0"),
                avg_cost_native=parse_decimal(item.get("pur_pric")),
                current_price_native=parse_decimal(item.get("cur_prc")),
                cost_basis_native=cost_basis_native,
                market_value_native=market_value_native,
                unrealized_pnl_native=unrealized_pnl_native,
                unrealized_return_pct=parse_percent_as_fraction(item.get("prft_rt")),
                fx_rate_to_base=fx_rate_to_base,
                cost_basis_base=quantize_money(cost_basis_native * fx_rate_to_base) if cost_basis_native is not None else None,
                market_value_base=quantize_money(market_value_native * fx_rate_to_base) if market_value_native is not None else None,
                unrealized_pnl_base=quantize_money(unrealized_pnl_native * fx_rate_to_base) if unrealized_pnl_native is not None else None,
            )
        )

    return totals, rows