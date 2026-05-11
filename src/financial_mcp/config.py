from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
PERFORMANCE_DIR = PROCESSED_DIR / "Performance"
BUDGET_DIR = PROCESSED_DIR / "Budget"

CSV_PATHS = {
    "performance_revenue": PERFORMANCE_DIR / "revenue_part_long.csv",
    "performance_expenditure": PERFORMANCE_DIR / "expenditure_part_long.csv",
    "performance_details": PERFORMANCE_DIR / "details_long.csv",
    "budget_revenue": BUDGET_DIR / "monthly_revenue_budget_normalized.csv",
    "budget_expenditure": BUDGET_DIR / "monthly_expenditure_budget_normalized.csv",
}
