"""add strategy snapshots and daily decision logs

Revision ID: 080a65f2bbbe
Revises: 7639fd4cefcd
Create Date: 2026-04-08 15:25:01.074940
"""

from alembic import op
import sqlalchemy as sa

revision = "080a65f2bbbe"
down_revision = "7639fd4cefcd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "strategy_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("market", sa.String(), nullable=False),
        sa.Column("country", sa.String(), nullable=False),
        sa.Column("sleeve", sa.String(), nullable=False),
        sa.Column("strategy_state", sa.String(), nullable=True),
        sa.Column("target_state", sa.String(), nullable=True),
        sa.Column("target_weight", sa.Numeric(18, 8), nullable=True),
        sa.Column("target_dollars", sa.Numeric(18, 4), nullable=True),
        sa.Column("actual_position_dollars", sa.Numeric(18, 4), nullable=True),
        sa.Column("actual_vs_target_delta", sa.Numeric(18, 4), nullable=True),
        sa.Column("eligibility_status", sa.String(), nullable=True),
        sa.Column("buy_list_status", sa.String(), nullable=True),
        sa.Column("reason_code", sa.String(), nullable=True),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("source_run_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["source_run_id"], ["sync_runs.id"]),
    )
    op.create_index("ix_strategy_snapshots_as_of_date", "strategy_snapshots", ["as_of_date"])
    op.create_index("ix_strategy_snapshots_symbol", "strategy_snapshots", ["symbol"])
    op.create_index("ix_strategy_snapshots_market", "strategy_snapshots", ["market"])
    op.create_index("ix_strategy_snapshots_sleeve", "strategy_snapshots", ["sleeve"])
    op.create_index("ix_strategy_snapshots_account_id", "strategy_snapshots", ["account_id"])

    op.create_table(
        "daily_decision_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("decision_date", sa.Date(), nullable=False),
        sa.Column("decision_timestamp", sa.DateTime(timezone=True), nullable=True),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("market", sa.String(), nullable=False),
        sa.Column("sleeve", sa.String(), nullable=False),
        sa.Column("sector", sa.String(), nullable=True),
        sa.Column("eligibility_status", sa.String(), nullable=True),
        sa.Column("buy_list_status", sa.String(), nullable=True),
        sa.Column("morningstar_status", sa.String(), nullable=True),
        sa.Column("foreign_buy_list_status", sa.String(), nullable=True),
        sa.Column("foreign_sell_list_status", sa.String(), nullable=True),
        sa.Column("decision_price", sa.Numeric(18, 4), nullable=True),
        sa.Column("macd_value", sa.Numeric(18, 8), nullable=True),
        sa.Column("macd_signal_value", sa.Numeric(18, 8), nullable=True),
        sa.Column("rsi_value", sa.Numeric(18, 8), nullable=True),
        sa.Column("rsi_signal_line", sa.Numeric(18, 8), nullable=True),
        sa.Column("sma20", sa.Numeric(18, 8), nullable=True),
        sa.Column("ema50", sa.Numeric(18, 8), nullable=True),
        sa.Column("volatility_estimate", sa.Numeric(18, 8), nullable=True),
        sa.Column("current_state", sa.String(), nullable=True),
        sa.Column("target_state", sa.String(), nullable=True),
        sa.Column("current_position_dollars", sa.Numeric(18, 4), nullable=True),
        sa.Column("target_position_dollars", sa.Numeric(18, 4), nullable=True),
        sa.Column("generated_order_quantity", sa.Numeric(18, 4), nullable=True),
        sa.Column("fill_quantity", sa.Numeric(18, 4), nullable=True),
        sa.Column("rejection_status", sa.String(), nullable=True),
        sa.Column("reason_code", sa.String(), nullable=True),
        sa.Column("source_type", sa.String(), nullable=False),
        sa.Column("source_run_id", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["source_run_id"], ["sync_runs.id"]),
    )
    op.create_index("ix_daily_decision_logs_decision_date", "daily_decision_logs", ["decision_date"])
    op.create_index("ix_daily_decision_logs_symbol", "daily_decision_logs", ["symbol"])
    op.create_index("ix_daily_decision_logs_market", "daily_decision_logs", ["market"])
    op.create_index("ix_daily_decision_logs_sleeve", "daily_decision_logs", ["sleeve"])
    op.create_index("ix_daily_decision_logs_account_id", "daily_decision_logs", ["account_id"])


def downgrade() -> None:
    op.drop_index("ix_daily_decision_logs_account_id", table_name="daily_decision_logs")
    op.drop_index("ix_daily_decision_logs_sleeve", table_name="daily_decision_logs")
    op.drop_index("ix_daily_decision_logs_market", table_name="daily_decision_logs")
    op.drop_index("ix_daily_decision_logs_symbol", table_name="daily_decision_logs")
    op.drop_index("ix_daily_decision_logs_decision_date", table_name="daily_decision_logs")
    op.drop_table("daily_decision_logs")

    op.drop_index("ix_strategy_snapshots_account_id", table_name="strategy_snapshots")
    op.drop_index("ix_strategy_snapshots_sleeve", table_name="strategy_snapshots")
    op.drop_index("ix_strategy_snapshots_market", table_name="strategy_snapshots")
    op.drop_index("ix_strategy_snapshots_symbol", table_name="strategy_snapshots")
    op.drop_index("ix_strategy_snapshots_as_of_date", table_name="strategy_snapshots")
    op.drop_table("strategy_snapshots")