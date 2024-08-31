"""
Postgres Database Connector

Establishes connection with the target Database.
Verifies PostGIS extension being enabled for the target Database.
Enables PostGIS extension for the target Database.
Retrieves lits of existing Databases, tables and columns within them.

© 2024 Kirill Romashchenko
"""
import psycopg
from typing import Union

class DBConnector:
    """Database connector class. Establishes connection with the
    target Database. Verifies PostGIS extension being enabled
    for the target Database. Includes four core methods"""
    def __init__(self, db_name: str, user: str, credentials: str,
                 autocommit: bool=True) -> None:
        """Coonector's constructor method
        :param db_name: (str) target Database name
        :param user: (str) username
        :param credentials: (str) user's password
        :param autocommit: (bool) enables/disables psycopg's
        autocommit option. True by default"""
        self.db_name = db_name
        self.user = user
        self.credentials = credentials
        self.autocommit = autocommit

    def connect(self, verbose: bool=False)\
            -> psycopg.Connection:
        """Establishes connection with the target Database
        :param verbose: (bool) enables/disables informational
        messages being shown. False by default"""
        try:
            connection = psycopg.connect(host="localhost",
                                         port=5432,
                                         dbname=self.db_name,
                                         user=self.user,
                                         password=self.credentials,
                                         autocommit=self.autocommit)
            if verbose:
                print(f"Connected to {self.db_name}")
            return connection
        except psycopg.OperationalError:
            if verbose:
                print(f"Failed to establish connection with {self.db_name} Database")

    def check_postgis(self, verbose: bool=False) -> bool:
        """Verifies if PostGIS extension is enabled for the
        target Database. Returns either True of False depending on the result.
        :param verbose: (bool) enables/disables informational
        messages being shown. False by default"""
        with self.connect() as connection:
            with connection.cursor() as cur:
                try:
                    cur.execute("""SELECT PostGIS_Full_Version();""")
                    for row in cur:
                        version = row[0].split('" [EXTENSION]')[0].rsplit(' ', 1)[1]
                    if verbose:
                        print(f"PostGIS v. {version} is"
                              f" enabled for the {self.db_name} Database")
                    return True
                except psycopg.errors.UndefinedFunction:
                    if verbose:
                        print(f"PostGIS extension is not"
                              f" enabled for the {self.db_name} Database")
                    return False

    def enable_postgis(self, verbose: bool=False) -> None:
        """Enables PostGIS extension for the target Database
        :param verbose: (bool) enables/disables informational
        messages being shown. False by default"""
        with self.connect() as connection:
            try:
                with connection.cursor() as cur:
                    cur.execute("""CREATE EXTENSION postgis;""")

                connection.commit()
                if verbose:
                    print(f"PostGIS extension enabled"
                          f" for the {self.db_name} Database")
            except psycopg.errors.DuplicateObject:
                if verbose:
                    print("PostGIS extension has"
                          " already been enabled")

    def list_data(self, structure: str, name: str=None)\
            -> Union[list, None]:
        """Returns a list of either:
        -existing Postgres Databases
        -tables within Database
        -columns within table
        :param structure: (str) a flag indicating what type of data should
        de retrieved
        :param name: (str) target table's name as a string. None by default.
        Used only for retrieving columns
        :return output: (list) queried data (if any)"""
        queries = {
            'databases':
                """SELECT datname FROM pg_database
                WHERE datistemplate = false;""",
            "tables": """
                SELECT tablename
                FROM pg_catalog.pg_tables
                WHERE schemaname != 'pg_catalog' AND 
                schemaname != 'information_schema';""",
            "columns": f"""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = '{name}';"""
        }
        query = queries[structure]
        output = []

        with self.connect() as connection:
            try:
                with connection.cursor() as cur:
                    result = cur.execute(query)
                    for unit in result:
                        output.append(unit[0])
                return output
            except:
                return None

