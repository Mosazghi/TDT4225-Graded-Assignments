import csv
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from DbConnector import DbConnector

DATASET_PATH = Path.cwd() / "porto" / "porto.csv"

trip_insert_query = "INSERT INTO trip (id, call_type, origin_call_id, origin_stand_id, taxi_id, timestamp, day_type, missing_data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
gps_point_insert_query = "INSERT INTO gps_point (trip_id, point_index, latitude, longitude) VALUES (%s, %s, %s, %s)"


@dataclass
class Trip:
    id: int
    call_type: str
    origin_call: int | None
    origin_stand: int | None
    taxi_id: int
    timestamp: int
    day_type: str
    missing_data: bool

@dataclass
class GPSPoint:
    # id: int
    trip_id: int
    point_index: int
    longitude: float
    latitude: float

@dataclass
class TripFromCSV:
    trip_id: int
    call_type: str
    origin_call: int | None
    origin_stand: int | None
    taxi_id: int
    timestamp: int
    day_type: str
    missing_data: bool
    polyline: list[list[float]]

def parse_raw_trip(row: dict) -> TripFromCSV:
    polyline = json.loads(row["POLYLINE"])
    return TripFromCSV(
        trip_id=int(row["TRIP_ID"]),
        call_type=row["CALL_TYPE"],
        origin_call=int(row["ORIGIN_CALL"]) if row["ORIGIN_CALL"] else None,
        origin_stand=int(row["ORIGIN_STAND"]) if row["ORIGIN_STAND"] else None,
        taxi_id=int(row["TAXI_ID"]),
        timestamp=int(row["TIMESTAMP"]),
        day_type=row["DAY_TYPE"],
        missing_data=row["MISSING_DATA"].strip().lower() == "true",
        polyline=polyline
    )
def parse_gps_point(raw_trip: TripFromCSV) -> list[GPSPoint]:
    if not raw_trip.polyline:
        return []
    return [
        GPSPoint(trip_id=raw_trip.trip_id, point_index=i, longitude=lon, latitude=lat)
        for i, (lon, lat) in enumerate(raw_trip.polyline)
    ]

def inject_into_db(cursor, conn, batch_size: int = 25_000) -> None:
    batch = []

    def insert():
        try:
            unique_trips = {}
            for trip, points in batch:
                unique_trips.setdefault(trip.trip_id, (trip, points))

            trip_ids = tuple(unique_trips)
            placeholders = ", ".join(["%s"] * len(trip_ids))
            cursor.execute(
                f"SELECT id FROM trip WHERE id IN ({placeholders})", trip_ids
            )
            existing_ids = {row[0] for row in cursor.fetchall()}
            new_trips = [
                entry for trip_id, entry in unique_trips.items()
                if trip_id not in existing_ids
            ]

            trips = [
                (
                    trip.trip_id, trip.call_type, trip.origin_call,
                    trip.origin_stand, trip.taxi_id,
                    datetime.fromtimestamp(trip.timestamp, timezone.utc).replace(tzinfo=None),
                    trip.day_type, trip.missing_data,
                )
                for trip, _ in new_trips
            ]
            if trips:
                cursor.executemany(trip_insert_query, trips)

            gps_points = [
                (point.trip_id, point.point_index, point.latitude, point.longitude)
                for _, points in new_trips
                for point in points
            ]
            if gps_points:
                cursor.executemany(gps_point_insert_query, gps_points)

            conn.commit()
            print(f"Inserted {len(trips)} trips; skipped {len(batch) - len(trips)} duplicates")
            batch.clear()
        except Exception as e:
            print(f"Error inserting: {e}")
            try:
                conn.rollback()
            except Exception as rollback_error:
                print(f"Rollback failed: {rollback_error}")
            raise


    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            print(f"Processing {row['TRIP_ID']} ({i})")

            trip = parse_raw_trip(row)
            gps_points = parse_gps_point(trip)
            batch.append((trip, gps_points))

            if len(batch) >= batch_size:
                insert()

        if batch:
            insert()

def main():
    connection = DbConnector()
    try:
        inject_into_db(connection.cursor, connection.db_connection)
    finally:
        connection.close_connection()



if __name__ == "__main__":
    main()
