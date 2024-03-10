import re
from flask import Flask, render_template, request
from search import Search


app = Flask(__name__)
es = Search()


@app.get('/')
def index():
    return render_template('index.html')


@app.post('/')
def handle_search():
    query = request.form.get('query', '')
    from_ = request.form.get('from_', type=int, default=0)
    filters, parsed_query = extract_filters(query)

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
    
    default_start_date = "2023-01-01"
    default_end_date = "2023-12-01"
    date_from = request.form.get('date_from', default_start_date)
    date_to = request.form.get('date_to', default_end_date)

    # Define date range aggregation with custom date range
    date_range_agg = {
        'date_range': {
            'field': 'post_date',
            'ranges': [
                {'from': date_from, 'to': date_to, 'key': 'custom_date_range'}
            ]
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
            'date-range-agg': date_range_agg
        },
        size=5, 
        from_=from_
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
        'CustomDateRange': {
            bucket['key']: bucket['doc_count']
            for bucket in results['aggregations']['date-range-agg']['buckets']
        }
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
    date_range_regex = r'customdaterange:(\d{4}-\d{2}-\d{2}) (\d{4}-\d{2}-\d{2})\s*'

    matches = re.findall(date_range_regex, query)

    for date_range in matches:
        date_from, date_to = date_range
        filters.append({
            'range': {
                'post_date': {
                    'gte': date_from,
                    'lte': date_to
                }
            }
        })

    query = re.sub(date_range_regex, '', query).strip()

    return {'filter': filters}, query
