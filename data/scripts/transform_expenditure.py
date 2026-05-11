# transform_expenditure.py
IGNORE_PREFIXES = {
    "ANNUAL",
}
import pandas as pd
from pathlib import Path

try:
    from data.scripts.cleaner_performance import clean_part_sheet, EXCEL_FILE, PROJECT_ROOT
except ModuleNotFoundError:
    from cleaner_performance import clean_part_sheet, EXCEL_FILE, PROJECT_ROOT

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "Performance"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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


def transform_expenditure_part(df):
    """
    Convert wide expenditure sheet into normalized long format.
    """

    # Keep only actual line data
    df = df[df["ROW_TYPE"] == "LINE"].copy()

    # Standardize column names
    df.columns = (
        df.columns.str.strip()
        .str.upper()
        .str.replace(" ", "_")
    )

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

    # Optional fiscal metadata
    long_df["FISCAL_YEAR"] = "2082/83"

    # Convert values safely to numeric
    long_df["VALUE"] = pd.to_numeric(
        long_df["VALUE"],
        errors="coerce"
    )

    # Drop temporary column
    long_df = long_df.drop(columns=["PERIOD_METRIC"])

    # Remove empty values
    long_df = long_df.dropna(subset=["VALUE"])

    ordered_cols = [
        "SEGEMENT",
        "SUB_SEGMENT",
        "PARTICULARS",
        "ROW_TYPE",
        "FISCAL_YEAR",
        "PERIOD",
        "METRIC",
        "VALUE",
    ]

    existing = [c for c in ordered_cols if c in long_df.columns]
    remaining = [c for c in long_df.columns if c not in existing]

    long_df = long_df[existing + remaining]

    return long_df


if __name__ == "__main__":

    # Clean Expenditure Part sheet
    df, info = clean_part_sheet(EXCEL_FILE, "Expenditure Part")

    # Transform
    transformed = transform_expenditure_part(df)

    csv_path = OUTPUT_DIR / "expenditure_part_long.csv"

    transformed.to_csv(csv_path, index=False)

    print("=" * 80)
    print("EXPENDITURE TRANSFORMATION COMPLETE")
    print("=" * 80)
    print(f"Rows: {len(transformed)}")
    print(f"Columns: {len(transformed.columns)}")
    print(f"CSV: {csv_path}")

    with pd.option_context(
        "display.max_columns", 20,
        "display.width", 200
    ):
        print(transformed.head())
