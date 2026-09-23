from DbConnector import DbConnector
from tabulate import tabulate
from trip_tables import TABLES


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

    def fetch_data(self, table_name):
        query = "SELECT * FROM %s"
        self.cursor.execute(query % table_name)
        rows = self.cursor.fetchall()
        print(f"Data from table {table_name}, raw format:")
        print(rows)
        # Using tabulate to show the table in a nice way
        print(f"Data from table {table_name}, tabulated:")
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


def main():
    program = None
    try:
        program = A1Program()
        program.create_tables()
        program.show_tables()
        program.fetch_data("trip")
        program.fetch_data("gps_point")
    except Exception as e:
        print("ERROR: Failed to use database:", e)
    finally:
        if program:
            program.connection.close_connection()


if __name__ == '__main__':
    main()
