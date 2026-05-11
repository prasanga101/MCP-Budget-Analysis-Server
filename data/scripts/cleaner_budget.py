from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BUDGET_FILE = PROJECT_ROOT / "data" / "Budget Details.xlsx"
MONTHLY_BUDGET_SHEETS = {
    "revenue": "Monthly Revenue Budget",
    "expenditure": "Monthly Expenditure Budget",
}


def load_excel_file(file_path=DEFAULT_BUDGET_FILE):
    """Open an Excel workbook and return a pandas ExcelFile."""
    return pd.ExcelFile(file_path)


def get_sheet(file_path=DEFAULT_BUDGET_FILE, sheet_name=None, skiprows=3):
    """Read a budget workbook sheet using the source workbook layout."""
    if sheet_name is None:
        raise ValueError("sheet_name is required")
    return pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skiprows)


def basic_clean(df):
    """Remove empty workbook scaffolding while preserving source columns."""
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    df = df.replace("", np.nan)
    df = df.dropna(axis=0, how="all")
    df = df.dropna(axis=1, how="all")
    df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]
    return df.reset_index(drop=True)


def filter_rows(df):
    """Drop subtotal/summary rows that should not become facts."""
    df = basic_clean(df)
    skip_keywords = ["subtotal", "total", "operating profit"]
    mask = df["PARTICULARS"].astype(str).str.contains(
        "|".join(skip_keywords),
        case=False,
        na=False,
    )
    has_particulars = df["PARTICULARS"].notna()
    return df.loc[has_particulars & ~mask].copy()


def propagate_segments(df):
    df = df.copy()
    df["SEGEMENT"] = df["SEGEMENT"].ffill()
    return df


def propagate_categories(df):
    """Forward-fill revenue sub-categories such as I./II./III. sections."""
    df = df.copy()
    category_mask = df["PARTICULARS"].astype(str).str.match(
        r"^[IVXLCDM]+\.",
        na=False,
    )
    segment_only_mask = df["S.N."].notna() & ~category_mask

    df["CATEGORY"] = df["PARTICULARS"].where(category_mask)
    df.loc[segment_only_mask, "CATEGORY"] = np.nan
    df["CATEGORY"] = df["CATEGORY"].ffill()
    return df


def propagate_serial_numbers(df):
    df = df.copy()
    df["S.N."] = df["S.N."].ffill()
    return df


def process_sheet(df, sheet_name):
    """Clean a raw monthly budget sheet into a wide, analysis-ready frame."""
    df = filter_rows(df)
    df = propagate_segments(df)
    df = propagate_serial_numbers(df)

    if sheet_name == MONTHLY_BUDGET_SHEETS["revenue"]:
        df = propagate_categories(df)

    return df.reset_index(drop=True)


def load_and_process_sheet(file_path, sheet_name):
    raw = get_sheet(file_path=file_path, sheet_name=sheet_name)
    return process_sheet(raw, sheet_name)


def inspect_sheet(df, rows=10):
    print(df.head(rows))
    print("\nColumns:")
    print(df.columns.tolist())
    print("\nShape:")
    print(df.shape)


if __name__ == "__main__":
    for kind, sheet_name in MONTHLY_BUDGET_SHEETS.items():
        processed = load_and_process_sheet(DEFAULT_BUDGET_FILE, sheet_name)
        print(f"{kind}: {sheet_name} -> {processed.shape}")
