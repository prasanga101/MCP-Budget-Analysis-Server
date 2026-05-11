from data.scripts.cleaner_performance import (
    EXCEL_FILE,
    clean_details_sheet,
    clean_part_sheet,
)
from data.scripts.transform_expenditure import (
    OUTPUT_DIR as PERFORMANCE_OUTPUT_DIR,
    transform_expenditure_part,
)
from data.scripts.transform_revenue import transform_revenue_part
from data.scripts.transformer_budget import build_all_budget_outputs
from data.scripts.transformer_details import transform_details
from data.scripts.validator import validate_all
from financial_mcp.data_loader import clear_cache


def validate_financial_data():
    return validate_all()


def refresh_budget_data():
    outputs = build_all_budget_outputs()
    clear_cache()
    return {
        kind: {
            "path": str(result["path"]),
            "rows": int(len(result["data"])),
            "columns": int(len(result["data"].columns)),
        }
        for kind, result in outputs.items()
    }


def refresh_financial_data():
    revenue = transform_revenue_part(clean_part_sheet(EXCEL_FILE, "Revenue Part")[0])
    expenditure = transform_expenditure_part(clean_part_sheet(EXCEL_FILE, "Expenditure Part")[0])
    details = transform_details(
        clean_details_sheet(EXCEL_FILE, "Revenue and Expenses Details")[0]
    )

    PERFORMANCE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    revenue_path = PERFORMANCE_OUTPUT_DIR / "revenue_part_long.csv"
    expenditure_path = PERFORMANCE_OUTPUT_DIR / "expenditure_part_long.csv"
    details_path = PERFORMANCE_OUTPUT_DIR / "details_long.csv"

    revenue.to_csv(revenue_path, index=False)
    expenditure.to_csv(expenditure_path, index=False)
    details.to_csv(details_path, index=False)
    budget_outputs = build_all_budget_outputs()

    clear_cache()
    return {
        "performance_revenue": {
            "path": str(revenue_path),
            "rows": int(len(revenue)),
            "columns": int(len(revenue.columns)),
        },
        "performance_expenditure": {
            "path": str(expenditure_path),
            "rows": int(len(expenditure)),
            "columns": int(len(expenditure.columns)),
        },
        "performance_details": {
            "path": str(details_path),
            "rows": int(len(details)),
            "columns": int(len(details.columns)),
        },
        "budget": {
            kind: {
                "path": str(result["path"]),
                "rows": int(len(result["data"])),
                "columns": int(len(result["data"].columns)),
            }
            for kind, result in budget_outputs.items()
        },
    }


def available_transformers():
    return [
        transform_revenue_part.__name__,
        transform_expenditure_part.__name__,
        transform_details.__name__,
        build_all_budget_outputs.__name__,
    ]
