from pprint import pprint

from DbConnector import DbConnector


class Task9:

    def __init__(self):
        self.connection = DbConnector()
        self.client = self.connection.client
        self.db = self.connection.db

    def fetch_documents(self):
        result = self.db["Movie"].aggregate([
            {
                "$match" : {"original_language" : {"$ne" : "en"}}
            },
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
                "$lookup" : {
                    "from" : "Companies",
                    "localField" : "Mov.company_ids",
                    "foreignField" : "_id",
                    "as" : "Comp"
                }
            },
            {
                "$match" : {
                    "$or" : [
                        {"Comp.name" : "United States"},
                        {"Mov.country_codes" : "US"}
                    ]
                }
            },
            {
                "$lookup" : {
                    "from" : "Languages",
                    "localField" : "original_language",
                    "foreignField" : "_id",
                    "as" : "Lang"
                }
            },
            {"$unwind" : "$Lang"},
            {"$match": {"Lang.name": {"$nin": ["No Language", ""]}}},
            {
                "$group" : {
                    "_id" : "$Lang.name",
                    "movie_count" : {"$sum" : 1},
                    "example_title" : {"$first" : "$original_title"}
                }
            },
            {
                "$sort" : {"movie_count" : -1}
            },
            {
                "$project" : {
                    "movie_count" : 1,
                    "example_title" : 1
                }
            },
            { "$limit" : 10}

        ])

        for p in result:
            pprint(p)


def main():
    program = None
    try:
        program = Task9()
        program.fetch_documents()

    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == "__main__":
    main()
