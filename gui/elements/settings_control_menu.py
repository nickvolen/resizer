from tkinter import Menu, filedialog, messagebox
from typing import Callable, List

from settings import SettingsManager, Settings, get_settings, save_settings


class SettingsControlMenu:
    """Class describing how the settings dropdown menu should look like."""

    def __init__(self, master, init_settings: SettingsManager):
        """
        Construct a settings control menu.

        Args:
            master: Parent window.
            init_settings (SettingsManager): Initial instance of SettingsManager which contains the settings.
        """
        self.master = master
        self.settings_manager = init_settings
        self._handle_list: List[Callable] = []
        """List[Callable]: List containing callable objects that will be called after a settings update."""
        self.file_menu = Menu(master, tearoff=0)
        self.file_menu.add_command(label="New", command=self.new_settings)
        self.file_menu.add_command(label="Open", command=self.open_settings)
        self.file_menu.add_command(label="Save", command=self.save_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.exit)

    def new_settings(self):
        """Menu option handler. Resets settings."""
        self.settings_manager.reconfigure(Settings())
        self._reload_settings()

    def open_settings(self):
        """Menu option handler. Opens a dialog box for selecting a settings file to load."""
        file_types = (("Setting files (*.yaml)", "*.yaml"), ("all files", "*"))
        file_selected = filedialog.askopenfilename(
            title="Select file for open", initialdir=".", filetypes=file_types
        )
        if file_selected != "":
            settings = get_settings(file_selected)
            if settings is None:
                messagebox.showerror("Settings error",
                                     "Error reading the selected settings file. Please try again with a different file",
                                     parent=self.master)
            else:
                self.settings_manager.reconfigure(settings)
                self._reload_settings()

    def save_settings(self):
        """Menu option handler. Opens a file selection dialog box for saving the current settings."""
        file_types = (("Setting files (.yaml)", ".yaml"), ("all files", ".*"))
        file_selected = filedialog.asksaveasfilename(
            title="Select file for save", initialdir=".", filetypes=file_types, defaultextension=".yaml",
            initialfile="settings.yaml"
        )
        if file_selected != "":
            save_settings(self.settings_manager.settings, file_selected)

    def exit(self):
        """Menu option handler. Closing the root window."""
        self.master.master.destroy()

    def add_handle(self, handle: Callable):
        """
        Add the object to be called to the list of objects to be called after a settings update.

        Args:
            handle (Callable): Instance that will be added to the list
        """
        self._handle_list.append(handle)

    def _reload_settings(self):
        """Calling all callable objects that are in the list to be called after a settings update"""
        for handle in self._handle_list:
            handle()

    def disable(self):
        """Disables user interaction with specified menu items."""
        self.file_menu.entryconfig("New", state="disabled")
        self.file_menu.entryconfig("Open", state="disabled")
        self.file_menu.entryconfig("Exit", state="disabled")

    def enable(self):
        """Enables user interaction with specified menu items."""
        self.file_menu.entryconfig("New", state="normal")
        self.file_menu.entryconfig("Open", state="normal")
        self.file_menu.entryconfig("Exit", state="normal")
