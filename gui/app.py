"""
App class module
Contains logic behind Application's window and its core settings

© 2024 Kirill Romashchenko
"""
import tkinter as tk
import customtkinter as ctk
from gui.log_in_screen import LogInScreen
from qtd_to_postgis.lib.settings_reader import Reader

class App(ctk.CTk):
    def __init__(self, dimensions: tuple=(800, 600)):
        """App class constructor method.
        :param dimensions: (tuple) width and height (in pixels)
        of the App's window"""
        super().__init__()
        self.dimensions = dimensions
        self.geometry(f"{dimensions[0]}x{dimensions[1]}")
        self.title('QuickTime Data to PostGIS')
        self.configure(fg_color="#121212")
        self.resizable(0, 0)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.settings = Reader().get_settings()
        self.default_username = tk.StringVar(value=self.settings["Default user"])
        self.default_credentials = tk.StringVar()

        self.initial_screen = LogInScreen(master=self)

