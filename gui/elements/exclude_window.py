from tkinter import Label, Entry, Event
from typing import List

from gui.elements.editing_control import HorizontalButtons
from settings import ExcludeWindow


class ExcludeWindowElement:
    """
    Class that describes how the exclude window editing element should look like.

    Attributes:
        master: Parent window.
        exclude_windows_list (List[ExcludeWindow]): List of all exclude windows.
        exclude_window_idx (int): Index of the exclude window to be viewed.
        exclude_window (ExcludeWindow): Current open exclude window.
        window_name_label: Label in front of the field for entering name of excluded window.
        window_name_entry: Field for entering the name of excluded window.
        editing_control_buttons (HorizontalButtons): Buttons to control the editing process.
    """

    def __init__(self, master, exclude_windows_list: List[ExcludeWindow], exclude_window_idx: int):
        """
        Construct a window for viewing exclude window attributes.

        Args:
            master: Parent window.
            exclude_windows_list (List[ExcludeWindow]): List of all exclude window.
            exclude_window_idx (int): Index of the exclude window to be viewed.
        """
        self.master = master
        self.exclude_windows_list = exclude_windows_list
        self.exclude_window_idx = exclude_window_idx
        self.exclude_window = ExcludeWindow()

        if exclude_window_idx >= 0:
            self.exclude_window = self.exclude_windows_list[self.exclude_window_idx]

        self.window_name_label: Label = Label(master, text="Window name")
        self.window_name_label.grid(column=0, row=0, sticky="nw", padx=(5, 0))

        self.window_name_entry: Entry = Entry(master, width=30)
        self.window_name_entry.insert(0, self.exclude_window.name)
        self.window_name_entry.grid(column=0, row=1, padx=(5, 0))

        self.editing_control_buttons = HorizontalButtons(master, 2)
        self.editing_control_buttons.frame_grid(column=0, row=2, sticky="nswe", pady=(10, 0), padx=(5, 0))

        self.editing_control_buttons.configure_button(0, text="Save", command=self.save_exclude_window)
        self.editing_control_buttons.configure_button(1, text="Exit", command=self.exit)

    def save_exclude_window(self, event: Event = None):
        """
        Saving values from interface fields to ExcludeWindow instance fields.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        if self.exclude_window_idx >= 0:
            exclude_window = self.exclude_windows_list[self.exclude_window_idx]
            exclude_window.name = self.window_name_entry.get()
        else:
            exclude_window_name = self.window_name_entry.get()
            exclude_window = ExcludeWindow(name=exclude_window_name)
            self.exclude_windows_list.append(exclude_window)
        self.exit()

    def exit(self, event: Event = None):
        """
        Closing the master window.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        self.master.destroy()
        self.master.update()
