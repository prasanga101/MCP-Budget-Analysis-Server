import pandas as pd
import os
from dotenv import load_dotenv  
load_dotenv()  # Load environment variables from .env file
from data.scripts.cleaner_budget import process_sheet
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)
# pd.set_option('display.max_rows', None)
def normalize_monthly_data(df):

    id_columns = [
        "S.N.",
        "SEGEMENT",
        "PARTICULARS",
        "BUDGETED AMOUNT FOR THE YEAR (NPR)"
        ]
    if "CATEGORY" in df.columns:
        id_columns.append("CATEGORY")
        
    month_columns = [
        col for col in df.columns
        if col not in id_columns
        ]
    
    normalized_df = pd.melt(
        df,
        id_vars=id_columns,
        value_vars=month_columns,
        var_name="MONTH",
        value_name="VALUE"
    )
    return normalized_df


df = pd.read_excel(
    os.getenv("INPUT_DIR_BUDGET"),
    sheet_name="Monthly Revenue Budget",
    skiprows=3
)
df = process_sheet(df, "Monthly Expenditure Budget")
normalized_df = normalize_monthly_data(df)
normalized_df = normalized_df[
    normalized_df["VALUE"].notna()
]
normalized_df[["MONTH_NAME", "YEAR"]] = (
    normalized_df["MONTH"]
    .str.split(expand=True)
)
normalized_df = normalized_df.drop(columns=["MONTH"])

normalized_df.to_csv(
    "data/processed/Budget/monthly_revenue_budget_normalized.csv",
    index=False
)
normalized_df.to_csv(
    "data/processed/Budget/monthly_expenditure_budget_normalized.csv",
    index=False
)

# print(normalized_df.head(20))
print(normalized_df.shape)
print(normalized_df.columns.tolist())