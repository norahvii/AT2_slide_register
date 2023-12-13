import os
import pandas as pd

def process_csv_file(file_name):
    df = pd.read_csv(file_name).dropna()
    labels_str = ', '.join(map(str, df['brain_region'].unique()))
    print(f"File: {file_name}\nLabels: {labels_str}")
    stain_str = ', '.join(map(str, df['stain_id'].unique()))
    print(f"Stains: {stain_str}\n")

csv_files = [file for file in os.listdir() if file.endswith('.csv')]
list(map(process_csv_file, csv_files))
