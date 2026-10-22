from pprint import pprint

from DbConnector import DbConnector


# Task 1
def highest_median_earning_director(collection):
    pipeline = [
        {"$unwind": "$crew"},
        {"$match": {"crew.job": "Director"}},
        {"$group": {
                "_id": "$crew.person_id",
                "movieCount": {"$sum": 1},
                "movies": {"$push": {
                    "movie_id": "$movie_id",
                    "revenue": "$revenue"
                }},
                "medianRevenue": {
                    "$median": {
                        "input": "$revenue",
                        "method": "approximate"
                    },
        }}},
        {"$match": {"movieCount": {"$gte": 5}}},
        {"$sort": {"medianRevenue": -1}},
        {"$limit": 10},
            {"$lookup": {
            "from": "Crew",
            "localField": "_id",
            "foreignField": "_id",
            "as": "director"
        }},
            {"$lookup": {
                "from": "Movie",
                "localField": "movies.movie_id",
                "foreignField": "_id",
                "as": "movieStats"
            }},
    {"$unwind": "$director"},
    {"$project": {
        "_id": 0,
        "director_name": "$director.name",
        "medianRevenue": 1,
        "movieCount": 1,
        "meanRating": {"$avg": "$movieStats.vote_average"}
    }}
    ]

    for document in collection.aggregate(pipeline):
        pprint(document)


# Task 4
def largest_total_revenue_film_collections(collection):
    pipeline = [
        {"$match": 
         {"belongs_to_collection":
                    {"$ne": None}}},
        {"$group": {
                "_id": "$belongs_to_collection.id",
                "collectionName":  {"$first": "$belongs_to_collection.name"},
                "collectionCount": {"$sum": 1},
                "movieIds": {"$push": "$_id"},
                "medianVoteAverage": {"$median": 
                                      {"input": "$vote_average",
                                       "method": "approximate"}},
                "earliestReleaseDate": {"$min": "$release_date"},
                "latestReleaseDate": {"$max": "$release_date"}
        }},
    {"$match": {"collectionCount": {"$gte": 3}}},
    {"$lookup": {
        "from": "Production",
        "localField": "movieIds",
        "foreignField": "movie_id",
        "as": "productions"
    }},
    {"$set": {
            "totalRevenue": {"$sum": "$productions.revenue"}
        }},
    {"$sort": {"totalRevenue": -1}},
    {"$limit": 10},
    {"$project":{
            "collectionCount": 1,
            "collectionName": 1,
            "totalRevenue": 1,
            "earliestReleaseDate": 1,
            "latestReleaseDate": 1,
            "medianVoteAverage": 1
    }}
    ]

    for document in collection.aggregate(pipeline):
        pprint(document)


# Task 7
def noir_highest_vote_average():
    pass


# Task 10
def user_ratings_info():
    pass


if __name__ == "__main__":
    connection = None
    try:
        connection = DbConnector()
        db = connection.db
        highest_median_earning_director(db["Production"])
        largest_total_revenue_film_collections(db["Movie"])
    finally:
        if connection:
            connection.close_connection()