import ast
import pandas as pd
from DbConnector import DbConnector


def parse(text):
    try:
        result = ast.literal_eval(text)
        return result if isinstance(result, list) else []
    except (ValueError, SyntaxError):
        return []


def ids(text, key):
    return [item[key] for item in parse(text)]


def none_if_nan(value):
    return None if pd.isna(value) else value


def load_data():
    metadata = pd.read_csv("data/movies_metadata.csv", low_memory=False)
    credits = pd.read_csv("data/credits.csv")

    metadata["id"] = pd.to_numeric(metadata["id"], errors="coerce")
    metadata = metadata.dropna(subset=["id"]).drop_duplicates(subset="id")
    metadata["id"] = metadata["id"].astype(int)

    for column in ["budget", "revenue", "runtime", "popularity"]:
        metadata[column] = pd.to_numeric(metadata[column], errors="coerce")

    credits = credits.drop_duplicates(subset="id")
    return metadata, credits


LOOKUPS = [
    ("Genres",    "metadata", "genres",               "id",         ["name"]),
    ("Companies", "metadata", "production_companies", "id",         ["name"]),
    ("Countries", "metadata", "production_countries", "iso_3166_1", ["name"]),
    ("Languages", "metadata", "spoken_languages",     "iso_639_1",  ["name"]),
    ("Cast",      "credits",  "cast",                 "id",         ["name", "gender"]),
    ("Crew",      "credits",  "crew",                 "id",         ["name", "gender"]),
]


def insert_lookup(db, name, column_data, id_key, fields):
    unique_items = {}
    for text in column_data:
        for item in parse(text):
            unique_items[item[id_key]] = {f: item.get(f) for f in fields}

    docs = [{"_id": _id, **values} for _id, values in unique_items.items()]
    db[name].drop()
    db[name].insert_many(docs)
    print(f"Inserted {len(docs)} documents into {name}")


def insert_movies(db, metadata):
    columns = ["homepage", "original_language", "original_title", "overview",
               "popularity", "release_date", "status", "tagline", "title",
               "vote_average", "vote_count"]

    docs = []
    for row in metadata.to_dict("records"):
        doc = {"_id": row["id"]}
        for column in columns:
            doc[column] = none_if_nan(row[column])
        doc["genre_ids"] = ids(row["genres"], "id")
        doc["language_codes"] = ids(row["spoken_languages"], "iso_639_1")
        docs.append(doc)

    db["Movie"].drop()
    db["Movie"].insert_many(docs)
    print(f"Inserted {len(docs)} documents into Movie")


def insert_productions(db, metadata, credits):
    credits_by_movie = credits.set_index("id").to_dict("index")

    docs = []
    for row in metadata.to_dict("records"):
        credit = credits_by_movie.get(row["id"], {"cast": "[]", "crew": "[]"})

        cast = [{"person_id": p["id"], "character": p.get("character")}
                for p in parse(credit["cast"])]
        crew = [{"person_id": p["id"], "job": p.get("job"), "department": p.get("department")}
                for p in parse(credit["crew"])]

        docs.append({
            "movie_id": row["id"],
            "budget": none_if_nan(row["budget"]),
            "revenue": none_if_nan(row["revenue"]),
            "runtime": none_if_nan(row["runtime"]),
            "company_ids": ids(row["production_companies"], "id"),
            "country_codes": ids(row["production_countries"], "iso_3166_1"),
            "cast": cast,
            "crew": crew,
        })

    db["Production"].drop()
    db["Production"].insert_many(docs)
    print(f"Inserted {len(docs)} documents into Production")


def main():
    connection = None
    try:
        metadata, credits = load_data()
        dataframes = {"metadata": metadata, "credits": credits}

        connection = DbConnector()
        db = connection.db

        for name, source, column, id_key, fields in LOOKUPS:
            insert_lookup(db, name, dataframes[source][column], id_key, fields)

        insert_movies(db, metadata)
        insert_productions(db, metadata, credits)

    except Exception as e:
        print("ERROR:", e)
    finally:
        if connection:
            connection.close_connection()


if __name__ == "__main__":
    main()