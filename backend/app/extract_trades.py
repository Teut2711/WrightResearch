import pandas as pd
from pathlib import Path
import base64
import mailparser
import io
from typing import Optional

eml_dir: Path = Path("data")

column_mapping = {
    "Deal Date": "deal_date",
    "party code/SEBI regn code of party": "party_code",
    "Instrument ISIN": "isin",
    "Buy/Sell Flag": "buy_sell",
    "QTY": "quantity",
    "COST": "cost",
    "NET AMOUNT": "net_amount",
    "Brokerage Amount": "brokerage",
    "Settlement Date": "settlement_date",
    "STT": "stt",
    "Exchange Code": "exchange_code",
    "Depository Code": "depository_code",
}

column_casting = {
    "quantity": "int",
    "cost": "float",
    "net_amount": "float",
    "brokerage": "float",
    "stt": "float",
}


def extract_excel_from_eml() -> Optional[pd.DataFrame]:
    """
    Extracts Excel files from all .eml emails in a directory and returns them as a Pandas DataFrame.

    Args:
        eml_dir (Path): Path to the directory containing .eml files.

    Returns:
        Optional[pd.DataFrame]: A DataFrame if Excel files are found, otherwise None.
    """
    all_dfs = []

    for eml_file in eml_dir.glob("*.eml"):

        mail = mailparser.parse_from_file(eml_file)

        for attachment in mail.attachments:
            if Path(attachment["filename"]).suffix.lower() == ".xlsx":
                excel_bytes = base64.b64decode(attachment["payload"])

                with io.BytesIO(excel_bytes) as excel_io:
                    df = pd.read_excel(excel_io, dtype=str).rename(
                        columns=column_mapping
                    )
                    date_cols = ["deal_date", "settlement_date"]
                    for col in date_cols:
                        if col in df.columns:
                            df[col] = pd.to_datetime(
                                df[col], format="%Y-%m-%d %H:%M:%S"
                            ).dt.date
                    for col, dtype in column_casting.items():
                        if col in df.columns:
                            df[col] = df[col].astype(dtype)

                    df.dropna(how="all", axis=1, inplace=True)
                    all_dfs.append(df)

    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    else:
        return None
