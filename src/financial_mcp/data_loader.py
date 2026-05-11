from functools import lru_cache

import pandas as pd

from financial_mcp.config import CSV_PATHS


def normalize_period(period):
    if period is None:
        return None
    return str(period).strip().upper().replace(" ", "_")


def normalize_segment(segment):
    if segment is None:
        return None
    return str(segment).strip().upper()


@lru_cache(maxsize=1)
def load_dataframes():
    return {
        name: pd.read_csv(path)
        for name, path in CSV_PATHS.items()
    }


@lru_cache(maxsize=1)
def load_master_dataframe():
    frames = []

    revenue = load_dataframes()["performance_revenue"].copy()
    revenue["TYPE"] = "revenue"
    revenue["SOURCE"] = "performance"
    frames.append(revenue)

    expenditure = load_dataframes()["performance_expenditure"].copy()
    expenditure["TYPE"] = "expenditure"
    expenditure["SOURCE"] = "performance"
    frames.append(expenditure)

    details = load_dataframes()["performance_details"].copy()
    details["TYPE"] = "details"
    details["SOURCE"] = "performance"
    frames.append(details)

    budget_revenue = load_dataframes()["budget_revenue"].copy()
    budget_revenue["TYPE"] = "revenue_budget"
    budget_revenue["SOURCE"] = "budget"
    budget_revenue["PERIOD"] = (
        budget_revenue["MONTH_NAME"].astype(str) + "_" + budget_revenue["YEAR"].astype(str)
    )
    frames.append(budget_revenue)

    budget_expenditure = load_dataframes()["budget_expenditure"].copy()
    budget_expenditure["TYPE"] = "expenditure_budget"
    budget_expenditure["SOURCE"] = "budget"
    budget_expenditure["PERIOD"] = (
        budget_expenditure["MONTH_NAME"].astype(str)
        + "_"
        + budget_expenditure["YEAR"].astype(str)
    )
    frames.append(budget_expenditure)

    return pd.concat(frames, ignore_index=True, sort=False)


def clear_cache():
    load_dataframes.cache_clear()
    load_master_dataframe.cache_clear()
