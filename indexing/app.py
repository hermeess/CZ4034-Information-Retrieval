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
    size_ = 5
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
        },
        size=size_, 
        from_=from_,
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
                           aggs=aggs, size_=size_)



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
