from haversine import haversine
from tabulate import tabulate

from DbConnector import DbConnector

def main():
    with DbConnector() as db:
        porto_city_hall = (41.15794, -8.62911)
        rows = db.query(
            "SELECT trip_id, longitude, latitude FROM gps_point "
            "WHERE latitude BETWEEN %s AND %s AND longitude BETWEEN %s AND %s",
            (
                41.15794 - 0.001,
                41.15794 + 0.001,
                -8.62911 - 0.0013,
                -8.62911 + 0.0013,
            ),
        )

        trips = {}
        for row in rows:
            distance = haversine(
                porto_city_hall,
                (row["latitude"], row["longitude"]),
            )
            if distance <= 0.1:
                trips[row["trip_id"]] = min(
                    distance,
                    trips.get(row["trip_id"], distance),
                )

        print(
            f"{len(rows)} points in box, {len(trips)} trips "
            "within 100 m of Porto City Hall"
        )
        table = sorted(trips.items(), key=lambda trip: trip[1])
        print(
            tabulate(
                table[:20],
                headers=["trip_id", "closest distance (km)"],
            )
        )


if __name__ == "__main__":
    main()
