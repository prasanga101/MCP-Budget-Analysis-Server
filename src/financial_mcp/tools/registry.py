from financial_mcp.tools.analytics import (
    get_segment_performance,
    get_total_summary,
    get_variance,
)
from financial_mcp.tools.metadata import list_datasets, list_periods, list_segments
from financial_mcp.tools.pipeline import (
    available_transformers,
    refresh_budget_data,
    refresh_financial_data,
    validate_financial_data,
)
from financial_mcp.tools.validation import search_financial_records, validate_dataset


TOOL_FUNCTIONS = [
    list_segments,
    list_periods,
    list_datasets,
    get_total_summary,
    get_variance,
    get_segment_performance,
    search_financial_records,
    validate_dataset,
    validate_financial_data,
    refresh_budget_data,
    refresh_financial_data,
    available_transformers,
]


def register_tools(mcp):
    for function in TOOL_FUNCTIONS:
        mcp.tool()(function)
    return mcp
