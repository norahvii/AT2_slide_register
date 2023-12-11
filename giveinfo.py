import os
import pandas as pd

def process_csv_file(file_name):
    # read file
    df = pd.read_csv(file_name)
    df = df.dropna()

    labels_str = ', '.join(map(str, set(df['brain_region'])))
    print(f"File: {file_name}\nLabels: {labels_str}")
    stain_str = ', '.join(map(str, set(df['stain_id'])))
    print(f"Stains: {stain_str}\n")

# Get a list of all CSV files in the current working directory
csv_files = [file for file in os.listdir() if file.endswith('.csv')]

# Iterate through each CSV file and process it
for file_name in csv_files:
    process_csv_file(file_name)
