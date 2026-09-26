from DbConnector import DbConnector
from tabulate import tabulate
from trip_tables import TABLES
from haversine import haversine, Unit


class A1Program:
    def __init__(self):
        self.connection = DbConnector()
        self.db_connection = self.connection.db_connection
        self.cursor = self.connection.cursor

    def create_tables(self):
        for table_name, table_definition in TABLES.items():
            print(f"Creating table {table_name}...")
            self.cursor.execute(table_definition)
        self.db_connection.commit()

    # def insert_data(self, table_name):
    #     names = ['Bobby', 'Mc', 'McSmack', 'Board']
    #     for name in names:
    #         # Take note that the name is wrapped in '' --> '%s' because it is a string,
    #         # while an int would be %s etc
    #         query = "INSERT INTO %s (name) VALUES ('%s')"
    #         self.cursor.execute(query % (table_name, name))
    #     self.db_connection.commit()

    def fetch_data(self, table_name, limit=None):
        query = "SELECT * FROM %s"
        if limit is not None:
            query += " LIMIT %s"
        self.cursor.execute(query % (table_name, limit))
        rows = self.cursor.fetchall()
        print(f"\nData from table {table_name}, raw format:")
        print(rows)
        # Using tabulate to show the table in a nice way
        print(f"\nData from table {table_name}, tabulated:")
        print(tabulate(rows, headers=self.cursor.column_names))
        return rows

    def drop_table(self, table_name):
        print(f"Dropping table {table_name}...")
        query = "DROP TABLE %s"
        self.cursor.execute(query % table_name)

    def show_tables(self):
        self.cursor.execute("SHOW TABLES")
        rows = self.cursor.fetchall()
        print(tabulate(rows, headers=self.cursor.column_names))

    def task_1(self):
        query = "SELECT (SELECT count(distinct(taxi_id)) from trip) as taxis, (SELECT count(trip.id) from trip) as trips, (SELECT count(*) from gps_point) as gps_points;"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        print(tabulate(rows, headers=self.cursor.column_names))



    def task_4b_avg_duration(self):
        cursor = self.connection.db_connection.cursor(buffered=False)

        cursor.execute("""
            WITH trip_durations AS (
                SELECT
                    g.trip_id,
                    MAX(g.point_index) * 15 AS duration_seconds
                FROM gps_point g
                GROUP BY g.trip_id
            )
            SELECT
                t.call_type,
                AVG(td.duration_seconds) AS average_duration_seconds
            FROM trip_durations td
            JOIN trip t ON t.id = td.trip_id
            GROUP BY t.call_type;
        """)
        rows = cursor.fetchall()
        print(tabulate(rows, headers=self.cursor.column_names))

    def task_4b_avg_distance(self):
        cursor = self.connection.db_connection.cursor(buffered=False)

        cursor.execute("""
            SELECT
                g.trip_id,
                t.call_type,
                g.latitude,
                g.longitude
            FROM gps_point g
            JOIN trip t ON t.id = g.trip_id
            ORDER BY g.trip_id, g.point_index;
        """)

        distance_sum = {
            "A": 0.0,
            "B": 0.0,
            "C": 0.0,
        }

        trip_count = {
            "A": 0,
            "B": 0,
            "C": 0,
        }

        current_trip_id = None
        current_call_type = None
        previous_pos = None
        current_distance = 0.0

        for trip_id, call_type, latitude, longitude in cursor:
            current_pos = (latitude, longitude)

            if trip_id != current_trip_id:

                if current_trip_id is not None:
                    distance_sum[current_call_type] += current_distance
                    trip_count[current_call_type] += 1

                current_trip_id = trip_id
                current_call_type = call_type
                current_distance = 0.0
                previous_pos = current_pos

                continue

            current_distance += haversine(previous_pos, current_pos)

            previous_pos = current_pos

        if current_trip_id is not None:
            distance_sum[current_call_type] += current_distance
            trip_count[current_call_type] += 1

        cursor.close()

        print("Average distance per call type:")

        for call_type in ["A", "B", "C"]:
            average_distance = (
                distance_sum[call_type] / trip_count[call_type]
                if trip_count[call_type] > 0
                else 0
            )

            print(
                f"{call_type}: "
                f"{average_distance:.2f} km "
                f"({trip_count[call_type]} trips)"
            )



def main():
    program = None
    try:
        program = A1Program()
        program.task_4b_avg_duration()
        # program.show_tables()
        # program.fetch_data("gps_point", 10)
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == "__main__":
    main()
