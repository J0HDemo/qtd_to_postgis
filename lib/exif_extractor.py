"""
EXIF extractor module

Extracts positional information from video's data via the EXIFTool.
Returns parsed data as a nested list

© 2024 Kirill Romashchenko
"""

class EXIFExtractor:
    """
    EXIF extractor class. Class instance validates input and sets
    up processing. extract_data method performs module's functionality.
    """
    def __init__(self, input_path: str) -> None:
        """Instantiates class. Verifies input. Reads processing parameters (settings.json)
        :param input_path: (str) absolute path to the folder, containing target file
        """
        import os
        from lib.settings_reader import Reader

        self.settings = Reader().get_settings() # Settings setup
        self.coordinate_precision = self.settings['Coordinate precision']  # 8 by default
        self.altitude_data_type = self.settings['Altitude data type'] # Integer by default
        self.prefix = self.settings["Default prefix"]  # Default prefix for the video identifier
        self.default_file = self.settings["Default filename"]  # origin_6_lrv.mp4 by default

        self.exe_path = "lib/exiftool.exe"  # Paths setup
        self.input_path = input_path
        self.video_path = f"{input_path}/{self.default_file}"
        assert os.path.exists(self.input_path), 'The input is invalid'
        assert os.path.exists(self.video_path), 'The input folder does not contain target filess'
        self.parent_folder = (os.path.abspath(os.path.join(os.getcwd(), os.pardir)))

    def __repr__(self) -> str:
        """
        Overwrite of the built-in __repr__ method for the extractor class instance
        """
        return f"{self.__class__.__name__} (input_path={self.input_path})"

    def __str__(self) -> str:
        """
        Overwrite of the built-in __str__ method for the extractor class instance
        """
        return f"{self.__class__.__name__} instance for {self.input_path})"

    def extract_data(self) -> (list, str):
        """
        Extracts spatial data and video's creation time from EXIF
        to list via the parse_data method.
        :return: (tuple) parsed data with three values per point
        (i.e. per each (succesfull) GPS measurement) as a list
        and video's creation time as a string
        """
        import subprocess, shlex

        query = f'{self.exe_path} -G1 -a -s' f' -ee3\
        -p "$gpslongitude, $gpslatitude, $gpsaltitude#"'\
        f' -api largefilesupport=1 -c "%.8f" {self.video_path}'

        args = shlex.split(query)
        output, error = subprocess.Popen(args=args, stdout=subprocess.PIPE,
                                         stderr=subprocess.DEVNULL).communicate()
        parsed_lines = output.splitlines()
        raw_output = []
        for line in parsed_lines:
            raw_output.append(line.decode())

        processed_output = self.parse_data(raw_data=raw_output)
        default_name = self.extract_default_name()

        return processed_output, default_name

    def parse_data(self, raw_data: list) -> list:
        """Converts parsed raw output into a list
        :param raw_data: (list) a list of strings with stoutput's parsed lines
        :return: parsed_data: (list) a list of nested lists of three
        coordinate values per each (succesfull) GPS measurement"""
        parsed_data = []
        for line in raw_data:
            initial_split = line.split(',')

            hemisphere_ew = initial_split[0][-1]  # Longitudes
            longitude_value = float(initial_split[0][:-2])
            longitude = longitude_value if hemisphere_ew == 'E'\
                else longitude_value*-1

            hemisphere_ns = initial_split[1][-1]  # Latitudes
            latitude_value = float(initial_split[1][1:-2])
            latitude = latitude_value if hemisphere_ns == 'N'\
                else latitude_value*-1

            altitude = int(float(initial_split[2][1:])) if\
                self.altitude_data_type == 'integer'\
                    else round((float(initial_split[2][1:])), 1)

            parsed_data.append([longitude, latitude, altitude])

        return parsed_data

    def extract_default_name(self) -> str:
        """Extracts 'CreateData' EXIF tag to be used as video's
        possible default identifier/name (if no name provided during
        the later processing stages)
        :return formated_date: (str) video creation time formated
        with underscores"""
        import subprocess, shlex

        query = f'{self.exe_path} -G1 -a -s -createdate\
        -api largefilesupport=1 {self.video_path}'

        date_args = shlex.split(query)
        output, error = subprocess.Popen(args=date_args, stdout=subprocess.PIPE,
                                         stderr=subprocess.DEVNULL).communicate()

        raw_line = output.splitlines()[0].decode()
        no_colons = raw_line.split(': ')[1].replace(':', '_')
        formated_name = f"{self.prefix}_{no_colons.replace(' ', '_')}"

        return formated_name

