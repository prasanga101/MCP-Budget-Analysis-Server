from financial_mcp.data_loader import load_master_dataframe


def list_segments():
    df = load_master_dataframe()
    segment_col = "SEGEMENT"
    if segment_col not in df.columns:
        return []
    return sorted(
        value
        for value in df[segment_col].dropna().astype(str).str.strip().unique().tolist()
        if value
    )


def list_periods():
    df = load_master_dataframe()
    if "PERIOD" not in df.columns:
        return []
    return sorted(
        value
        for value in df["PERIOD"].dropna().astype(str).str.strip().unique().tolist()
        if value
    )


def list_datasets():
    return [
        "performance_revenue",
        "performance_expenditure",
        "performance_details",
        "budget_revenue",
        "budget_expenditure",
    ]
