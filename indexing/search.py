import json
from pprint import pprint
import os
import time

from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()


class Search:
    def __init__(self):
        self.es = Elasticsearch([{'host': 'localhost', 'port': 9200, "scheme": "https"}],
                                basic_auth=(os.environ['ELASTIC_USERNAME'], os.environ['ELASTIC_PASSWORD']),
                                verify_certs=False)
        client_info = self.es.info()
        print('Connected to Elasticsearch!')
        pprint(client_info.body)
        self.index_name = 'mental_health'

    def create_index(self):
        """
        Deletes the existing index and creates a new index with the specified name.
        """
        self.es.indices.delete(index=self.index_name, ignore_unavailable=True)
        self.es.indices.create(index=self.index_name)

    def insert_documents(self, documents):
            """
            Inserts a list of documents into the Elasticsearch index.

            Args:
                documents (List[Dict[str, Any]]): The list of documents to be inserted.

            Returns:
                Dict[str, Any]: The response from the Elasticsearch bulk operation.
            """
            operations = []
            for document in documents:
                operations.append({'index': {'_index': self.index_name}})
                operations.append(document)
            return self.es.bulk(operations=operations)
    
    def reindex(self, file_path='data/dataset.json'):
        self.create_index()
        with open(file_path, 'rt') as f:
            documents = json.loads(f.read())
        return self.insert_documents(documents)
    
    def search(self, **query_args):
        return self.es.search(index=self.index_name, **query_args)
    
    def retrieve_document(self, id):
        return self.es.get(index=self.index_name, id=id)


if __name__ == '__main__':
    # Test the elasticsearch connection
    search = Search()
    print('Done')