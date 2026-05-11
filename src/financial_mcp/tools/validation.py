import pandas as pd

from financial_mcp.config import CSV_PATHS
from financial_mcp.data_loader import load_dataframes


def validate_dataset():
    results = []
    for name, df in load_dataframes().items():
        null_counts = {
            column: int(count)
            for column, count in df.isna().sum().items()
            if count
        }
        duplicate_rows = int(df.duplicated().sum())
        results.append(
            {
                "dataset": name,
                "path": str(CSV_PATHS[name]),
                "rows": int(len(df)),
                "columns": int(len(df.columns)),
                "null_counts": null_counts,
                "duplicate_rows": duplicate_rows,
                "has_value_column": "VALUE" in df.columns,
            }
        )
    return results


def search_financial_records(query, limit=20):
    query_text = str(query).strip().casefold()
    matches = []

    for dataset, df in load_dataframes().items():
        text_df = df.astype(str)
        mask = text_df.apply(
            lambda col: col.str.casefold().str.contains(query_text, na=False)
        ).any(axis=1)
        for record in df.loc[mask].head(int(limit)).to_dict(orient="records"):
            cleaned = {
                key: (None if pd.isna(value) else value)
                for key, value in record.items()
            }
            cleaned["dataset"] = dataset
            matches.append(cleaned)
            if len(matches) >= int(limit):
                return matches

    return matches
