import pandas as pd
import numpy as np
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)

INPUT_DIR_PERFORMANCE ="/home/prasanga/projects/mcp/data/6. SCT_Financial Performance Report_Upto Poush End, 2082.xlsx"
INPUT_DIR_BUDGET ="/home/prasanga/projects/mcp/data/Budget Details.xlsx"


def load_excel_file(file_path):
    try:
        df = pd.ExcelFile(file_path)
        return df
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return None

def get_sheet(file_path, sheet_name):
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    except Exception as e:
        print(f"Error loading sheet '{sheet_name}': {e}")
        return None

def basic_clean(df):
    # Remove leading/trailing whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Replace empty strings with NaN
    df.replace("", np.nan, inplace=True)
    
    # Drop rows with all NaN values
    df.dropna(axis=0, how='all', inplace=True)
    df.dropna(axis=1,how='all', inplace=True)
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df.reset_index(drop=True, inplace=True)
    
    return df

def inspect_sheet(df, rows=10):
    print(df.head(rows))
    print("\nColumns:")
    print(df.columns.tolist())
    print("\nShape:")
    print(df.shape)

def classify_rows(df):
    for index, row in df.iterrows():
        print(index, row["PARTICULARS"]) 
        
def filter_rows(df):
    #Keywords for filtering
    skip_keywords=[
        "subtotal",
        "total",
        "operating profit"
    ]
    df = basic_clean(df)
    filtered_df = df[~df["PARTICULARS"].str.lower().str.contains("|".join(skip_keywords), case=False, na=False)]
    return filtered_df

def propagate_segments(df):
    df['SEGEMENT'] = df['SEGEMENT'].ffill()
    return df


def propagate_categories(df):
    # Detect category rows (I., II., III., etc.)
    category_mask = df["PARTICULARS"].str.match(
        r"^[IVXLCDM]+\.",
        na=False
    )
    # Create CATEGORY column from detected category rows
    df["CATEGORY"] = df["PARTICULARS"].where(category_mask)
    # Detect pure segment rows (A., B., C. etc. but NOT category rows)
    segment_only_mask = (
        df["S.N."].notna() &
        ~category_mask
    )
    # Reset category on new segment rows
    df.loc[segment_only_mask, "CATEGORY"] = np.nan
    # Forward fill category within valid sections
    df["CATEGORY"] = df["CATEGORY"].ffill()
    return df

def propagate_serial_numbers(df):
    df["S.N."] = df["S.N."].ffill()
    return df


def process_sheet(df, sheet_name):

    df = basic_clean(df)
    df = filter_rows(df)
    df = propagate_segments(df)
    df = propagate_serial_numbers(df)

    if sheet_name == "Monthly Revenue Budget":
        df = propagate_categories(df)

    return df


df = pd.read_excel(
    INPUT_DIR_BUDGET,
    sheet_name="Monthly Revenue Budget",
    skiprows=3
)
df = process_sheet(df, "Monthly Revenue Budget")

print(df.head(20))