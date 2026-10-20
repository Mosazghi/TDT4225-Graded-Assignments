from pprint import pprint

from DbConnector import DbConnector


class Task3:

    def __init__(self):
        self.connection = DbConnector()
        self.client = self.connection.client
        self.db = self.connection.db

    def fetch_documents(self):
        self.db["Production"].create_index("movie_id")

        collection = self.db["Movie"]
        documents = collection.aggregate([
            {
                "$lookup": {
                    "from": "Production",
                    "localField": "_id",
                    "foreignField": "movie_id",
                    "as": "Mov"
                },
            },
            {"$unwind": "$Mov"},
            {"$project": {
                "movie_id": "$_id",
                "genre_ids": 1,
                "cast": "$Mov.cast"
            }},
            {"$unwind": "$cast"},
            {
                "$group": {
                    "_id": "$cast.person_id",
                    "genre_arrays": {"$addToSet": "$genre_ids"},
                    "movie_ids": {"$addToSet": "$movie_id"}
                }
            },
            {
                "$addFields": {
                    "movie_count": {"$size": "$movie_ids"}
                }
            },
            {"$match": {"movie_count": {"$gte": 10}}},
            {
                "$project": {
                    "movie_count": 1,
                    "all_genres": {
                        "$reduce": {
                            "input": "$genre_arrays",
                            "initialValue": [],
                            "in": {"$setUnion": ["$$value", "$$this"]}
                        }
                    }
                }
            },
            {
                "$lookup": {
                    "from": "Genres",
                    "localField": "all_genres",
                    "foreignField": "_id",
                    "as": "genre_docs"
                }
            },
            {
                "$lookup": {
                    "from": "Cast",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "casting"
                },
            },
            {
                "$addFields": {
                    "genre_count": {"$size": "$all_genres"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": {"$arrayElemAt": ["$casting.name", 0]},
                    "genre_count": 1,
                    "movie_count": 1,
                    "genres": {"$slice": ["$genre_docs.name", 5]}
                }
            },
            {"$sort": {"genre_count": -1, "movie_count": -1}},
            {"$limit": 10}
        ], allowDiskUse=True)
        for doc in documents:
            pprint(doc)

def main():
    program = None
    try:
        program = Task3()
        program.fetch_documents()

    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == "__main__":
    main()
