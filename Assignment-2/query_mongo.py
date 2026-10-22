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
def noir_highest_vote_average(collection):
    pipeline = [
        {"$match": {
            "$text": {"$search": "noir"}
        }},
        {"$sort": {"vote_average": -1}},
        {
            "$set": {
                "year": {"$substr": ["$release_date", 0, 4]}
        }},
        {"$match": {"vote_count": {"$gte": 50}}},
        {"$limit": 20},
        {"$project": {
            "vote_average": 1,
            "vote_count": 1,
            "title": 1,
            "year": 1

    }}
    ]

    for document in collection.aggregate(pipeline):
        pprint(document)

# Task 10
def user_ratings_info(collection):
    pipeline = [
        {"$group": {
        "_id": "$user_id",
        "movieIds": {"$addToSet": "$movie_id"},
        "ratingCount": {"$sum": 1},
        "ratingStandardDeviation": {
            "$stdDevPop": "$rating"
    }}},
    {"$set": {
        "ratingVariance": {
        "$pow": ["$ratingStandardDeviation", 2]}}},
        {"$lookup": {
                "from": "Movie",
                "localField": "movieIds",
                "foreignField": "_id",
                "as": "movies"}},
        {"$set": {
                "genres": {
                    "$reduce": {
                        "input": "$movies.genre_ids",
                        "initialValue": [],
                        "in": {"$setUnion": ["$$value", "$$this"]},
                    }
                }
            }},
    {"$set": {"genreCount": {"$size": "$genres"}}},
    {"$sort": {"ratingVariance": -1}},
    {"$match": {"ratingCount": {"$gte": 20}}},
    {"$limit": 10},
    {"$project": {
            "ratingCount": 1,
            "genreCount": 1,
            "ratingVariance": 1}}
    ]

    for document in collection.aggregate(pipeline):
        pprint(document)

    pipeline = [
        {"$group": {
        "_id": "$user_id",
        "movieIds": {"$addToSet": "$movie_id"},
        "ratingCount": {"$sum": 1},
        "ratingStandardDeviation": {
            "$stdDevPop": "$rating"
    }}},
    {"$set": {
        "ratingVariance": {
        "$pow": ["$ratingStandardDeviation", 2]}}},
        {"$lookup": {
                "from": "Movie",
                "localField": "movieIds",
                "foreignField": "_id",
                "as": "movies"}},
        {"$set": {
                "genres": {
                    "$reduce": {
                        "input": "$movies.genre_ids",
                        "initialValue": [],
                        "in": {"$setUnion": ["$$value", "$$this"]},
                    }
                }
            }},
    {"$set": {"genreCount": {"$size": "$genres"}}},
    {"$sort": {"genreCount": -1}},
    {"$limit": 10},
    {"$project": {
            "ratingCount": 1,
            "genreCount": 1,
            "ratingVariance": 1}}
    ]

    for document in collection.aggregate(pipeline):
        pprint(document)


if __name__ == "__main__":
    connection = None
    try:
        connection = DbConnector()
        db = connection.db
        highest_median_earning_director(db["Production"])
        largest_total_revenue_film_collections(db["Movie"])

        # Run index creation once for Task 7
        db["Movie"].create_index([
            ("overview", "text"),
            ("tagline", "text")
        ])

        noir_highest_vote_average(db["Movie"])

        user_ratings_info(db["Rating"])

    finally:
        if connection:
            connection.close_connection()