from DbConnector import DbConnector

"""
Contains code for tasks 5, 8 and 10

WARNING: task 5 is intense to run.
"""

def setup_indexes_and_distance_table(cursor, conn):
    print("Creating index on gps_point(trip_id, point_index)...")
    cursor.execute("""
        SELECT COUNT(*) FROM information_schema.statistics
        WHERE table_schema = DATABASE()
          AND table_name = 'gps_point'
          AND index_name = 'idx_trip_point'
    """)
    if cursor.fetchone()[0] == 0:
        cursor.execute("ALTER TABLE gps_point ADD INDEX idx_trip_point (trip_id, point_index)")
        conn.commit()
        print("Index created.")
    else:
        print("Index already exists, skipping.")

    print("Building trip_distance table (this may take a while)...")
    cursor.execute("DROP TABLE IF EXISTS trip_distance")
    cursor.execute("""
        CREATE TABLE trip_distance AS
        SELECT
            trip_id,
            SUM(
                6371 * 2 * ASIN(SQRT(
                    POWER(SIN(RADIANS(latitude - prev_lat) / 2), 2)
                    + COS(RADIANS(prev_lat)) * COS(RADIANS(latitude))
                    * POWER(SIN(RADIANS(longitude - prev_lon) / 2), 2)
                ))
            ) AS distance_km
        FROM (
            SELECT
                trip_id, latitude, longitude,
                LAG(latitude) OVER (PARTITION BY trip_id ORDER BY point_index) AS prev_lat,
                LAG(longitude) OVER (PARTITION BY trip_id ORDER BY point_index) AS prev_lon
            FROM gps_point
        ) sub
        WHERE prev_lat IS NOT NULL
        GROUP BY trip_id
    """)
    conn.commit()
    cursor.execute("ALTER TABLE trip_distance ADD PRIMARY KEY (trip_id)")
    conn.commit()
    print("trip_distance table built and indexed.")

    print("Building trip_duration table...")
    cursor.execute("DROP TABLE IF EXISTS trip_duration")
    cursor.execute("""
        CREATE TABLE trip_duration AS
        SELECT trip_id, MAX(point_index) AS max_idx
        FROM gps_point
        GROUP BY trip_id
    """)
    conn.commit()
    cursor.execute("ALTER TABLE trip_duration ADD PRIMARY KEY (trip_id)")
    conn.commit()
    print("trip_duration table built and indexed.")


def top_taxis_by_hours_and_distance(cursor, limit=10):
    cursor.execute("""
        SELECT
            t.taxi_id,
            SUM(15 * td.max_idx) / 3600 AS total_hours,
            SUM(dist.distance_km) AS total_distance_km
        FROM trip t
        JOIN trip_duration td ON td.trip_id = t.id
        JOIN trip_distance dist ON dist.trip_id = t.id
        GROUP BY t.taxi_id
        ORDER BY total_hours DESC
        LIMIT %s
    """, (limit,))

    rows = cursor.fetchall()
    print(f"Top {limit} taxis by hours and distance:")
    for taxi_id, total_hours, total_distance_km in rows:
        print(f"  Taxi {taxi_id}: {total_hours:.2f}h, {total_distance_km:.2f}km")


def midnight_crossers(cursor):
    cursor.execute("""
        SELECT t.id
        FROM trip t
        JOIN (
            SELECT trip_id, MAX(point_index) AS max_idx
            FROM gps_point
            GROUP BY trip_id
        ) mc ON mc.trip_id = t.id
        WHERE DATE(t.timestamp) <> DATE(t.timestamp + INTERVAL (15 * mc.max_idx) SECOND)
    """)
    midnight_crossers = [trip[0] for trip in cursor.fetchall()]
    print("Trips that cross midnight:")
    print(f"Total amount: {len(midnight_crossers)}")
    print("First 10:")
    for i in range(10):
        print(midnight_crossers[i])


def average_idle_time_between_trips(cursor, limit=10):
    cursor.execute(f"""
        WITH trip_times AS (
            SELECT
                t.taxi_id,
                t.timestamp AS start_ts,
                t.timestamp + INTERVAL (15 * d.max_idx) SECOND AS end_ts
            FROM trip t
            JOIN (
                SELECT trip_id, MAX(point_index) AS max_idx
                FROM gps_point
                GROUP BY trip_id
            ) d ON d.trip_id = t.id
        ),
        with_prev AS (
            SELECT
                taxi_id,
                start_ts,
                LAG(end_ts) OVER (PARTITION BY taxi_id ORDER BY start_ts) AS prev_end_ts
            FROM trip_times
        )
        SELECT
            taxi_id,
            AVG(TIMESTAMPDIFF(SECOND, prev_end_ts, start_ts)) / 3600 AS avg_idle_hours
        FROM with_prev
        WHERE prev_end_ts IS NOT NULL
        GROUP BY taxi_id
        ORDER BY avg_idle_hours DESC
        LIMIT {limit}
    """)
    top_average_idle_time_taxis = cursor.fetchall()
    print("Top average idle time taxis:")
    print(f"First {limit}:")
    for i in range(limit):
        print(f"Taxi id: {top_average_idle_time_taxis[i][0]}, average idle hours: {top_average_idle_time_taxis[i][1]}")


def main():
    connection = DbConnector()
    try:
        cursor = connection.cursor
        #setup_indexes_and_distance_table(cursor, connection.db_connection)  # run once
        #top_taxis_by_hours_and_distance(cursor, limit=10)
        #midnight_crossers(cursor)
        average_idle_time_between_trips(cursor)
    finally:
        connection.close_connection()


if __name__ == "__main__":
    main()