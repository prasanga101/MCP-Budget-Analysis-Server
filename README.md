# MCP Financial Data Pipeline

A Python pipeline for cleaning, validating, and transforming financial Excel reports into structured data.

## Project Structure

```
mcp/
├── data/
│   ├── scripts/
│   │   ├── cleaner.py       # Data loading, cleaning, and filtering
│   │   ├── validator.py     # Data validation logic
│   │   └── transformer.py   # Data transformation logic
│   ├── Budget Details.xlsx
│   └── Financial Performance Report_Upto Poush End, 2082.xlsx
```

## Requirements

- Python 3.10+
- pandas
- numpy
- openpyxl (for `.xlsx` support)

Install dependencies:

```bash
pip install pandas numpy openpyxl
```

## Usage

Run the cleaner script to load, clean, and inspect budget data:

```bash
python data/scripts/cleaner.py
```

### Key Functions (`cleaner.py`)

| Function | Description |
|---|---|
| `load_excel_file(path)` | Opens an Excel file and returns an `ExcelFile` object |
| `get_sheet(path, sheet_name)` | Reads a specific sheet into a DataFrame |
| `basic_clean(df)` | Strips whitespace, drops empty rows/columns, removes unnamed columns |
| `filter_rows(df)` | Removes subtotal/total/summary rows by keyword matching |
| `propagate_segments(df)` | Forward-fills the `SEGEMENT` column to assign segment labels |
| `inspect_sheet(df)` | Prints head, columns, and shape for quick inspection |

## Data Sources

- **Budget Details.xlsx** — Monthly expenditure budget by segment and line item
- **SCT Financial Performance Report** — Financial performance data up to Poush End, 2082 (BS)
