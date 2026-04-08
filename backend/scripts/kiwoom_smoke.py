from __future__ import annotations

from pprint import pprint

from backend.app.adapters.kiwoom.account import KiwoomAccountAdapter
from backend.app.adapters.kiwoom.archive import archive_kiwoom_payload
from backend.app.adapters.kiwoom.auth import KiwoomAuthClient
from backend.app.adapters.kiwoom.parser import summarize_payload_shape


def main() -> None:
    auth = KiwoomAuthClient()
    token = auth.issue_access_token()

    print("Token issued.")
    print(f"Token type: {token.token_type}")
    print(f"Expires:    {token.expires_dt}")

    adapter = KiwoomAccountAdapter()

    account_numbers_envelope = adapter.get_account_numbers_raw()
    account_numbers_archive = archive_kiwoom_payload(
        "account_numbers",
        account_numbers_envelope.body,
    )

    account_numbers = adapter.get_account_numbers()
    print("\nAccount numbers:")
    pprint(account_numbers)
    print(f"Archived raw account-numbers payload to: {account_numbers_archive}")

    primary_account_no = adapter.get_primary_account_no()
    print(f"\nPrimary account: {primary_account_no}")

    cash_envelope = adapter.get_cash_raw()
    cash_archive = archive_kiwoom_payload("cash", cash_envelope.body)
    print("\nCash payload keys / shape:")
    pprint(summarize_payload_shape(cash_envelope.body))
    print(f"Archived raw cash payload to: {cash_archive}")

    daily_status_envelope = adapter.get_daily_status_raw()
    daily_status_archive = archive_kiwoom_payload("daily_status", daily_status_envelope.body)
    print("\nDaily status payload keys / shape:")
    pprint(summarize_payload_shape(daily_status_envelope.body))
    print(f"Archived raw daily-status payload to: {daily_status_archive}")

    holdings_payload = adapter.get_holdings_raw()
    holdings_archive = archive_kiwoom_payload("holdings", holdings_payload)
    print("\nHoldings page count:")
    print(holdings_payload["page_count"])
    print(f"Archived raw holdings payload to: {holdings_archive}")


if __name__ == "__main__":
    main()