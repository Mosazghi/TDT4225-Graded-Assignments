from collections import defaultdict
import itertools
from pprint import pprint

from DbConnector import DbConnector


class ExampleProgram:

    def __init__(self):
        self.connection = DbConnector()
        self.client = self.connection.client
        self.db = self.connection.db

    def create_coll(self, collection_name):
        collection = self.db.create_collection(collection_name)
        print("Created collection: ", collection)

    def insert_documents(self, collection_name):
        docs = [
            {
                "_id": 1,
                "name": "Bobby",
                "courses": [
                    {
                        "code": "TDT4225",
                        "name": " Very Large, Distributed Data Volumes",
                    },
                    {"code": "BOI1001", "name": " How to become a boi or boierinnaa"},
                ],
            },
            {
                "_id": 2,
                "name": "Bobby",
                "courses": [
                    {"code": "TDT02", "name": " Advanced, Distributed Systems"},
                ],
            },
            {
                "_id": 3,
                "name": "Bobby",
            },
        ]
        collection = self.db[collection_name]
        collection.insert_many(docs)

    def fetch_documents(self, collection_name):
        collection = self.db[collection_name]
        documents = collection.find({})
        for doc in documents:
            pprint(doc)

    def drop_coll(self, collection_name):
        collection = self.db[collection_name]
        collection.drop()

    def show_coll(self):
        collections = self.client["test"].list_collection_names()
        print(collections)
    def task_2(self):
        movie_votes = {
            movie["_id"]: movie.get("vote_average")
            for movie in self.db["Movie"].find({}, {"vote_average": 1})
        }
        pairs = defaultdict(lambda: {"appearances": 0, "vote_sum": 0.0, "rated_count": 0})

        production = self.db["Production"].find({}, {"cast.person_id": 1, "movie_id": 1})
        for prod in production:
            person_ids = sorted({c["person_id"] for c in (prod.get("cast") or [])})
            vote_average = movie_votes.get(prod["movie_id"])

            for pair in itertools.combinations(person_ids, 2):
                pairs[pair]["appearances"] += 1
                if vote_average is not None:
                    pairs[pair]["vote_sum"] += vote_average
                    pairs[pair]["rated_count"] += 1

        qualified_pairs = {
            pair: {
                "appearances": data["appearances"],
                "vote_average": (
                    data["vote_sum"] / data["rated_count"]
                    if data["rated_count"] else None
                ),
            }
            for pair, data in sorted(
                pairs.items(), key=lambda item: item[1]["appearances"], reverse=True
            )
            if data["appearances"] >= 3
        }

        pprint(dict(itertools.islice(qualified_pairs.items(), 20)), sort_dicts=False)
        # pprint(qualified_pairs, sort_dicts=False)
    def task_5(self):
        # By decade (e.g., 1970s, 1980s, …) and primary genre (first element in genres),
        # what is the median runtime and movie count?
        # List results sorted by decade then median runtime (desc).
        pipeline = [
            {
                "$project": {
                    "decade": {
                        "$toInt": {
                            "$multiply": [
                                {"$floor":
                                    {"$divide":
                                        [{"$year":
                                            {"$dateFromString":
                                                {"dateString":
                                                    "$release_date"}}},
                                        10]}},
                                10
                            ]
                        },
                    },
                    "genre_id": {"$arrayElemAt": ["$genre_ids", 0]},
                    "_id": 1,
                }
            },
            {
                "$lookup": {
                    "from": "Production",
                    "localField": "_id",
                    "foreignField": "movie_id",
                    "as": "production",
                }
            },
            {
                "$unwind": "$production",
            },
            {
                "$lookup": {
                    "from": "Genres",
                    "localField": "genre_id",
                    "foreignField": "_id",
                    "as": "genre",
                }
            },
            {
                "$unwind": "$genre",
            },
            {
                "$project": {
                    "_id": 0,
                    "decade": 1,
                    "genre": "$genre.name",
                    "runtime": "$production.runtime",
                    "movie_id": "$production.movie_id",
                },
            },
            {
             "$match": {
                 "decade": {"$ne": None },
                 "genre": {"$nin": [None, ""]},
                 "runtime": {"$type": "number", "$gt": 0}
             }
            },
            {
                "$group": {
                    "_id": {
                        "decade": "$decade",
                        "genre": "$genre",
                    },
                    "median_runtime": {"$median":
                        {
                            "input": "$runtime",
                            "method": "approximate",
                        }},
                    "count": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "decade": "$_id.decade",
                    "genre": "$_id.genre",
                    "median_runtime": 1,
                    "count": 1,
                },
            },
            {
                "$sort": {
                    "decade": 1,
                    "median_runtime": -1,
                },
            }
        ]
        results = self.db["Movie"].aggregate(pipeline)
        for result in results:
            pprint(result)

    def task_8(self):

        pass




def main():
    program = None
    program = ExampleProgram()
    program.task_5()
    program.connection.close_connection()


if __name__ == "__main__":
    main()
