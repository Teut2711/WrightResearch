from enum import Enum


class ReportType(str, Enum):
    matched_trades = "matched_trades.csv"
    unmatched_trades = "unmatched_trades.csv"
    broker_summary = "broker_summary.csv"
