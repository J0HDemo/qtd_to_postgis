"""
Log in screen module

Contains logic for logging in to the Postgres

© 2024 Kirill Romashchenko
"""

import tkinter as tk
from tkinter import *
from PIL import Image
import customtkinter as ctk
from gui.processing_screen import ProcessingScreen

class LogInScreen:
    def __init__(self, master) -> None:
        """Constructor method for the Log in screen/frame
        :param master: a master tkinter widget"""
        self.master = master
        self.dimensions = 800, 600

        # Elements setup
        self.entry_Frame = None  # Entries
        self.credentials_Frame = None

        self.user_entry = None  # Core widgets
        self.credentials_entry = None
        self.confirm_button = None

        self.visible_icon = None
        self.invisible_icon = None
        self.visibility_label = None

        self.enetered_username = tk.StringVar()
        self.entered_password = tk.StringVar()

        self.error_frame = None  # Error-related widgets
        self.error_icon = None
        self.error_message_label = None
        self.error_icon_label = None

        self.expanded = False  # Initial flags of state
        self.visible = False

        self.frame_width = 200  # Paddings and dimensions

        self.entry_height = 40
        self.entry_padding_x = 10
        self.entry_padding_y = 10
        self.entry_padding_top = 10
        self.entry_width = self.frame_width - self.entry_padding_x * 2

        self.error_icon_size = 30, 30
        self.visible_icon_size = 25, 25

        self.frame_height_default = (self.entry_height * 2 + self.entry_padding_y +
                                     self.entry_padding_top + 50)
        self.frame_height_expanded = self.frame_height_default + 50

        # Packing
        self.login_Frame = self.add_frame(master=self.master)
        self.login_Frame.grid(row=0, column=0, sticky='nsew')

        self.credentials_entry.bind("<Return>",
                                    lambda e: self.verify_credentials())

    def add_frame(self, master) -> ctk.CTkFrame:
        """Generates entry form's frame
        :param master: a master tkinter widget"""
        offset_x = int((self.dimensions[0] - (self.dimensions[0] / 2 -
                                              self.frame_width -
                                              (self.entry_padding_x * 2))) / 2)
        offset_y = int((self.dimensions[1] - self.frame_height_default) / 2)

        # General frame
        self.entry_Frame = ctk.CTkFrame(master=master, width=self.frame_width,
                                        height=self.frame_height_default,
                                        fg_color="#edf5f6", corner_radius=10)

        # Entries
        self.user_entry = ctk.CTkEntry(master=self.entry_Frame,
                                       textvariable=self.enetered_username)
        self.user_entry.insert(0, self.master.default_username.get())
        self.credentials_entry = ctk.CTkEntry(master=self.entry_Frame,
                                              textvariable=self.entered_password)
        self.credentials_entry.configure(show='*')

        for entry in [self.user_entry, self.credentials_entry]:
            entry.configure(width=self.entry_width,
                            height=self.entry_height,
                            justify="center",
                            font=('Corbel', 16))

        self.user_entry.grid(row=0, column=0, padx=self.entry_padding_x,
                             pady=self.entry_padding_top)
        self.credentials_entry.grid(row=1, column=0, padx=self.entry_padding_x)

        self.entry_Frame.grid(row=0, column=0, padx=offset_x, pady=offset_y)
        self.entry_Frame.grid_propagate(0)

        # Log in button
        self.credentials_Frame = ctk.CTkFrame(master=self.entry_Frame,
                                              width=self.frame_width,
                                              height=50,
                                              fg_color="#edf5f6")
        self.confirm_button = ctk.CTkButton(self.credentials_Frame,
                                            text="Log in",
                                            font=('Corbel', 18))
        self.confirm_button.configure(command=lambda: self.verify_credentials())

        # Visibility icon/tkinter label
        visible_icon_path = './gui/assets/Visible.png'
        self.visible_icon = ctk.CTkImage(light_image=Image.open(visible_icon_path),
                                         size=self.visible_icon_size)
        invisible_icon_path = './gui/assets/NotVisible.png'
        self.invisible_icon = ctk.CTkImage(light_image=Image.open(invisible_icon_path),
                                           size=self.visible_icon_size)

        self.visibility_label = ctk.CTkLabel(master=self.credentials_Frame)
        self.visibility_label.configure(image=self.visible_icon, text='')
        self.visibility_label.grid(row=0, column=0, sticky='w')
        self.visibility_label.bind("<Button-1>",
                                   lambda event: self.switch_visibility())
        self.confirm_button.grid(row=0, column=1, padx=10)
        self.credentials_Frame.grid(row=2, column=0, pady=10)

        return self.entry_Frame

    def verify_credentials(self) -> None:
        """Verifies connection to the Dataset with provided credentials"""
        from qtd_to_postgis.lib.db_connector import DBConnector

        postgres_connection = DBConnector(db_name="postgres",
                                          user=self.user_entry.get(),
                                          credentials=self.credentials_entry.get()).connect()
        if postgres_connection:
            self.enter_processing(credentials=[self.user_entry.get(),
                                                 self.credentials_entry.get()])
        else:
            self.master.expanded = True
            self.entry_Frame.configure(height=self.frame_height_expanded)
            self.display_error()
            self.master.after(1200, self.shrink)

    def display_error(self) -> None:
        """Displays an error message for the wrong credentials"""
        self.error_frame = ctk.CTkFrame(master=self.entry_Frame,
                                        width=self.frame_width,
                                        height=50,
                                        fg_color="#edf5f6",
                                        corner_radius=10)
        self.error_frame.grid_propagate(0)
        self.error_icon_label = ctk.CTkLabel(self.error_frame,
                                             fg_color="#edf5f6",
                                             width=30,
                                             height=30)
        error_icon_path = './gui./assets/Error.png'
        self.error_icon = ctk.CTkImage(light_image=Image.open(error_icon_path),
                                       size=self.error_icon_size)
        self.error_icon_label.configure(image=self.error_icon, text='')
        self.error_icon_label.grid(row=0, column=0, padx=7, pady=5, sticky='ew')
        self.error_message_label = ctk.CTkLabel(self.error_frame,
                                                fg_color="#edf5f6",
                                                text='Wrong credentials',
                                                font=('Corbel', 18),
                                                text_color="#e81c0f")
        self.error_message_label.grid(row=0, column=1, padx=7, pady=5)
        self.error_frame.grid(row=3, column=0, pady=5, sticky='ew')

    def shrink(self) -> None:
        """Shrinks entry frame back to its original height"""
        self.entry_Frame.configure(height=self.frame_height_default)

    def switch_visibility(self) -> None:
        """Controls password's entry's text visibility"""
        current_text = self.credentials_entry.get()
        self.credentials_entry.delete(0, 'end')

        if self.visible:
            self.visible = False
            self.visibility_label.configure(image=self.visible_icon,
                                        text='')
            self.credentials_entry.configure(show='*')
        else:
            self.visible = True
            self.visibility_label.configure(image=self.invisible_icon,
                                            text='')
            self.credentials_entry.configure(show='')

        self.credentials_entry.insert(0, current_text)

    def enter_processing(self, credentials: list) -> None:
        """Switches App to the Processing screen state
        :param credentials: (list) a list of credentials, stored as strings"""
        self.master.ProcessingSceen = ProcessingScreen(master=self.master,
                                                       credentials=credentials)
