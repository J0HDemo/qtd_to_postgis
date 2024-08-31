"""
PostGIS Database Packer module

Inserts extracted positional data into the target Postgres
Spatial Database

© 2024 Kirill Romashchenko
"""
from lib.db_connector import DBConnector
import psycopg
from typing import Union

class DBPacker:
    """
    Packer class. Class instance inserts extracted spatial
    data into the target Postgres Database. Geometry type
    options are either/both points or polyline (Linestring)
    """
    def __init__(self, video: str,
                 alias: str=None) -> None:
        """Packer's constructor method.
        :param video: (str) absolute path to the folder containing
        the target video
        :param alias: (str) video identifier. None by default.
        If no alias provided, default video identifier/prefix
        (from settings.json) is used instead
        """
        from lib.settings_reader import Reader

        self.video = video
        self.alias = alias
        self.parsed_data = None
        self.default_video_alias = None

        self.settings = Reader().get_settings()
        self.schema = self.settings["Default schema"]
        self.default_names = self.settings["Default table names"]
        self.default_user = self.settings["Default user"]
        self.id_column_length = self.settings["Identifier field length"]
        self.coordinate_precision = self.settings['Coordinate precision']
        self.altitude_data_type = self.settings['Altitude data type']

    def extract_data(self) -> None:
        """Extract video's spatial data and creation date"""
        from lib.exif_extractor import EXIFExtractor
        (self.parsed_data,
         self.default_video_alias) = EXIFExtractor(self.video).extract_data()

    @staticmethod
    def create_database(connection: psycopg.Connection, database_name: str,
                        verbose: bool=True,
                        to_console: bool=False) -> Union[str, None]:
        """Creates a new Postgres Database
        :param connection: (psycopg.Connection) Database connection
        :param database_name: (str) new Database's name
        :param verbose: (bool) enables/disables informational messages.
        True by default
        :param to_console: (bool) enables return of the informational message
        for to print to GUI's console. False by default"""
        with connection.cursor() as cur:
            cur.execute(f'CREATE DATABASE {database_name}')
        message = f"{database_name} Database created"
        if verbose:
            print(message)
        if to_console:
            return message

    def create_columns(self, connection: psycopg.Connection,
                       table_names: list, geometry: str='Both') -> None:
        """
        :param connection: (psycopg.Connection) Database connection
        :param table_names: (list) a list with either one or two
        target table names as strings, depending on the geometry type.
        Empty by default, if no values provided - self.default values
        (read from settings) are applied
        :param geometry: (str) geometry type(s) flag as a string.
        Possible values:
        'Point', 'Line', 'Both'. 'Both' is the default"""
        altitude_type = "integer" if self.altitude_data_type == "integer"\
            else "decimal(6,1)"
        point_query = f"""
                        CREATE TABLE {self.schema}.{table_names[0]}
                        (id SERIAL PRIMARY KEY,
                        "video" varchar({self.id_column_length}),
                        longitude decimal({self.coordinate_precision + 4},{self.coordinate_precision}),
                        latitude decimal({self.coordinate_precision + 4},{self.coordinate_precision}),
                        altitude {altitude_type},
                        geom geometry(Point, 4326));"""
        line_query = f"""
                        CREATE TABLE {self.schema}.{table_names[0]}
                        (id SERIAL PRIMARY KEY,
                        video varchar({self.id_column_length}),
                        length decimal(8,3),
                        geom geometry(Linestring, 4326));"""
        both_query = (point_query +
                      f"""
                        CREATE TABLE {self.schema}.{table_names[1]}
                        (id SERIAL PRIMARY KEY,
                        video varchar({self.id_column_length}),
                        length decimal(8,3),
                        geom geometry(Linestring, 4326));""")
        if geometry == 'Point':
            query = point_query
        elif geometry == "Line":
            query = line_query
        elif geometry == "Both":
            query = both_query

        with connection.cursor() as cur:
            cur.execute('CREATE EXTENSION postgis;')
            cur.execute(query)
            connection.commit()

    def insert_points(self, connection: psycopg.Connection,
                      table_name: str, alias: str=None,
                      verbose: bool=True,
                      to_console: bool=False) -> Union[str, None]:
        """Inserts spatial data into the point table
        :param connection: (psycopg.Connection) Database connection
        :param table_name: (str) point table's name
        :param alias: (str) video identifier (alias). None by default.
        If no alias provided, video is identified by its creation date,
        read via the extractor module
        :param verbose: (bool) enables/disables informational messages.
        True by default
        :param to_console: (bool) enables/disables return of the
        informational message for to print to GUI's console.
        False by default"""
        identifier = alias if alias else self.default_video_alias
        for point in self.parsed_data:
            longitude = point[0]
            latitude = point[1]
            altitude = point[2]
            query = f"""
                INSERT INTO public.{table_name}(video, longitude, latitude, altitude, geom)
                VALUES('{identifier}', {longitude}, {latitude}, {altitude},
                ST_GeomFromText('POINT({longitude} {latitude})', 4326));"""

            with connection.cursor() as cur:
                cur.execute(query)
                connection.commit()
        message = 'Point data inserted'
        if verbose:
            print(message)
        if to_console:
            return message

    def insert_line(self, connection: psycopg.Connection,
                    table_name: str, alias: str=None,
                    verbose: bool=True,
                    to_console: bool=False) -> Union[str, None]:
        """Inserts spatial data into the line table
        :param connection: (psycopg.Connection) Database connection
        :param table_name: (str) line table's name
        :param alias: (str) video identifier (alias). None by default.
        If no alias provided, video is identified by its creation date,
        read with extractor module
        :param verbose: (bool) enables/disables informational message.
        True by default
        :param to_console: (bool) enables/disables return of the
        informational message for to print to GUI's console.
        False by default"""
        identifier = alias if alias else self.default_video_alias
        pairs = []
        for point in self.parsed_data:
            pairs.append(f"{point[0]} {point[1]}")
        geometry_string = ','.join(pairs)

        query = f"""INSERT INTO public.{table_name}(video, geom)
                    VALUES('{identifier}',
                    ST_GeomFromText('LINESTRING({geometry_string})', 4326));
                    UPDATE public.{table_name} SET length = ST_LengthSpheroid(geom,
                    'SPHEROID["WGS 84",6378137,298.257223563]')/1000;"""

        with connection.cursor() as cur:
            cur.execute(query)
            connection.commit()

        message = 'Line data inserted'
        if verbose:
            print(message)
        if to_console:
            return message

    def insert_both(self, connection: psycopg.Connection,
                    table_names: list,
                    alias: str=None,
                    verbose: bool=True,
                    to_console: bool=False) -> Union[tuple, None]:
        """Inserts spatial data into both point and line tables
        :param connection: (psycopg.Connection) Database connection
        :param table_names: (list) a list of target tables
        :param alias: (str) video identifier (alias). None by default.
        If no alias provided, video is identified by its creation date,
        read with extractor module
        :param verbose: (bool) enables/disables informational messages.
        True by default
        :param to_console: (bool) enables/disables return of the
        informational messages for to print to GUI's console.
        False by default"""
        point_message = self.insert_points(connection=connection,
                       table_name=table_names[0],
                       alias=alias,
                       verbose=verbose,
                       to_console=to_console)
        line_message = self.insert_line(connection=connection,
                     table_name=table_names[1],
                     alias=alias,
                     verbose=verbose,
                     to_console=to_console)
        if to_console:
            return point_message, line_message

    def pack_data(self, new: bool, db_name: str, user: str,
                  credentials: str, table_names: list,
                  geometry: str='Both', alias: str=None,
                  verbose: bool=True, to_console: bool=False) -> None:
        """Packs processed data to the Database (either new or the existing one)
        :param new: (bool) flag, enables/disables new Database creation/appending
        to the existing one
        :param db_name: (str) Database name
        :param user: (str) username
        :param credentials: (str) user's password
        :param table_names: (list) a list with either one or two target table
        names as strings, depending on the geometry type. Empty by default,
        if no values provided - self.default values (read from settings)
        are applied
        :param geometry: (str) geometry type(s) flag as a string.
        Possible values: 'Point', 'Line', 'Both'. 'Both' is the default
        :param alias: (str) video identifier (alias). None by default.
        If no alias provided, video is identified by its creation date,
        read with extractor module
        :param verbose: (bool) enables/disables informational messages.
        True by default
        :param to_console: (bool) enables/disables return of the
        informational messages for to print to GUI's console.
        False by default"""
        self.extract_data()
        db_message = None
        if new:
            postgres_connection = DBConnector(db_name='postgres',
                                              user=user,
                                              credentials=credentials,
                                              autocommit=True).connect()
            if to_console:
                db_message = self.create_database(connection=postgres_connection,
                                 database_name=db_name,
                                 verbose=False,
                                 to_console=True)
            else:
                self.create_database(connection=postgres_connection,
                                     database_name=db_name,
                                     verbose=verbose,
                                     to_console=False)
            target_connection = DBConnector(db_name=db_name,
                                            user=user,
                                            credentials=credentials).connect()
            self.create_columns(connection=target_connection,
                                table_names= table_names,
                                geometry=geometry)
        elif not new:
            target_connection = DBConnector(db_name=db_name,
                                            user=user,
                                            credentials=credentials).connect()

        if geometry == 'Point' and to_console:
            message = self.insert_points(connection=target_connection,
                               table_name= table_names[0],
                               alias=alias,
                               verbose=verbose,
                               to_console=to_console)
            if db_message:
                return db_message, message
            else:
                return message
        elif geometry == 'Point' and not to_console:
            self.insert_points(connection=target_connection,
                               table_name= table_names[0],
                               alias=alias,
                               verbose=verbose)
        elif geometry == 'Line' and to_console:
            message = self.insert_line(connection=target_connection,
                             table_name= table_names[0],
                             alias=alias,
                             verbose=verbose,
                             to_console=to_console)
            if db_message:
                return db_message, message
            else:
                return message
        elif geometry == 'Line' and not to_console:
            self.insert_line(connection=target_connection,
                             table_name= table_names[0],
                             alias=alias,
                             verbose=verbose)
        elif geometry == 'Both' and to_console:
            messages = self.insert_both(connection=target_connection,
                             table_names=table_names,
                             alias=alias,
                             verbose=verbose,
                             to_console=to_console)
            if db_message:
                return db_message, messages
            else:
                return messages
        elif geometry == 'Both' and not to_console:
            self.insert_both(connection=target_connection,
                             table_names=table_names,
                             alias=alias,
                             verbose=verbose)

