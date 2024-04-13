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

def convert_json_to_csv(json_file, csv_file):
    with open(json_file, 'r') as file:
        data = json.load(file)

        fieldnames = data[0].keys()

    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def process_data(comment_file, custom_cluster, custom_sentiments, result_file):
    comment_df = pd.read_csv(comment_file)
    # custom_cluster_df = pd.read_csv(custom_cluster)
    custom_sentiments_df = pd.read_csv(custom_sentiments)

    comment_df.drop_duplicates(inplace=True)
    comment_df = comment_df[comment_df['post_comment'] != '[removed]']
    comment_df = comment_df[comment_df['post_comment'] != '[deleted]']

    comment_df.drop("sentiment", axis=1, inplace=True)
    # comment_df = pd.merge(comment_df, custom_cluster_df[['post_comment', 'Cluster', 'subreddit']], on=['post_comment', 'subreddit'], how='right')
    comment_df = pd.merge(comment_df, custom_sentiments_df[['post_comment', 'sentiment', 'subreddit']], on=['post_comment', 'subreddit'], how='right')
    comment_df.rename(columns={"Cluster": "intent"}, inplace=True)
    comment_df.drop_duplicates(inplace=True)

    comment_df.to_csv(result_file, index=False)

def process_data_test():
    cluster_df = pd.read_csv('data/custom_cluster.csv')
    cluster_df.drop_duplicates(inplace=True)
    cluster_df.to_csv('data/custom_cluster_test.csv', index=False)


if __name__ == "__main__":
    json_file = 'data/dataset.json'
    csv_file = 'data/classified_comments-cluster.csv'
    csv_result_file = 'data/classified_comments-cluster.csv'
    # custom_cluster = 'data/classified_comments-cluster.csv'
    # custom_sentiments = 'data/custom_sentiments.csv'

    # process_data(csv_file, custom_cluster, custom_sentiments, csv_result_file)
    convert_csv_to_json(csv_result_file, json_file)
    # process_data_test()
    
    print("Done")
