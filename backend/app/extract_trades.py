import pandas as pd
from pathlib import Path
import base64
import mailparser
import io
from typing import Optional

eml_dir: Path = Path("data")


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
                    df = pd.read_excel(excel_io)
                    df.dropna(how="all", axis=1, inplace=True)
                    all_dfs.append(df)

    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    else:
        return None
