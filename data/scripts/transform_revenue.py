# transform_revenue.py

import pandas as pd
from pathlib import Path

from cleaner_performance import clean_part_sheet, EXCEL_FILE

OUTPUT_DIR = Path("data/processed/Performance")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IGNORE_PREFIXES = {
    "ANNUAL",
}
METRICS = {
    "BUDGET",
    "ACTUAL",
    "VARIANCE",
    "PCT_OF_ACHIEVEMENT",
}

ID_COLUMNS = {
    "SN",
    "SEGEMENT",
    "PARTICULARS",
    "SUB_SEGMENT",
    "ROW_TYPE",
}


def split_period_metric(column_name):

    for prefix in IGNORE_PREFIXES:
        if column_name.startswith(prefix):
            return None, None

    for metric in sorted(METRICS, key=len, reverse=True):
        suffix = f"_{metric}"

        if column_name.endswith(suffix):
            period = column_name[:-len(suffix)]
            return period, metric

    return None, None

def transform_revenue_part(df):
    df = df[df["ROW_TYPE"] == "LINE"].copy()

    value_columns = []

    for col in df.columns:
        if col in ID_COLUMNS:
            continue

        period, metric = split_period_metric(col)

        if period and metric:
            value_columns.append(col)

    long_df = df.melt(
        id_vars=[c for c in ID_COLUMNS if c in df.columns],
        value_vars=value_columns,
        var_name="PERIOD_METRIC",
        value_name="VALUE",
    )

    parsed = long_df["PERIOD_METRIC"].apply(split_period_metric)

    long_df["PERIOD"] = parsed.apply(lambda x: x[0])
    long_df["METRIC"] = parsed.apply(lambda x: x[1])

    long_df = long_df.drop(columns=["PERIOD_METRIC"])

    long_df = long_df.dropna(subset=["VALUE"])

    ordered_cols = [
        "SEGEMENT",
        "SUB_SEGMENT",
        "PARTICULARS",
        "ROW_TYPE",
        "PERIOD",
        "METRIC",
        "VALUE",
    ]

    existing = [c for c in ordered_cols if c in long_df.columns]
    remaining = [c for c in long_df.columns if c not in existing]

    long_df = long_df[existing + remaining]

    return long_df


if __name__ == "__main__":
    df, info = clean_part_sheet(EXCEL_FILE, "Revenue Part")

    transformed = transform_revenue_part(df)

    csv_path = OUTPUT_DIR / "revenue_part_long.csv"

    transformed.to_csv(csv_path, index=False)

    print("=" * 80)
    print("REVENUE TRANSFORMATION COMPLETE")
    print("=" * 80)
    print(f"Rows: {len(transformed)}")
    print(f"Columns: {len(transformed.columns)}")
    print(f"CSV: {csv_path}")

    with pd.option_context("display.max_columns", 20, "display.width", 200):
        print(transformed.head())