"""
Processing screen module

Main module for the App's GUI mode
Controls all processing operations:
-Data input
-Parameters setup
-Processing launch

© 2024 Kirill Romashchenko
"""
import tkinter as tk
from tkinter import *
from PIL import ImageTk, Image
import ttkbootstrap as ttk
import customtkinter as ctk
from typing import Union
from qtd_to_postgis.lib.settings_reader import Reader
from qtd_to_postgis.lib.db_connector import DBConnector

class ProcessingScreen:
    def __init__(self, master, credentials: list) -> None:
        """Constructor method for the processing class
        :param master: parent/master tkinter widget
        :param credentials: (list) valid credentials entered via
        the log in screen. Should be hashed/stored in a more clever manner,
        but in this localhost-designed App it doesn't really matter"""
        self.master = master
        self.credentials = credentials
        self.dimensions = 800, 600

        self.settings = Reader().get_settings()
        self.default_alias =self.settings["Default prefix"]
        self.default_directory = self.settings["Default directory"]
        self.default_flename = self.settings["Default filename"]

        self.point_table_name = tk.StringVar(value=self.settings["Default table names"][0])
        self.line_table_name = tk.StringVar(value=self.settings["Default table names"][1])

        # Elements setup

        # Left side
        self.general_Frame = None  # Frames
        self.input_Frame = None
        self.parameters_Frame = None
        self.input_buttons_Frame = None
        self.entries_Frame = None

        self.add_folder_button = None  # Buttons
        self.add_subfolders_button = None
        self.clear_button = None

        self.input_folders = []
        self.entries_list = []
        self.alias_list = []
        self.input_limit = 20  # Maximum amount of entries

        # Right side
        self.geometry_Frame = None  # Frames
        self.database_Frame = None
        self.tables_Frame = None
        self.console_Frame = None

        self.point_radio_button = None  # Radio buttons
        self.line_radio_button = None
        self.both_radio_button = None

        self.geometry_type = tk.StringVar(value='Both')  # Database related
        self.new_database_yn = tk.StringVar(value='New')

        self.new_db_switch = None
        self.new_db_entry = None
        self.db_combo_box = None

        self.new_database_name = tk.StringVar()
        self.existing_db_name = tk.StringVar()

        self.point_table_combobox = None  # Table related
        self.line_table_combobox = None
        self.existing_point_table = tk.StringVar()
        self.existing_line_table = tk.StringVar()

        self.point_table_entry = None
        self.line_table_entry = None
        self.point_label = None
        self.line_label = None

        self.console_box = None  # Console
        self.launch_button = None

        self.all_aliasses = []  # Processing related
        self.packed_input = []

        self.main_Frame = self.setup_ui(master=self.master)  # Packing
        self.main_Frame.grid(row=0, column=0, sticky='nsew')

    def setup_ui(self, master):
        """Generates two main frames of the screen - input frame (left)
        and parameters frame (right)
        :param master: master tkinter widget"""
        self.general_Frame = ctk.CTkFrame(master=master,
                                          width=self.dimensions[0],
                                          height=self.dimensions[1],
                                          fg_color="#121212",
                                          corner_radius=0)
        self.input_Frame = ctk.CTkFrame(master=self.general_Frame,
                                        width=int(self.dimensions[0]/2),
                                        height=self.dimensions[1],
                                        fg_color="#121212",
                                        corner_radius=0)
        self.parameters_Frame = ctk.CTkFrame(master=self.general_Frame,
                                             width=int(self.dimensions[0]/2),
                                             height=self.dimensions[1],
                                             fg_color="#121212",
                                             corner_radius=0)
        self.input_buttons_Frame = ctk.CTkFrame(master=self.input_Frame,
                                                width=int(self.dimensions[0]/2),
                                                height=30,
                                                fg_color="#121212",
                                                corner_radius=0)
        self.input_buttons_Frame.grid_propagate(0)

        self.input_Frame.grid(row=0, column=0, sticky='nsew')
        self.parameters_Frame.grid(row=0, column=1, sticky='nsew')
        self.input_Frame.grid_propagate(0)
        self.parameters_Frame.grid_propagate(0)

        self.setup_input_frame()
        self.setup_parameters_frame()

        return self.general_Frame

    def setup_input_frame(self) -> None:
        """Sets upleft (input) frame"""
        self.add_folder_button = ctk.CTkButton(self.input_buttons_Frame,
                                               text="Add folder(s)",
                                               font=('Corbel', 18),
                                               corner_radius=0,
                                               command=lambda: self.select_data(subfolders=False))
        self.add_folder_button.grid(row=0, column=0, sticky='ew', padx=2)
        self.add_subfolders_button = ctk.CTkButton(self.input_buttons_Frame,
                                                   text="Add subfolders",
                                                   font=('Corbel', 18),
                                                   corner_radius=0,
                                                   command=lambda: self.select_data(subfolders=True))
        self.add_subfolders_button.grid(row=0, column=1, sticky='ew', padx=17)

        clear_logo_path = './gui/assets/Delete.png'
        clear_logo = ctk.CTkImage(light_image=Image.open(clear_logo_path), size=(15, 15))
        self.clear_button = ctk.CTkButton(self.input_buttons_Frame,
                                          text="Clear All",
                                          corner_radius=0,
                                          image=clear_logo,
                                          width=85,
                                          command=lambda: self.clear_all(redraw=False))
        self.clear_button.grid(row=0, column=2, sticky='ew')

        self.input_buttons_Frame.grid(row=0, column=0, sticky='ew')

        # Entries
        self.entries_Frame = ctk.CTkFrame(master=self.input_Frame,
                                          width=int(self.dimensions[0] / 2),
                                          height=self.dimensions[1],
                                          fg_color="#121212",
                                          corner_radius=0)
        self.entries_Frame.grid(row=1, column=0, sticky='ew', padx=2)
        self.entries_Frame.grid_propagate(0)

    def setup_parameters_frame(self) -> None:
        """Sets up right (parameters) frame via the related methods"""
        self.setup_radio_buttons()
        self.setup_db_frame()
        self.setup_tables_frame()
        self.setup_console()

    def setup_radio_buttons(self) -> None:
        """Sets up geometry frame with radio buttons for geometry type(s)
        selection"""
        self.geometry_Frame = ctk.CTkFrame(master=self.parameters_Frame,
                                           width=self.dimensions[0],
                                           height=50,
                                           fg_color="#121212",
                                           corner_radius=0)
        self.geometry_Frame.grid_propagate(0)
        self.geometry_Frame.grid(row=0, column=0, sticky='new')

        self.point_radio_button = ctk.CTkRadioButton(self.geometry_Frame,
                                                     text="Point",
                                                     variable=self.geometry_type,
                                                     value="Point",
                                                     command=lambda: self.control_table_entries(),
                                                     corner_radius=0,
                                                     border_width_unchecked=2,
                                                     border_width_checked=4)
        self.line_radio_button = ctk.CTkRadioButton(self.geometry_Frame,
                                                    text="Line",
                                                    variable=self.geometry_type,
                                                    value="Line",
                                                    command=lambda: self.control_table_entries(),
                                                    corner_radius=0,
                                                    border_width_unchecked=2,
                                                    border_width_checked=4)
        self.both_radio_button = ctk.CTkRadioButton(self.geometry_Frame,
                                                    text="Point & Line",
                                                    variable=self.geometry_type,
                                                    value="Both",
                                                    command=lambda: self.control_table_entries(),
                                                    corner_radius=0,
                                                    border_width_unchecked=2,
                                                    border_width_checked=4)

        self.point_radio_button.grid(row=0, column=0, padx=25, pady=5)
        column = 1
        for button in [self.line_radio_button,
                       self.both_radio_button]:
            button.grid(row=0, column=column, padx=15, pady=5)
            column += 1

    def setup_db_frame(self) -> None:
        """Sets up database frame with widgets related to
        Database creation/selection"""
        self.database_Frame = ctk.CTkFrame(master=self.parameters_Frame,
                                           width=self.dimensions[0],
                                           height=40,
                                           fg_color="#121212",
                                           corner_radius=0)
        self.database_Frame.grid_propagate(0)
        self.new_db_switch = ctk.CTkSwitch(master=self.database_Frame,
                                           text="New Database",
                                           font=("Roboto", 14),
                                           variable=self.new_database_yn,
                                           onvalue="New",
                                           offvalue="Existing",
                                           width=100,
                                           height=25,
                                           border_width=60,
                                           switch_height=25,
                                           switch_width=50,
                                           corner_radius=3,
                                           button_color="#FFFFFF",
                                           command=lambda: self.control_db_selection())
        self.new_db_switch.grid(row=0, column=0, sticky='w', padx=15)

        self.new_db_entry = ctk.CTkEntry(master=self.database_Frame,
                                         width=150,
                                         placeholder_text=self.new_database_name.get(),
                                         textvariable=self.new_database_name)
        self.new_db_entry.insert(0, self.new_database_name.get())
        self.new_db_entry.grid(row=0, column=1, sticky='ew', padx=35)

        self.db_combo_box = ctk.CTkComboBox(master=self.database_Frame,
                                            variable=self.existing_db_name,
                                            corner_radius=0)

        self.database_Frame.grid(row=1, column=0, sticky='nsew')

    def setup_tables_frame(self) -> None:
        """Sets up tables frame with widgets related to table(s) selection"""
        self.tables_Frame = ctk.CTkFrame(master=self.parameters_Frame,
                                         width=self.dimensions[0],
                                         height=100,
                                         fg_color="#121212",
                                         corner_radius=0)
        self.tables_Frame.grid_propagate(0)

        self.point_table_entry = ctk.CTkEntry(master=self.tables_Frame,
                                              width=150,
                                              placeholder_text=self.point_table_name.get())
        self.point_table_entry.insert(0, self.point_table_name.get())
        self.line_table_entry = ctk.CTkEntry(master=self.tables_Frame,
                                             width=150,
                                             placeholder_text=self.line_table_name.get())
        self.line_table_entry.insert(0, self.line_table_name.get())

        self.point_table_combobox = ctk.CTkComboBox(master=self.tables_Frame,
                                                    variable=self.existing_point_table,
                                                    corner_radius=0)
        self.line_table_combobox = ctk.CTkComboBox(master=self.tables_Frame,
                                                   variable=self.existing_line_table,
                                                   corner_radius=0)
        self.point_label = ctk.CTkLabel(master=self.tables_Frame,
                                    text="Point table's name",
                                    font=("Roboto", 16),
                                    justify="center")
        self.line_label = ctk.CTkLabel(master=self.tables_Frame,
                                   text="Line table's name",
                                   font=("Roboto", 16),
                                   justify="center")
        self.tables_Frame.grid(row=2, column=0, sticky='nsew')

        self.point_table_entry.grid(row=0, column=0, padx=20, sticky='ew')
        self.line_table_entry.grid(row=0, column=1, padx=20, sticky='ew')

        self.point_label.grid(row=1, column=0, padx=20, pady=5, sticky='ew')
        self.line_label.grid(row=1, column=1, padx=20, pady=5, sticky='ew')

    def setup_console(self):
        """Sets up both informational console of the parameters frame and
        the launch button"""
        self.console_Frame = ctk.CTkFrame(master=self.parameters_Frame,
                                         width=self.dimensions[0],
                                         height=420,
                                         fg_color="#121212",
                                         corner_radius=0)
        self.launch_button = ctk.CTkButton(self.console_Frame,
                                               text="Launch processing",
                                               font=('Corbel', 18),
                                               fg_color="#f2b60f",
                                               text_color="#000000",
                                               corner_radius=0,
                                           command=lambda: self.launch_processing())
        self.console_box = ctk.CTkTextbox(master=self.console_Frame,
                                          width=(int(self.dimensions[0]/2)-2),
                                          height=382,
                                          corner_radius=0,
                                          fg_color="#21211f",
                                          font=("Roboto", 18),
                                          spacing2=4,
                                          wrap="word",
                                          activate_scrollbars=False)
        self.console_box.bind("<Button-3>",
                              command=lambda event: self.console_rmb_menu(event))
        self.launch_button.grid(row=0, column=0, padx=135, sticky='w')
        self.console_box.grid(row=1, column=0, sticky="sw")
        self.console_Frame.grid_propagate(0)
        self.console_Frame.grid(row=4, column=0, sticky='nsew')

    def select_data(self, subfolders: bool=False) -> None:
        """Recursve/continuous target folders selection
        (interrupted by cancel/escape)
        :param subfolders: (bool) flag indicating subfolders
        selection mode"""
        import os
        from pathlib import Path
        from customtkinter import filedialog

        def add_continuously(message: str, output: list,
                             initial_directory: str) -> list:
            """Continiously launches file dialog window"""
            directory_path = filedialog.askdirectory(initialdir=initial_directory,
                                                     title=message)

            if len(directory_path) > 0:
                output.append(directory_path)
                add_continuously('Select the next\
                 Directory/Cancel to end', output,
                                 os.path.dirname(directory_path))

            return output

        if subfolders:
            parent_folder = filedialog.askdirectory()
            selected_folders = [fr"{f}".replace("\\", '/') for f\
                                in Path(parent_folder).iterdir() if f.is_dir()]
            split_to_check = [f.rsplit('/', 1)[0] for f in selected_folders]
            inner_folders = ['gui', 'lib']
            comparison = [i for i, j in zip(split_to_check, inner_folders) if i == j]
            if comparison == inner_folders:
                return None
        else:
            selected_folders = []
            add_continuously(message='Select folder', output=selected_folders,
                             initial_directory=self.default_directory)

        tested_selection = [f for f in (set(selected_folders)) if f not in self.input_folders]
        if not tested_selection:
            return None

        input_count = len(self.input_folders)

        overflow_yn = bool((input_count + len(tested_selection)) > self.input_limit)
        free_slots = self.input_limit - input_count

        if overflow_yn:
            self.input_folders.extend(tested_selection[:free_slots])
            self.activate_buttons(to_state="off")
        elif not overflow_yn:
            self.input_folders.extend(tested_selection)

        self.add_entries()

        if len(self.input_folders) >= self.input_limit:
            self.activate_buttons(to_state="off")

    def add_entries(self) -> None:
        """Adds entrie(s) for the input folder(s)"""
        counter = 0
        self.alias_list.clear()
        for folder in self.input_folders:
            entry = ctk.CTkEntry(self.entries_Frame, corner_radius=0,
                                 width=int((self.dimensions[0] - 5) / 4))
            entry.insert(0, folder)
            entry.grid(row=counter, column=0, sticky='ew')
            entry.xview_moveto(1)
            self.entries_list.append(entry)
            entry.bind("<Button-3>", lambda event,
                                            target=entry: self.rmb_menu(event, target))

            alias_entry = ctk.CTkEntry(self.entries_Frame, corner_radius=0,
                                       width=int((self.dimensions[0] - 47) / 4))
            alias_entry.insert(0, self.default_alias)
            alias_entry.grid(row=counter, column=1, sticky='ew', padx=10)
            self.alias_list.append(alias_entry)
            counter += 1

    def remove_entry(self, target) -> None:
        """Removes a single entry
        :param target: target tkinter entry widget"""
        target_value = target.get()
        self.input_folders.remove(target_value)
        self.clear_all(redraw=True)
        self.add_entries()

        for button in [self.add_folder_button, self.add_subfolders_button]:
            if len(self.input_folders) < self.input_limit\
                    and button.cget('state') == "disabled":
                button.configure(state='active')

    def clear_all(self, redraw: bool=True) -> None:
        """Removes all entries/performs related clean-up logic
        :param redraw: (bool) flag indicating if method is used to
        either redraw entries or to completely remove them"""
        for child in self.entries_Frame.winfo_children():
            child.destroy()

        containers = [self.entries_list,
                      self.alias_list,
                      self.input_folders]
        if redraw:
            containers.remove(self.input_folders)

        for container in containers:
            container.clear()

        if not redraw:
            self.activate_buttons(to_state="on")

    def rmb_menu(self, event, target) -> None:
        """Logic behind entry's right mouse button context menu
        :param event: tkinter event object
        :param target: a target tkinter widget"""
        import os

        target_folder = target.get()

        rmb = ttk.Menu(self.general_Frame, tearoff=0)
        rmb.add_command(label="Browse folder",
                        command=lambda: os.startfile(target_folder))
        rmb.add_separator()
        rmb.add_command(label="Remove entry",
                        command=lambda: self.remove_entry(target))

        try:
            rmb.tk_popup(event.x_root, event.y_root, 0)
        finally:
            rmb.grab_release()

    def activate_buttons(self, to_state: str) -> None:
        """Enables/disables input control buttons"""
        for button in [self.add_folder_button,
                       self.add_subfolders_button]:
            if to_state == 'on':
                button.configure(state='active')
            elif to_state == "off":
                button.configure(state='disabled')

    def control_table_entries(self) -> None:
        """Controls logic behind entries and comboboxes for table's names"""
        if self.geometry_type.get() == "Both":
            for widget in [self.point_table_entry, self.point_table_combobox,
                           self.line_table_entry,  self.line_table_combobox]:
                widget.configure(state="normal")
        elif self.geometry_type.get() == "Point":
            for widget in [self.point_table_entry, self.point_table_combobox]:
                widget.configure(state="normal")
            for widget in [self.line_table_entry,  self.line_table_combobox]:
                widget.configure(state="disabled")
        elif self.geometry_type.get() == "Line":
            for widget in [self.point_table_entry, self.point_table_combobox]:
                widget.configure(state="disabled")
            for widget in [self.line_table_entry, self.line_table_combobox]:
                widget.configure(state="normal")

    def control_db_selection(self) -> None:
        """Controls logic behind displaying/hiding database related widgets"""
        if self.new_database_yn.get() == 'New':
            self.point_table_combobox.grid_forget()
            self.line_table_combobox.grid_forget()
            self.db_combo_box.grid_forget()

            self.new_db_entry.grid(row=0, column=1, sticky='ew', padx=35)
            self.point_table_entry.grid(row=0, column=0, padx=20, sticky='ew')
            self.line_table_entry.grid(row=0, column=1, padx=20, sticky='ew')
            self.control_table_entries()
        elif self.new_database_yn.get() == 'Existing':
            self.point_table_entry.configure(state="disabled")
            self.line_table_entry.configure(state="disabled")

            self.new_db_entry.grid_forget()
            self.db_combo_box.grid(row=0, column=1, sticky='ew', padx=35)
            connector_instance = DBConnector(db_name="postgres",
                                             user=self.credentials[0],
                                             credentials=self.credentials[1])
            exising_dbs = connector_instance.list_data(structure="databases")
            self.db_combo_box.configure(values=exising_dbs)

            connector_instance = DBConnector(db_name=self.existing_db_name.get(),
                                             user=self.credentials[0],
                                             credentials=self.credentials[1])
            tables = connector_instance.list_data(structure="tables")

            counter = 0
            for box in [self.point_table_combobox,
                        self.line_table_combobox]:
                box.grid(row=0, column=counter, padx=20, sticky='ew')
                box.configure(values=tables)
                counter += 1

            if self.geometry_type.get() == "Point":
                self.point_table_combobox.configure(state="normal")
            elif self.geometry_type.get() == "Line":
                self.line_table_combobox.configure(state="normal")
            elif self.geometry_type.get() == "Both":
                self.point_table_combobox.configure(state="normal")
                self.line_table_combobox.configure(state="normal")

    def validate_table(self) -> bool:
        """Verifies if table name(s) being properly filled
        :return (bool) flag indicating if table name(s) are
        filled properly"""
        entry_data = [self.point_table_entry.get(),
                      self.line_table_entry.get()]
        if self.geometry_type.get() == "Both" and "" in entry_data:
            return False
        elif self.geometry_type.get() == "Point" and entry_data[0] == "":
            return False
        elif self.geometry_type.get() == "Line" and entry_data[1] == "":
            return False
        else:
            return True

    def validate_columns(self) -> bool:
        """Verifies presence of the required columns in the existing
        Database table(s)
        Yep, I know this method is a mess and should be refactored
        :param (bool) a flag indicating if table's schemas match"""
        required_columns = {
            "Point": ['video', 'longitude', 'latitude', 'altitude', 'geom'],
            "Line": ['id', 'video', 'length', 'geom']
        }

        selected_db = self.existing_db_name.get()
        connector_instance = DBConnector(db_name=selected_db,
                                        user=self.credentials[0],
                                        credentials=self.credentials[1])
        if self.geometry_type.get() == "Point":
            table = self.point_table_combobox.get()
            columns_list = connector_instance.list_data(structure="columns", name=table)
            columns_to_match = required_columns["Point"]
            not_matched = [c for c in columns_to_match if c not in columns_list]
            if not_matched:
                self.to_console("Schemas don't match")
                return False
            else:
                self.to_console("Schemas match")
                return True
        elif self.geometry_type.get() == "Line":
            table = self.line_table_combobox.get()
            columns_list = connector_instance.list_data(structure="columns", name=table)
            columns_to_match = required_columns["Line"]
            not_matched = [c for c in columns_to_match if c not in columns_list]
            if not_matched:
                self.to_console("Schemas don't match")
                return False
            else:
                self.to_console("Schemas match")
                return True
        elif self.geometry_type.get() == "Both":
            point_table = self.point_table_combobox.get()
            line_table = self.line_table_combobox.get()

            point_columns_list = connector_instance.list_data(structure="columns",
                                                              name=point_table)
            line_columns_list = connector_instance.list_data(structure="columns",
                                                             name=line_table)

            point_columns_to_match = required_columns["Point"]
            poins_not_matched = [c for c in point_columns_to_match if c not in point_columns_list]

            line_columns_to_match = required_columns["Line"]
            line_not_matched = [c for c in line_columns_to_match if c not in line_columns_list]

            if poins_not_matched:
                self.to_console(f"Point table's schema doesn't match")
            if line_not_matched:
                self.to_console(f"Line table's schema doesn't match")
            if any([poins_not_matched, line_not_matched]):
                return False
            else:
                self.to_console('Schemas match')
                return True

    def launch_processing(self) -> None:
        """Launches processing and controls the related logic"""
        from lib.db_packer import DBPacker
        from CTkMessagebox import CTkMessagebox
        import sys

        if not self.input_folders:
            self.to_console('No input provided')
            return None

        if not self.validate_table():
            self.to_console('Tables are not filled properly')
            return None

        if not self.verify_input():
            return None

        self.all_aliasses = [e.get() for e in self.alias_list]
        checked_aliases = []
        for alias in self.all_aliasses:
            if alias != self.default_alias:
                checked_aliases.append(alias)
            else:
                checked_aliases.append(None)
        output = list(zip(self.input_folders, checked_aliases))

        if self.new_database_yn.get() == 'New':
            new_db = True
            target_db = self.new_db_entry.get()
            target_tables = [self.point_table_entry.get(),
                             self.line_table_entry.get()]
        elif self.new_database_yn.get() == 'Existing':
            schema_check = self.validate_columns()
            if not schema_check:
                return None
            new_db = False
            target_db = self.existing_db_name.get()
            target_tables = [self.point_table_combobox.get(),
                             self.line_table_combobox.get()]

        def console_messages(message: Union[str, tuple]) -> None:
            """Prints informational message(s) to console,
            followed by the separator
            :param message: a string (or a tuple of strings) with
            informational message(s)"""
            self.to_console('Data extracted')
            if self.geometry_type.get() == 'Both' or new_db or \
                    (self.geometry_type.get() == 'Both' and new_db):
                for statement in message:
                    if type(statement) != tuple:
                        self.to_console(statement)
                    else:
                        for substatement in statement:
                            self.to_console(substatement)
            else:
                self.to_console(message)

            self.to_console(separator=True, message='')

        output_count = len(output)
        if output_count < 2:
            for video in output:
                packer_instance = DBPacker(video=video[0])
                message = packer_instance.pack_data(new=new_db,
                                         db_name=target_db,
                                         user=self.credentials[0],
                                         credentials=self.credentials[1],
                                         table_names=target_tables,
                                         alias=video[1],
                                         to_console=True,
                                         verbose=False,
                                         geometry=self.geometry_type.get())
                console_messages(message=message)
        elif output_count >= 2 and self.new_database_yn.get() == "New":
            initial_folder = output[0]
            packer_instance = DBPacker(video=initial_folder[0])
            message = packer_instance.pack_data(new=True,
                                                db_name=target_db,
                                                user=self.credentials[0],
                                                credentials=self.credentials[1],
                                                alias=initial_folder[1],
                                                table_names=target_tables,
                                                to_console=True,
                                                verbose=False,
                                                geometry=self.geometry_type.get())
            console_messages(message=message)

            for video in output[1:]:
                packer_instance = DBPacker(video=video[0])
                message = packer_instance.pack_data(new=False,
                                                    db_name=target_db,
                                                    user=self.credentials[0],
                                                    credentials=self.credentials[1],
                                                    table_names=target_tables,
                                                    alias=video[1],
                                                    to_console=True,
                                                    verbose=False,
                                                    geometry=self.geometry_type.get())
                console_messages(message=message)

        message_box = CTkMessagebox(message="Processing complete",
                                icon="check",
                                option_1="Close the app",
                                option_2="Continue processing",
                                justify="center",
                                title="Processing complete")
        response = message_box.get()
        if response == 'Close the app':
            sys.exit(0)
        elif response == 'Continue processing':
            message_box.destroy()

    def verify_input(self) -> bool:
        """Verifies input folders in terms of containing target videos
        (default is set to "origin_6_lrv.mp4" in the settings).
        Raises warning message (as notification and as text to console)
        if needed, removes incorrect input.
        :return (bool) flag indicating if all input folders are valid"""
        import os
        from CTkMessagebox import CTkMessagebox

        display_warning = False
        wrong_paths = []
        for folder in self.input_folders:
            contents = os.listdir(folder)
            if self.default_flename not in contents:
                display_warning = True
                wrong_paths.append(folder)
                self.to_console(f"{folder} does not contain target\
                 video files")

        if display_warning:
            waring_message = CTkMessagebox(message="Incorrect input",
                                    icon="warning",
                                    option_1="OK",
                                    justify="center",
                                    title="Incorrect input")
            response = waring_message.get()
            if response == 'OK':
                waring_message.destroy()

            for entry in self.entries_list:
                if entry.get() in wrong_paths:
                    self.remove_entry(target=entry)
            return False
        else:
            return True

    def to_console(self, message: str, separator: bool=False) -> None:
        """Prints formatted message to the processing screen's console
        :param message: (str) message's text
        :param separator: (bool) flag indicating that only the separator
        should be printed out. False by default"""
        if separator:
            self.console_box.insert('end', f"{'_'*30}\n")
        else:
            self.console_box.insert('end', f"·{message}\n")
        self.console_box.see(tk.END)

    def console_rmb_menu(self, event) -> None:
        """Controls logic behind console's right mouse button context menu
        :param event: tkinter event object"""
        rmb = ttk.Menu(self.console_Frame, tearoff=0)
        rmb.add_command(label="Clear console",
                        command=lambda: self.clear_console())

        try:
            rmb.tk_popup(event.x_root, event.y_root, 0)
        finally:
            rmb.grab_release()

    def clear_console(self) -> None:
        """Deletes all console's content"""
        self.console_box.delete('1.0', 'end')

