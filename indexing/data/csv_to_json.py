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
# for file_name in os.listdir(folder_path):
#     if file_name.endswith('.csv'):
#         csv_file = os.path.join(folder_path, file_name)
#         json_file = os.path.join(folder_path, file_name.replace('.csv', '.json'))
#         convert_csv_to_json(csv_file, json_file)
    
print('Done!')

def edit_post_date(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

    for entry in data:
        datetime_str = entry["post_date"]
        date_str = datetime_str.split()[0]  
        time_str = datetime_str.split()[1]  
        entry["post_date"] = date_str
        entry["post_time"] = time_str

    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    csv_file = "/Users/dion/Github/Y4_Projects/Sem 2/Information Retrieval/CZ4034-Information-Retrieval/crawling/reddit_post_with_separated_comments_with_datetime.csv"
    json_file = "/Users/dion/Github/Y4_Projects/Sem 2/Information Retrieval/CZ4034-Information-Retrieval/indexing/data/reddit_post_with_separated_comments_with_datetime.json"
    convert_csv_to_json(csv_file, json_file)
    edit_post_date(json_file)
