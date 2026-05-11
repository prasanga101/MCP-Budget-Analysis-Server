# transform_details.py

import pandas as pd
from pathlib import Path

try:
    from data.scripts.cleaner_performance import clean_details_sheet, EXCEL_FILE, PROJECT_ROOT
except ModuleNotFoundError:
    from cleaner_performance import clean_details_sheet, EXCEL_FILE, PROJECT_ROOT

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "Performance"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ID_COLUMNS = {
    "SN",
    "LINE_ITEM",
    "CATEGORY",
    "ROW_TYPE",
}

# Only actual month columns — excludes totals/upto aggregates
VALID_PERIODS = {
    "SHRAWAN_2082",
    "BHADRA_2082",
    "ASHWIN_2082",
    "KARTIK_2082",
    "MANGSIR_2082",
    "POUSH_2082",
    "MAGH_2082",
    "FALGUN_2082",
}


def split_period(column_name):

    for period in VALID_PERIODS:
        if column_name == period:
            return period

    return None


def transform_details(df):

    # only real line items
    df = df[df["ROW_TYPE"] == "LINE"].copy()

    value_columns = []

    for col in df.columns:

        if col in ID_COLUMNS:
            continue

        period = split_period(col)

        if period:
            value_columns.append(col)

    long_df = df.melt(
        id_vars=[c for c in ID_COLUMNS if c in df.columns],
        value_vars=value_columns,
        var_name="PERIOD",
        value_name="VALUE",
    )

    # remove nulls
    long_df = long_df.dropna(subset=["VALUE"])

    # optional: remove zero rows
    # long_df = long_df[long_df["VALUE"] != 0]

    ordered_cols = [
        "CATEGORY",
        "LINE_ITEM",
        "ROW_TYPE",
        "PERIOD",
        "VALUE",
    ]

    existing = [c for c in ordered_cols if c in long_df.columns]
    remaining = [c for c in long_df.columns if c not in existing]

    long_df = long_df[existing + remaining]

    return long_df


if __name__ == "__main__":

    df, info = clean_details_sheet(
        EXCEL_FILE,
        "Revenue and Expenses Details"
    )

    transformed = transform_details(df)

    csv_path = OUTPUT_DIR / "details_long.csv"

    transformed.to_csv(csv_path, index=False)

    print("=" * 80)
    print("DETAILS TRANSFORMATION COMPLETE")
    print("=" * 80)

    print(f"Rows: {len(transformed)}")
    print(f"Columns: {len(transformed.columns)}")

    print(f"CSV: {csv_path}")

    with pd.option_context(
        "display.max_columns",
        20,
        "display.width",
        200
    ):
        print(transformed.head())
