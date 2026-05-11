"""Export helpers for analysis tables."""

# This file is part of ProChem.
# ProChem Copyright (C) 2021-2026 A.A.Solovykh - https://github.com/asolovykh
# See LICENSE.txt for details.

from __future__ import annotations

from pathlib import Path

import pandas as pd


def export_dataframe(dataframe: pd.DataFrame, path: str | Path) -> Path:
    """Export a DataFrame to xlsx, csv or html based on file suffix."""
    output = Path(path)
    suffix = output.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        with pd.ExcelWriter(output) as writer:
            dataframe.to_excel(writer, sheet_name="analysis", index=False)
            worksheet = writer.sheets["analysis"]
            if hasattr(worksheet, "set_column"):
                for column_index, column in enumerate(dataframe.columns):
                    width = max(dataframe[column].astype(str).map(len).max(), len(str(column)))
                    worksheet.set_column(column_index, column_index, width)
    elif suffix == ".csv":
        dataframe.to_csv(output, index=False)
    elif suffix == ".html":
        dataframe.to_html(output, index=False, na_rep="")
    else:
        raise ValueError(f"Unsupported export format: {suffix}")
    return output
