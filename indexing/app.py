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
            }
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
        }
    }

    return render_template('index.html', results=results['hits']['hits'],
                           query=query, from_=from_,
                           total=results['hits']['total']['value'],
                           aggs = aggs)



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
    m = re.search(subreddit_filter_regex, query)
    if m:
        filters.append({
            'term': {
                'subreddit.keyword': {
                    'value': m.group(1)
                }
            }
        })
        query = re.sub(subreddit_filter_regex, '', query).strip()

    # Filter by sentiment
    sentiment_filter_regex = r'sentiment:([^\s]+)\s*'
    m = re.search(sentiment_filter_regex, query)
    if m:
        filters.append({
            'term': {
                'sentiment.keyword': {
                    'value': m.group(1)
                }
            }
        })
        query = re.sub(sentiment_filter_regex, '', query).strip()

    return {'filter': filters}, query
