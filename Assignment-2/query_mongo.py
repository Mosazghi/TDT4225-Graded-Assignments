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
            "from": "Rating",
            "let": {"movieIds": "$movies.movie_id"},
            "pipeline": [
                {"$match": {
                    "$expr": {
                        "$in": ["$movie_id", "$$movieIds"]
                    }
                }},
                {"$group": {
                    "_id": None,
                    "meanRating": {"$avg": "$rating"}
                }}
            ],
            "as": "ratingStats"
        }},
    {"$unwind": "$director"},
    {"$unwind": "$ratingStats"},
    {"$project": {
        "_id": 0,
        "director_name": "$director.name",
        "medianRevenue": 1,
        "movieCount": 1,
        "meanRating": "$ratingStats.meanRating"
    }}
    ]

    for document in collection.aggregate(pipeline):
        pprint(document)


# Task 4
def largest_total_revenue_film_collectiions():
    pass


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
    finally:
        if connection:
            connection.close_connection()