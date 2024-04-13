import csv
import json
import pandas as pd

def convert_csv_to_json(csv_file, json_file):
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_data = csv.DictReader(file)
        json_data = json.dumps(list(csv_data), indent=4)
    
    with open(json_file, 'w') as file:
        file.write(json_data)

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

def process_data(csv_file, custom_cluster, result_file):
    comment_df = pd.read_csv(csv_file)
    custom_cluster_df = pd.read_csv(custom_cluster)

    comment_df.drop_duplicates(inplace=True)
    comment_df = comment_df[comment_df['post_comment'] != '[removed]']
    comment_df = comment_df[comment_df['post_comment'] != '[deleted]']

    comment_df.drop(['senticnet_subjectivity', 'emotion', 'Unnamed: 0'], axis=1, inplace=True)
    comment_df = pd.merge(comment_df, custom_cluster_df[['post_comment', 'subreddit', 'intent']], on=['post_comment', 'subreddit'], how='left')
    comment_df.drop_duplicates(inplace=True)

    comment_df.to_csv(result_file, index=False)


if __name__ == "__main__":
    json_file = 'data/dataset.json'
    csv_file = 'data/classified_comments-sentiment.csv'
    custom_cluster = 'data/classified_comments-cluster.csv'
    result_file = 'data/classified_comments_final.csv'

    # process_data(csv_file, custom_cluster, result_file)
    # convert_csv_to_json(result_file, json_file)
    edit_post_date(json_file)
    
    print("Done")
