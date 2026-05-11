import pandas as pd

from financial_mcp.data_loader import (
    load_master_dataframe,
    normalize_period,
    normalize_segment,
)


def _filtered_performance(df, record_type=None, segment=None, period=None, metric=None):
    out = df[df["SOURCE"] == "performance"].copy()
    if record_type:
        out = out[out["TYPE"] == record_type]
    if segment and "SEGEMENT" in out.columns:
        out = out[out["SEGEMENT"].astype(str).str.upper() == normalize_segment(segment)]
    if period and "PERIOD" in out.columns:
        out = out[out["PERIOD"].astype(str).str.upper() == normalize_period(period)]
    if metric and "METRIC" in out.columns:
        out = out[out["METRIC"].astype(str).str.upper() == str(metric).strip().upper()]
    return out


def get_total_summary(period=None, segment=None, record_type=None, metric=None):
    df = load_master_dataframe()
    filtered = _filtered_performance(df, record_type, segment, period, metric)
    value = pd.to_numeric(filtered.get("VALUE"), errors="coerce").sum()
    return {
        "period": period,
        "segment": segment,
        "type": record_type,
        "metric": metric,
        "rows": int(len(filtered)),
        "total": float(value),
    }


def get_variance(segment=None, period=None, record_type="revenue"):
    df = load_master_dataframe()
    filtered = _filtered_performance(df, record_type, segment, period)
    if "METRIC" not in filtered.columns:
        return {"error": "No METRIC column available for this dataset."}

    totals = (
        filtered.assign(VALUE_NUM=pd.to_numeric(filtered["VALUE"], errors="coerce"))
        .groupby("METRIC")["VALUE_NUM"]
        .sum()
        .to_dict()
    )
    budget = float(totals.get("BUDGET", 0.0))
    actual = float(totals.get("ACTUAL", 0.0))
    variance = float(totals.get("VARIANCE", actual - budget))
    achievement_pct = (actual / budget * 100) if budget else None

    return {
        "segment": segment,
        "period": period,
        "type": record_type,
        "budget": budget,
        "actual": actual,
        "variance": variance,
        "achievement_pct": achievement_pct,
    }


def get_segment_performance(period=None, record_type="revenue", metric="ACTUAL", limit=5):
    df = load_master_dataframe()
    filtered = _filtered_performance(df, record_type, period=period, metric=metric)
    if "SEGEMENT" not in filtered.columns:
        return []

    ranked = (
        filtered.assign(VALUE_NUM=pd.to_numeric(filtered["VALUE"], errors="coerce"))
        .groupby("SEGEMENT", dropna=True)["VALUE_NUM"]
        .sum()
        .sort_values(ascending=False)
        .head(int(limit))
    )
    return [
        {"segment": segment, "value": float(value)}
        for segment, value in ranked.items()
    ]
