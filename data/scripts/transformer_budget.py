from pathlib import Path

import pandas as pd

try:
    from data.scripts.cleaner_budget import (
        DEFAULT_BUDGET_FILE,
        MONTHLY_BUDGET_SHEETS,
        load_and_process_sheet,
    )
except ModuleNotFoundError:
    from cleaner_budget import (
        DEFAULT_BUDGET_FILE,
        MONTHLY_BUDGET_SHEETS,
        load_and_process_sheet,
    )


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "Budget"
OUTPUT_FILES = {
    "revenue": "monthly_revenue_budget_normalized.csv",
    "expenditure": "monthly_expenditure_budget_normalized.csv",
}
ID_COLUMNS = [
    "S.N.",
    "SEGEMENT",
    "PARTICULARS",
    "BUDGETED AMOUNT FOR THE YEAR (NPR)",
    "CATEGORY",
]


def normalize_monthly_data(df):
    """Convert monthly budget columns into MONTH_NAME/YEAR/VALUE rows."""
    id_columns = [col for col in ID_COLUMNS if col in df.columns]
    month_columns = [col for col in df.columns if col not in id_columns]

    normalized_df = pd.melt(
        df,
        id_vars=id_columns,
        value_vars=month_columns,
        var_name="MONTH",
        value_name="VALUE",
    )
    normalized_df = normalized_df[normalized_df["VALUE"].notna()].copy()

    month_parts = normalized_df["MONTH"].astype(str).str.extract(
        r"^(?P<MONTH_NAME>[A-Z]+)\s+(?P<YEAR>\d{4})$"
    )
    normalized_df["MONTH_NAME"] = month_parts["MONTH_NAME"]
    normalized_df["YEAR"] = month_parts["YEAR"]
    normalized_df = normalized_df.dropna(subset=["MONTH_NAME", "YEAR"])
    normalized_df = normalized_df.drop(columns=["MONTH"])

    ordered_cols = [
        "S.N.",
        "SEGEMENT",
        "CATEGORY",
        "PARTICULARS",
        "BUDGETED AMOUNT FOR THE YEAR (NPR)",
        "VALUE",
        "MONTH_NAME",
        "YEAR",
    ]
    existing = [col for col in ordered_cols if col in normalized_df.columns]
    remaining = [col for col in normalized_df.columns if col not in existing]
    return normalized_df[existing + remaining].reset_index(drop=True)


def transform_budget_sheet(file_path, sheet_name):
    cleaned = load_and_process_sheet(file_path, sheet_name)
    return normalize_monthly_data(cleaned)


def build_all_budget_outputs(
    input_file=DEFAULT_BUDGET_FILE,
    output_dir=OUTPUT_DIR,
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    outputs = {}
    for kind, sheet_name in MONTHLY_BUDGET_SHEETS.items():
        normalized = transform_budget_sheet(input_file, sheet_name)
        csv_path = output_dir / OUTPUT_FILES[kind]
        normalized.to_csv(csv_path, index=False)
        outputs[kind] = {"path": csv_path, "data": normalized}

    return outputs


def main():
    outputs = build_all_budget_outputs()
    for kind, result in outputs.items():
        df = result["data"]
        print(f"{kind}: rows={len(df)} columns={len(df.columns)} csv={result['path']}")


if __name__ == "__main__":
    main()
