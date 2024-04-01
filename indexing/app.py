import re
from flask import Flask, render_template, request
from search import Search
from datetime import datetime

app = Flask(__name__)
es = Search()


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/')
def handle_search():
    query = request.form.get('query', '')
    from_ = request.form.get('from_', type=int, default=0)
    filters, parsed_query, date_from, date_to = extract_filters(query)

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
    
    default_start_date = "1999-01-01"
    default_end_date = "2025-12-31"

    # If date_from and date_to are None, use default values
    if date_from is None:
        date_from = default_start_date
    if date_to is None:
        date_to = default_end_date

    # Convert default dates to ISO format
    date_from_iso = datetime.strptime(date_from, "%Y-%m-%d").isoformat()
    date_to_iso = datetime.strptime(date_to, "%Y-%m-%d").isoformat()


    # Define date range aggregation with custom date range
    date_range_filter = {
    'range': {
        'post_date': {
            'gte': date_from_iso,
            'lte': date_to_iso
        }
    }
}

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
            # 'date-range-agg': date_range_filter
        },
        size=5, 
        from_=from_,
        post_filter=date_range_filter
    )
    
    aggs = {
        'Subreddit': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['subreddit-agg']['buckets']
        },
        'Sentiment': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['sentiment-agg']['buckets']
        },
    }

    return render_template('index.html', results=results['hits']['hits'],
                           query=query, from_=from_,
                           total=results['hits']['total']['value'],
                           aggs=aggs)



@app.get('/document/<id>')
def get_document(id):
    document = es.retrieve_document(id)
    title = document['_source']['post_title']
    paragraphs = document['_source']['post_comment'].split('\n')
    return render_template('document.html', title=title, paragraphs=paragraphs)



@app.cli.command()
def reindex():
    """Regenerate the Elasticsearch index."""
    response = es.reindex()
    print(f'Index with {len(response["items"])} documents created '
          f'in {response["took"]} milliseconds.')


def extract_filters(query):
    filters = []

    # Filter by subreddit
    subreddit_filter_regex = r'subreddit:([^\s]+)\s*'

    matches = re.findall(subreddit_filter_regex, query)

    for subreddit_name in matches:
        filters.append({
            'term': {
                'subreddit.keyword': {
                    'value': subreddit_name
                }
            }
        })

    query = re.sub(subreddit_filter_regex, '', query).strip()

    # Filter by sentiment
    sentiment_filter_regex = r'sentiment:([^\s]+)\s*'

    matches = re.findall(sentiment_filter_regex, query)

    for sentiment in matches:
        filters.append({
            'term': {
                'sentiment.keyword': {
                    'value': sentiment
                }
            }
        })

    query = re.sub(sentiment_filter_regex, '', query).strip()

    # Filter by date range
    date_range_regex = r'daterange:(\d{4}-\d{2}-\d{2}) (\d{4}-\d{2}-\d{2})\s*'
    matches = re.search(date_range_regex, query)

    if matches:
        date_from = matches.group(1)
        date_to = matches.group(2)
    else:
        date_from = None
        date_to = None

    return {'filter': filters}, query, date_from, date_to
