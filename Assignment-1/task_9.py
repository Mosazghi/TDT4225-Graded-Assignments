from tabulate import tabulate

from DbConnector import DbConnector

def main():
    with DbConnector() as db:
        MAX_DISTANCE_METERS = 50
        MIN_GPS_POINTS = 10
        MIN_TOTAL_DISTANCE_METERS = 100

        trips = db.query(
            """
            WITH endpoints AS (
                SELECT
                    trip_id,
                    MIN(point_index) AS first_index,
                    MAX(point_index) AS last_index,
                    COUNT(*) AS point_count
                FROM gps_point
                GROUP BY trip_id
                HAVING COUNT(*) >= %s
            ),

            candidate_trips AS (
                SELECT
                    endpoints.trip_id,
                    endpoints.point_count,

                    ST_Distance_Sphere(
                        POINT(first_point.longitude, first_point.latitude),
                        POINT(last_point.longitude, last_point.latitude)
                    ) AS distance_m

                FROM endpoints

                JOIN gps_point AS first_point
                    ON first_point.trip_id = endpoints.trip_id
                    AND first_point.point_index = endpoints.first_index

                JOIN gps_point AS last_point
                    ON last_point.trip_id = endpoints.trip_id
                    AND last_point.point_index = endpoints.last_index

                WHERE ST_Distance_Sphere(
                    POINT(first_point.longitude, first_point.latitude),
                    POINT(last_point.longitude, last_point.latitude)
                ) <= %s
            ),

            ordered_points AS (
                SELECT
                    gp.trip_id,
                    gp.point_index,
                    gp.latitude,
                    gp.longitude,

                    LAG(gp.latitude) OVER (
                        PARTITION BY gp.trip_id
                        ORDER BY gp.point_index
                    ) AS prev_lat,

                    LAG(gp.longitude) OVER (
                        PARTITION BY gp.trip_id
                        ORDER BY gp.point_index
                    ) AS prev_lon

                FROM gps_point AS gp

                JOIN candidate_trips AS candidate
                    ON candidate.trip_id = gp.trip_id
            ),

            travelled AS (
                SELECT
                    trip_id,

                    SUM(
                        CASE
                            WHEN prev_lat IS NULL THEN 0
                            ELSE ST_Distance_Sphere(
                                POINT(prev_lon, prev_lat),
                                POINT(longitude, latitude)
                            )
                        END
                    ) AS total_distance_m

                FROM ordered_points

                GROUP BY trip_id
            )

            SELECT
                candidate.trip_id,
                candidate.distance_m,
                candidate.point_count,
                travelled.total_distance_m

            FROM candidate_trips AS candidate

            JOIN travelled
                ON travelled.trip_id = candidate.trip_id

            WHERE travelled.total_distance_m >= %s

            ORDER BY candidate.distance_m ASC
            """,
            (
                MIN_GPS_POINTS,
                MAX_DISTANCE_METERS,
                MIN_TOTAL_DISTANCE_METERS
            )
        )

        table = [
            (
                row["trip_id"],
                round(row["distance_m"], 2),
                round(row["total_distance_m"], 2),
                row["point_count"]
            )
            for row in trips
        ]

        print(
            tabulate(
                table[:20],
                headers=[
                    "trip_id",
                    "start/end distance (m)",
                    "travelled distance (m)",
                    "gps points"
                ]
            )
        )

        print(f"\nNumber of trips: {len(table)}")


if __name__ == "__main__":
    main()
