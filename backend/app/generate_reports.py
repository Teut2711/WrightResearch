import pandas as pd


def generate_reports(reconciliation_results: pd.DataFrame):

    matched_trades = reconciliation_results[
        reconciliation_results["status"] == "matched"
    ]
    unmatched_trades = reconciliation_results[
        reconciliation_results["status"] != "matched"
    ]
    # broker_summary = (
    #     reconciliation_results.groupby("broker_code")
    #     .agg({"total_cost": "sum", "execution_slippage": "mean"})
    #     .reset_index()
    # )

    matched_trades.to_csv("data/generated/matched_trades.csv", index=False)
    unmatched_trades.to_csv("data/generated/unmatched_trades.csv", index=False)
    # broker_summary.to_csv("broker_summary.csv", index=False)
