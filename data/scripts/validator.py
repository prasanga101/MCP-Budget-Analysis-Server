from pathlib import Path
import sys

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.scripts.cleaner_performance import (
    EXCEL_FILE as PERFORMANCE_FILE,
    clean_details_sheet,
    clean_part_sheet,
)
from data.scripts.transform_expenditure import transform_expenditure_part
from data.scripts.transform_revenue import transform_revenue_part
from data.scripts.transformer_budget import (
    DEFAULT_BUDGET_FILE,
    OUTPUT_DIR as BUDGET_OUTPUT_DIR,
    OUTPUT_FILES as BUDGET_OUTPUT_FILES,
    transform_budget_sheet,
)
from data.scripts.transformer_details import transform_details


PERFORMANCE_OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "Performance"
PERFORMANCE_CHECKS = {
    "revenue": {
        "sheet": "Revenue Part",
        "csv": PERFORMANCE_OUTPUT_DIR / "revenue_part_long.csv",
        "builder": lambda: transform_revenue_part(
            clean_part_sheet(PERFORMANCE_FILE, "Revenue Part")[0]
        ),
    },
    "expenditure": {
        "sheet": "Expenditure Part",
        "csv": PERFORMANCE_OUTPUT_DIR / "expenditure_part_long.csv",
        "builder": lambda: transform_expenditure_part(
            clean_part_sheet(PERFORMANCE_FILE, "Expenditure Part")[0]
        ),
    },
    "details": {
        "sheet": "Revenue and Expenses Details",
        "csv": PERFORMANCE_OUTPUT_DIR / "details_long.csv",
        "builder": lambda: transform_details(
            clean_details_sheet(PERFORMANCE_FILE, "Revenue and Expenses Details")[0]
        ),
    },
}
BUDGET_CHECKS = {
    "budget_revenue": {
        "sheet": "Monthly Revenue Budget",
        "csv": BUDGET_OUTPUT_DIR / BUDGET_OUTPUT_FILES["revenue"],
        "builder": lambda: transform_budget_sheet(
            DEFAULT_BUDGET_FILE,
            "Monthly Revenue Budget",
        ),
    },
    "budget_expenditure": {
        "sheet": "Monthly Expenditure Budget",
        "csv": BUDGET_OUTPUT_DIR / BUDGET_OUTPUT_FILES["expenditure"],
        "builder": lambda: transform_budget_sheet(
            DEFAULT_BUDGET_FILE,
            "Monthly Expenditure Budget",
        ),
    },
}


def _series_equal(left, right):
    left_num = pd.to_numeric(left, errors="coerce")
    right_num = pd.to_numeric(right, errors="coerce")
    numeric_mask = left_num.notna() | right_num.notna()

    if numeric_mask.any():
        if not np.allclose(
            left_num[numeric_mask],
            right_num[numeric_mask],
            rtol=1e-9,
            atol=1e-6,
            equal_nan=True,
        ):
            return False

    left_text = left.loc[~numeric_mask].fillna("").astype(str).str.strip()
    right_text = right.loc[~numeric_mask].fillna("").astype(str).str.strip()
    return left_text.equals(right_text)


def compare_frame_to_csv(name, builder, csv_path):
    generated = builder()
    existing = pd.read_csv(csv_path)
    same_columns = generated.columns.tolist() == existing.columns.tolist()
    same_shape = generated.shape == existing.shape

    comparable = same_columns and same_shape
    same_values = False
    differing_columns = []
    if comparable:
        generated = generated.reset_index(drop=True)
        existing = existing.reset_index(drop=True)
        for col in generated.columns:
            if not _series_equal(generated[col], existing[col]):
                differing_columns.append(col)
        same_values = not differing_columns

    return {
        "name": name,
        "csv": str(csv_path),
        "generated_shape": generated.shape,
        "csv_shape": existing.shape,
        "same_columns": same_columns,
        "same_values": same_values,
        "differing_columns": differing_columns,
        "generated_columns": generated.columns.tolist(),
        "csv_columns": existing.columns.tolist(),
    }


def validate_all():
    checks = {**PERFORMANCE_CHECKS, **BUDGET_CHECKS}
    return [
        compare_frame_to_csv(name, config["builder"], config["csv"])
        for name, config in checks.items()
    ]


def main():
    results = validate_all()
    for result in results:
        status = "OK" if result["same_columns"] and result["same_values"] else "DIFF"
        print(
            f"{status} {result['name']}: "
            f"generated={result['generated_shape']} csv={result['csv_shape']}"
        )
        if not result["same_columns"]:
            print(f"  generated columns: {result['generated_columns']}")
            print(f"  csv columns:       {result['csv_columns']}")
        elif not result["same_values"]:
            print(f"  values differ in: {result['differing_columns']}")


if __name__ == "__main__":
    main()
