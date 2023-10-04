import os
import re
import subprocess
import pandas as pd

# Ask user for name
file_name = 'Nanozoomer Registry A20-131.xlsx'

# Read the xlsx file and extract the "Label" column
df = pd.read_excel(file_name, sheet_name='Sheet1')
labels = df['label'].tolist()

# Get the list of .ndpi files sorted by creation time
svs_files = sorted([f for f in os.listdir() if f.endswith('.svs')], key=os.path.getctime)

# Rename the .ndpi files using the labels from the xlsx file
for i, svs_file in enumerate(svs_files):
    print(f"Renaming {ndpi_file} to {labels[i] + '.svs'}")
    new_name = labels[i] + '.ndpi'
    os.rename(svs_file, new_name)

