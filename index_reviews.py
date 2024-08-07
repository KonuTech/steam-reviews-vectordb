# DOCS:
# https://partner.steamgames.com/doc/store/getreviews


import requests
from elasticsearch import Elasticsearch, helpers


class SteamReviewFetcher:
    def __init__(
        self,
        appid,
        filter="all",
        language="english",
        day_range=30,
        review_type="all",
        purchase_type="all",
        es_host="localhost",
        es_port=9200,
        es_index="steam_reviews"
    ):
        """
        Initializes the SteamReviewFetcher with the required parameters.

        :param appid: Steam application ID for the game.
        :param filter: Type of review filter.
        :param language: Language of the reviews.
        :param day_range: Number of days to consider for reviews.
        :param review_type: Type of review (all or specific).
        :param purchase_type: Type of purchase.
        """
        self.base_url = "https://store.steampowered.com/appreviews/"
        self.appid = appid
        self.filter = filter
        self.language = language
        self.day_range = day_range
        self.review_type = review_type
        self.purchase_type = purchase_type
        # self.es = Elasticsearch([{"host": es_host, "port": es_port}])
        self.es = Elasticsearch('http://localhost:9200')
        self.es_index = es_index

        # Ensure the Elasticsearch index exists
        if not self.es.indices.exists(index=self.es_index):
            self.create_index()

    def _construct_url(self):
        """
        Constructs the URL for the API request.

        :return: Full URL for the API request.
        """
        return f"{self.base_url}{self.appid}?json=1"

    def _fetch_reviews(self):
        """
        Fetches reviews from the Steam Store API.

        :return: JSON response containing the reviews.
        :raises: HTTPError if the API request fails.
        """
        url = self._construct_url()
        params = {
            "filter": self.filter,
            "language": self.language,
            "day_range": self.day_range,
            "review_type": self.review_type,
            "purchase_type": self.purchase_type,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()

    def get_reviews(self):
        """
        Retrieves and processes the reviews.

        :return: List of reviews.
        """
        review_data = self._fetch_reviews()
        reviews = review_data.get("reviews", [])
        return reviews

    def print_reviews(self):
        """
        Prints the review information in a readable format.
        """
        reviews = self.get_reviews()
        for review in reviews:
            # print(f"Review ID: {review['review_id']}")  # not working
            print(f"Author: {review['author']['steamid']}")  # working
            # print(f"Review: {review['review']}")  # working
            print(f"Rating: {'Positive' if review['voted_up'] else 'Negative'}")  # working
            print(f"Timestamp: {review['timestamp_created']}")  # working
            print("-" * 79)
    
    def create_index(self):
        """
        Defined the Elasticsearch index with the required mapping.
        """
        index_mapping = {
            "mappings": {
                "properties": {
                    "review_id": {"type": "keyword"},
                    "author": {"type": "keyword"},
                    "review": {"type": "text"},
                    "rating": {"type": "boolean"},
                    "timestamp_created": {"type": "date"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 768  # to be changed
                    }
                }
            }
        }
        self.es.indices.create(index=self.es_index, body=index_mapping, ignore=400)
    
    def index_reviews(self):
        reviews = self.get_reviews()
        actions = [
            {
                "_index": self.es_index,
                "_source": {
                    "review_id": review.get("review_id"),
                    "author": review.get("author", {}).get("steamid"),
                    "review": review.get("review"),
                    "rating": review.get("voted_up"),
                    "timestamp_created": review.get("timestamp_created"),
                    "embedding": [0] * 768  # Placeholder: Replace with actual embeddings
                }
            } for review in reviews
        ]
        helpers.bulk(self.es, actions)
        print(f"Indexed {len(reviews)} reviews into Elasticsearch.")


# Example usage
if __name__ == "__main__":
    appid = "1086940"  # 1086940 for Baldur's Gate 3
    review_fetcher = SteamReviewFetcher(appid)
    review_fetcher.index_reviews()
    review_fetcher.print_reviews()
