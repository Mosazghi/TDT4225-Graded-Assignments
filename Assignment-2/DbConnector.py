from pymongo import MongoClient


class DbConnector:
    """
    Connects to the MongoDB server on the Ubuntu virtual machine.
    Connector needs HOST, USER and PASSWORD to connect.

    Example:
    HOST = "tdt4225-00.idi.ntnu.no" // Your server IP address/domain name
    USER = "testuser" // This is the user you created and added privileges for
    PASSWORD = "test123" // The password you set for said user
    """

    def __init__(self,
                 DATABASE='test',
                 HOST="127.0.0.1",
                 USER="mosa",
                 PASSWORD="mosa",
                 AUTH_SOURCE="admin"):
        # Authenticate against the database where the MongoDB user was created.
        auth_source = AUTH_SOURCE or DATABASE
        # Connect to the databases
        self.client = MongoClient(
            host=HOST,
            username=USER,
            password=PASSWORD,
            authSource=auth_source,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        try:
            # MongoClient connects lazily; selecting a database is not a check.
            self.client.admin.command("ping")
            self.db = self.client[DATABASE]
        except Exception:
            self.client.close()
            raise

        # get database information
        print("You are connected to the database:", self.db.name)
        print("-----------------------------------------------\n")

    def close_connection(self):
        # close the cursor
        # close the DB connection
        self.client.close()
        print("\n-----------------------------------------------")
        print("Connection to %s-db is closed" % self.db.name)
