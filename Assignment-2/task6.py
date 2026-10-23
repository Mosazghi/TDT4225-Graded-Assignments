from pprint import pprint

from DbConnector import DbConnector


class Task3:

    def __init__(self):
        self.connection = DbConnector()
        self.client = self.connection.client
        self.db = self.connection.db

    def fetch_documents(self):
        documents = self.db["Movie"].aggregate([
            {
                "$lookup" : {
                    "from" : "Production",
                    "localField" : "_id",
                    "foreignField" : "movie_id",
                    "as" : "Mov"
                }
            },
            {"$unwind" : "$Mov"},
            {
                "$project" : {
                    "movie_id" : "_id",
                    "release_date" : 1,
                    "cast" : {"$slice" : ["$Mov.cast", 5]}
                }
            },
            {
                "$lookup" : {
                    "from" : "Cast",
                    "localField" : "cast.person_id",
                    "foreignField" : "_id",
                    "as" : "casting"
                }
            },
            {
                "$addFields": {
                    "release_year": {
                        "$year": {
                            "$dateFromString": {
                                "dateString": "$release_date",
                                "format": "%Y-%m-%d",
                                "onError": None,
                                "onNull": None
                            }
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "women_percent": {
                        "$cond": [
                            {"$gt": [{"$size": "$casting"}, 0]},
                            {
                                "$round": [
                                    {
                                        "$divide": [
                                            {
                                                "$size": {
                                                    "$filter": {
                                                        "input": "$casting",
                                                        "as": "person",
                                                        "cond": {"$eq": ["$$person.gender", 1]}
                                                    }
                                                }
                                            },
                                            {"$size": "$casting"}
                                        ]
                                    },
                                    3
                                ]
                            },
                            None
                        ]
                    }
                }
            },
            {"$match": {"release_year": {"$ne": None}}},
            {
                "$group" : {
                    "_id" : {
                        "$toInt" : {
                            "$multiply" : [
                                {"$floor" : {"$divide" : ["$release_year", 10]}},
                                10
                            ]
                        }
                    },
                    "women_avg_percent" : {
                        "$avg" : "$women_percent"
                    },
                    "movie_count" : {"$sum" : 1}
                }
            },
            {
                 "$set": {
                     "women_avg_percent": {"$round": ["$women_avg_percent", 3]}
                 }
            },
            {"$sort" : {"women_avg_percent" : -1}},
            {
                "$project" : {
                    "_id": 0,
                    "decade": "$_id",
                    "women_avg_percent": 1,
                    "movie_count" : 1
                }
            }
        ])

        for doc in documents:
            pprint(doc)

def main():
    program = None
    try:
        program = Task3()
        #program.movies_in_decades()
        program.fetch_documents()
        #program.count_movies_with_less_than_five_actors()

    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == "__main__":
    main()
