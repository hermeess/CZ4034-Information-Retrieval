import csv
import json
import os

def convert_csv_to_json(csv_file, json_file):
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_data = csv.DictReader(file)
        json_data = json.dumps(list(csv_data), indent=4)
    
    with open(json_file, 'w') as file:
        file.write(json_data)

# Specify the folder path containing the CSV files
folder_path = 'data'

# Iterate over the CSV files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        csv_file = os.path.join(folder_path, file_name)
        json_file = os.path.join(folder_path, file_name.replace('.csv', '.json'))
        convert_csv_to_json(csv_file, json_file)
    
print('Done!')
