from elasticsearch import Elasticsearch, ConnectionError

class ElasticsearchValidator:
    def __init__(self, es_host='localhost', es_port=9200, es_index='steam_reviews'):
        """
        Initializes the ElasticsearchValidator with the required parameters.
        """
        self.es = Elasticsearch(f'http://{es_host}:{es_port}')
        self.es_index = es_index

    def count_documents(self):
        """
        Counts the number of documents in the Elasticsearch index.
        """
        try:
            response = self.es.count(index=self.es_index)
            return response['count']
        except ConnectionError as e:
            print(f"Connection error: {e}")
            return None

    def get_sample_documents(self, size=5):
        """
        Retrieves a sample of documents from the Elasticsearch index.
        """
        try:
            query = {
                "size": size,
                "query": {
                    "match_all": {}
                }
            }
            response = self.es.search(index=self.es_index, body=query)
            return response['hits']['hits']
        except ConnectionError as e:
            print(f"Connection error: {e}")
            return []

    def print_sample_documents(self, documents):
        """
        Prints sample document information in a readable format.
        """
        if not documents:
            print("No documents found.")
        else:
            for doc in documents:
                source = doc['_source']
                print(f"Document ID: {doc['_id']}")
                print(f"Review ID: {source.get('review_id')}")
                print(f"Author: {source.get('author')}")
                print(f"Review: {source.get('review')}")
                print(f"Rating: {'Positive' if source.get('rating') else 'Negative'}")
                print(f"Timestamp: {source.get('timestamp_created')}")
                print("-" * 79)

# Example usage
if __name__ == "__main__":
    validator = ElasticsearchValidator()

    # Check the total number of documents
    count = validator.count_documents()
    if count is not None:
        print(f"Total number of documents in the index: {count}")

    # Retrieve and print a sample of documents
    sample_documents = validator.get_sample_documents(size=5)
    validator.print_sample_documents(sample_documents)
