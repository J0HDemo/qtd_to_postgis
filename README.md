# QuickTime Data to PostGIS
## Introduction

### App's purpose
**QuickTime Data to PostGIS** extracts desired geospatial information out of the QuickTime data of .mp4 video files.
More specifically, this App is predominantly used for extracting GPS tracks of the raw 360-degrees videos, shot with
[Insta360 Pro cameras](https://www.insta360.com/ru/product/insta360-pro/). Core use cases of the App include:

1. Quick evaluation of the footage's spatial location if source folders were not named properly (folder names are ambiguous/non-descriptive) "at the field".
2. Production priority-setting/planning - planning the order of "stitching" (processing of the raw videos), based on the evaluated spatial location of the particular footage.
3. Checking if GPS data is missing partially (or entirely) prior to the processing stage of particular video.
4. Further use of the footage's spatial data per se in production.

Application extracts GPS tags for longitute, latitude and altitude (for each GPS measure) and inserts data to the Postgres Spatial Database. Data can be stored as points (one point per GPS measure),
lines (Linestring PostGIS geometry type) or both types simultaneously. Extracted data can be either inserted into the existing Database (the way it's done most of the time
in the real production) or to the brand new Database.

The full list of QuickTime File Format (QTFF) tags is listed on ExifTool's [website](https://exiftool.org/TagNames/QuickTime.html). Any of the tags might be extracted (if present in the source) with slight modifications to the App's code.

### Basic info
**QuickTime Data to PostGIS** is a Python 3.x (tested on 3.7+) application build on top of the [ExifTool by Phil Harvey](https://github.com/exiftool/exiftool).
Application is designed for
Windows 64-bit systems and requires an ExifTool executable to perform its functions. See install section for details.

**QuickTime Data to PostGIS** is distributed under the [MIT License](https://opensource.org/license/mit).

## Install

### Application

Download **QuickTime Data to PostGIS** source code to the desired folder.

### ExifTool
Download the latest 64-bit.exe of ExifTool from the [official website](https://exiftool.org/index.html).

The latest ExifTool's release at the time of writing is **12.92**. Unzip the archive and copy the executable to the App's _lib_ folder/package.

### Dependencies
Install dependencies. Application depends of the following third-party libraries:

- [psycopg (3)](https://github.com/psycopg/psycopg)
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter)
- [CTkMessagebox](https://github.com/Akascape/CTkMessagebox)
- [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap)

All dependencies are listed in the _requirements.txt_. Three out of four packages (except psycopg) are required for the GUI mode only.

### Known issues
Several minor edits to the dependencies source code might be required on some systems for to run the GUI.
Specifically, customtkinter's [bad screen distance issue](https://github.com/TomSchimansky/CustomTkinter/issues/571#issuecomment-1943482147) is fixed via
converting the returned float value to integers in two methods (__apply_widget_scaling_ and __reverse_widget_scaling_), see _./windows/widgets/scaling_ module.

``` python
def _apply_widget_scaling(self, value: Union[int, float]) -> Union[float, int]:
        assert self.__scaling_type == "widget"
        if isinstance(value, float):
            return value * self.__widget_scaling
        else:
            return int(value * self.__widget_scaling)

def _reverse_widget_scaling(self, value: Union[int, float]) -> Union[float, int]:
    assert self.__scaling_type == "widget"
    if isinstance(value, float):
        return value / self.__widget_scaling
    else:
        return int(value / self.__widget_scaling)
```

The similar edits from float to integer might be required for the CTkMessagebox's source code.

## Examples

Raw Insta360 footage includes six pairs of **.mp4** files, **preview.mp4** and **pro.prj** file. GPS spatial data should be extracted from **origin_6_lrv.mp4** (hence **origin_6_lrv.mp4** is used as the default file name in App's settings.json file.

![Insta360 Raw Data](https://github.com/user-attachments/assets/e0f38ffe-de75-4e4e-ab90-d14bba0895c5)

A couple of examples for both point and linestring geometry data extracted with the App to the Postgres Spatial Database are shown in the figures below.

![Point Geometry Sample](https://github.com/user-attachments/assets/9a3ec559-f891-43dd-ace7-9d306f4f9575)

![Linestring Geometry Sample](https://github.com/user-attachments/assets/066a80c5-31dd-488e-8e96-48ec470704a8)

Tabular form in the Database

![Point table](https://github.com/user-attachments/assets/26ed8c8f-e152-4aed-ab5e-69869ce9aada)

![Line table](https://github.com/user-attachments/assets/1a35fe48-2aaf-41c0-9ece-ec33b982a37b)

### Sample data

The sample dataset of four **origin_6_lrv.mp4** files can be downloaded [here](https://disk.yandex.ru/d/EfwWAOxp-kBSjw).

### IDE usage

App's usage vid IDE (CLI if needed) is based primarily on db_packer module from lib package.

The following example shows batch processing of several folders to the existing Database. Geometry type is set to both
points and lines.

``` python
# Importing db_packer module and pathlib
from lib.db_packer import DBPacker
from pathlib import Path

# Getting all subfolders with target videos
data_folder = 'D://SampleData'
subfolders = [fr"{f}".replace("\\", '/') for f\
                                in Path(data_folder).iterdir() if f.is_dir()]

"""Looping over folder's list and processing each to the
existing Database called tracks2024.
Geometry type is both points and lines.
Tables are track_points and track_lines accordingly.
No alias provided"""
for folder in subfolders:
    packer = DBPacker(video=folder)
    packer.pack_data(new=False,
                     db_name="tracks2024",
                     user="postgres",
                     credentials="password12345",
                     geometry="Both",
                     table_names=["track_points", "track_lines"])
```

Second exxample. Processing single video's data to the brand new Database.
``` python
# Importing db_packer module
from lib.db_packer import DBPacker

"""Processing a single video to the brand new Database.
Defining new Database's and table's names
Alias for the video provided"""
other_folder = "D://data_2023"
packer = DBPacker(video=other_folder)
packer.pack_data(new=True,
                 db_name="tracks2023",
                 user="postgres",
                 credentials="password12345",
                 geometry="Point",
                 table_names=["points2023"])
```

See respective module's documentation (dosctrings) for more details

### GUI

App includes a basic, simplistic GUI mode, launched from main.py. Since this App is not designed for bulk data processing, GUI is limited to 20 videos per session. This can be easily adjusted (if desired) by editing the threshold in the code and turning tkinter's Frames to scrollable (via either creating canvas with a scrollbar and a nested window or via the CTK's Scrollable frame widget).

Launching GUI brings up a login screen, as show on the figure below:

![Log in screen](https://github.com/user-attachments/assets/a98917fa-e924-4f5b-a1d1-dd94cea7f212)

Succesfull login bring up App's main screen (aka Processing screen). Processing screen is shown in the figure below:

![GUI](https://github.com/user-attachments/assets/3fe8f36e-be2d-462b-9b77-f8870e80c39c)

Left side of the window is dedicated to the input handling. Three buttons at the top left side control data input.

- _Add folder_ button allows to recursively/continuously add input folders for processing. One folder is added per time due to Explorer's dialogue window limitation. To increase the speed for adding multiple folders, the dialogue would constantly re-appear (straight to the last selected folder's path location) until being canceled via the Esc key press (or the dialogue's window close button). Selected folder's absolute path is filled to the generated tkinter entry widget. To the right of each path is an alias entry. Alias is used as data's readable identifier in the respective column. If no alias has been entered, the default value is used. Default value consist of prefix (defined in settings) followed by a video's creation datetime data formatted with underscores as separators. This can be easily changed (if desired) to any format of choice.
- _Add subfolders_ button allows to add all nested (first level, no recursion) subfolders from the chosen seed folder
- _Clear all_ button removes all entries

RMB click on the entry opens a context Menu with two options:
- **Browse folder** - opens up selected folder in Explorer
- **Remove entry** - deletes the selected entry

![Context menu](https://github.com/user-attachments/assets/35a36437-99ee-4c94-95fa-2e5c7097e4d9)

The right side of the window is dedicated to parameters control. From top to bottom, rows:
  
- Geometry selection row - three radio buttons which control the desired geometry type(s) - point, line or both.
- Database selection row. Includes two widgets. A new/existing Database switch enables/disables entry/combobox widgets to the right. If switch is on, a new Database is created (for to store processing results), the entry for the Database's name appears. Otherwise a combobox appears, with a list of all existing Databases to choose from. No capital letters allowed due to psycopg's nuances.
- Table(s) selection row. A set of two entries/comboboxes for target table's names per each type of geometry. Controlled by the switch, the logic is exactly the same as in the row above. 'On' for the new Database (i.e. tables) - entries are present. Otherwise the existing tables are used, comboboxes are present and are filled of a list of existing tables in the selected Database. No capital letters allowed due to psycopg's nuances.
 
The last two widgets are placed below the parameter controls:
- __Launch processing__ button - launches processing per se.
- __Output Console__. Displays informational messages. Scrollable, scrollbars are disabled (not active) by default. RMB click opens up a context Menu with a single option - for clearing all the Console's contents.

Upon setting up the desired parameters and pressing the launch button, parameters and input data are verified. A warning notification and/or informational message might pop in case of an issue with parameter/input values. Otherwise the data processing begins, followed by the informational messages to the console and a **Processing complete** notification with two options provided.

![Message](https://github.com/user-attachments/assets/ae7a200d-c871-4cd1-aca1-54a0e53337ce)

### Settings.json

Some basic App's settings are stored in __settings.json__ and can be easily modified if needed. Options include:

- __Default user__. Set to **postgres**
- __Default schema__. Set to **public**
- __Default table names__. Used as defaults for respective entries. **trackpoints** and **tracklines** by default
- __Altitude data type__. Integer by default, might be changed to float, but there's no practical reason to do so due to general GNSS data precision
- __Identifier field length__. 300 dy default
- __Coordinate precision__. 8 decimal places by default
- __Default prefix__. Set to **VID**. Also used as a placeholder's text for the aliases entry widget
- __Default directory__. Default directory's absolute path to initialize adding inputs via the Explorer's dialogue window
- __Default filename__. Set to **origin_6_lrv.mp4**
