import mlcroissant as mlc
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta  # Handles accurate year subtraction

# Fetch the Croissant JSON-LD
croissant_dataset = mlc.Dataset("https://www.kaggle.com/datasets/sohier/interest-rate-records/croissant/download")

# Check what record sets are in the dataset
record_sets = croissant_dataset.metadata.record_sets
print(record_sets)

# Fetch the records and put them in a DataFrame
record_set_df = pd.DataFrame(croissant_dataset.records(record_set=record_sets[0].uuid))

# Print the actual column names for debugging
print("Columns in dataset:", record_set_df.columns.tolist())

# Define the expected column names
columns_to_keep = ["data.csv/1_year_treasury_bill",
                   "data.csv/10_year_treasury_constant_maturity",
                   "data.csv/time_period", "data.csv/federal_funds"]

# Filter only existing columns
existing_columns = [col for col in columns_to_keep if col in record_set_df.columns]
if not existing_columns:
    raise KeyError("None of the expected columns are found in the dataset.")

record_set_df = record_set_df[existing_columns]


if "data.csv/time_period" in record_set_df.columns:
    record_set_df["data.csv/time_period"] = pd.to_datetime(record_set_df["data.csv/time_period"], errors='coerce')
    record_set_df = record_set_df.dropna(subset=["data.csv/time_period"])  # Drop NaT values

    # Find the maximum date in the dataset
    max_date = record_set_df["data.csv/time_period"].max()

    # Compute the cutoff date
    ten_years_ago = max_date - relativedelta(years=10)

    # Filter records within the last 10 years from max_date
    filtered_df = record_set_df[record_set_df["data.csv/time_period"] >= ten_years_ago]

    # Rename columns
    rename_columns = {
        "data.csv/1_year_treasury_bill": "1_year_treasury_bill",
        "data.csv/10_year_treasury_constant_maturity": "10_year_treasury_constant_maturity",
        "data.csv/time_period": "time_period",
        "data.csv/federal_funds": "federal_funds"
    }
    filtered_df.rename(columns = rename_columns, inplace = True)

    # Save the filtered DataFrame as a CSV file
    csv_filename = "interest_rate_records.csv"
    filtered_df.to_csv(csv_filename, index=False)
    print(f"Dataset filtered for the last 10 years from {max_date.date()} and saved as {csv_filename}")
else:
    print("Column 'data.csv/time_period' not found in dataset. Skipping filtering.")
