import re
from flask import Flask, render_template, request
from search import Search
from datetime import datetime
import time

app = Flask(__name__)
es = Search()


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/')
def handle_search():
    query = request.form.get('query', '')
    sentiments = {
        'positive': request.form.get('positive', ''),
        'negative': request.form.get('negative', ''),
        'neutral': request.form.get('neutral', '')
    }
    filter = request.form.get('filter', '')
    from_ = request.form.get('from_', type=int, default=0)
    size_ = 5 # This is the max number of results shown in a page. This number is also used for calculation of page number for pagination
    filters, parsed_query = extract_filters(query, sentiments, filter)

    if parsed_query:
        search_query = {
            'must': {
                'multi_match': {
                    'query': parsed_query,
                    'fields': ['post_comment', 'post_content'],
                }
            }
        }
    else:
        search_query = {
            'must': {
                'match_all': {}
            }
        }
    start_time = time.time()
    results = es.search(
        query={
            'bool': {
                **search_query,
                **filters
            }
        }, 
        aggs={
            'subreddit-agg': {
                'terms': {
                    'field': 'subreddit.keyword',
                }
            },
            'sentiment-agg': {
                'terms': {
                    'field': 'sentiment.keyword',
                }
            },
            'intent-agg': {
                'terms': {
                    'field': 'intent.keyword',
                }
            }
        },
        size=size_, 
        from_=from_,
    )
    end_time = time.time()
    
    aggs = {
        'Subreddit': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['subreddit-agg']['buckets']
        },
        'Sentiment': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['sentiment-agg']['buckets']
        },
        'Intent': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['intent-agg']['buckets']
        }
    }

    return render_template('index.html', results=results['hits']['hits'],
                           query=query, from_=from_, sentiments=sentiments, filter=filter,
                           total=results['hits']['total']['value'],
                           aggs=aggs, size_=size_, time_ = round((end_time-start_time)*1000, 2))



@app.get('/document/<id>')
def get_document(id):
    document = es.retrieve_document(id)
    title = document['_source']['post_title']
    paragraphs = document['_source']['post_comment'].split('\n')
    post_link = document['_source']['post_link']
    comment_link = document['_source']['comment_link']
    return render_template('document.html', title=title, paragraphs=paragraphs, post_link=post_link, comment_link=comment_link)



@app.cli.command()
def reindex():
    """Regenerate the Elasticsearch index."""
    response = es.reindex()
    print(f'Index with {len(response["items"])} documents created '
          f'in {response["took"]} milliseconds.')


def extract_filters(query, sentiments, filter):
    filters = []

    # Filter by subreddit
    subreddit_filter_regex = r'subreddit:([^\s]+)\s*'
    matches = re.findall(subreddit_filter_regex, filter)
    for subreddit_name in matches:
        filters.append({
            'term': {
                'subreddit.keyword': {
                    'value': subreddit_name
                }
            }
        })

    intent_filter_regex = r'intent:([^\s]+)\s*'
    matches = re.findall(intent_filter_regex, filter)
    for intent_name in matches:
        filters.append({
            'term': {
                'intent.keyword': {
                    'value': intent_name
                }
            }
        })

    # Filter by sentiment
    sentiment_values = []
    for key, value in sentiments.items():
        if value == 'on':
            sentiment_values.append(key)

    if len(sentiment_values) > 0:
        filters.append({
            'terms': {
                'sentiment.keyword': sentiment_values
            }
        })

    # Filter by date range
    date_range_regex = r'daterange:(\d{4}-\d{2}-\d{2}) (\d{4}-\d{2}-\d{2})\s*'
    matches = re.search(date_range_regex, query)
    if matches:
        date_from = matches.group(1)
        date_to = matches.group(2)
        filters.append({
            'range': {
                'post_date': {
                    'gte': datetime.strptime(date_from, "%Y-%m-%d").isoformat(),
                    'lte': datetime.strptime(date_to, "%Y-%m-%d").isoformat()
                }
            }
        })
        query = re.sub(date_range_regex, '', query).strip()  # Remove date range part from query

    return {'filter': filters}, query
