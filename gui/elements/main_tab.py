from tkinter import Frame, Variable, Label, Listbox, Scrollbar, Event, messagebox, Toplevel
from typing import Callable, List

from daemon import processing_start
from gui.elements.editing_control import HorizontalButtons
from gui.elements.list_control import ListControlButtons
from gui.elements.window_attributes import WindowAttributesElement
from settings import SettingsManager


class MainTabWindow:
    """
    Class describing how the main settings tab should look like.

    Attributes:
        master: Parent window.
        frame: Frame that will contain all elements.
        is_processing: Field indicating whether window processing is running or not.
        windows_attributes_var: Field representing a list of the process name for each window attributes.
        start_stop_buttons: Buttons that can be used to start or stop window processing.
        windows_attributes_label: Label in front of listbox displaying windows attributes.
        windows_attributes_listbox: Listbox that displays windows attributes.
        windows_attributes_scrollbar: Scrollbar to scroll through the list of windows attributes.
        list_control_button (ListControlButtons): Buttons that let manage the windows attributes in the list.
    """

    def __init__(self, master, settings_manager: SettingsManager):
        """
        Construct a tab for viewing window attributes list.

        Args:
            master: Parent window.
            settings_manager (SettingsManager): Instance of SettingsManager which contains the main settings.
        """
        self.master = master
        self._settings_manager = settings_manager
        self.is_processing: bool = False
        self._start_handle_list: List[Callable] = []
        """List[Callable]: List containing callable objects that will be called before window processing"""
        self._stop_handle_list: List[Callable] = []
        """List[Callable]: List containing callable objects that will be called after window processing"""

        self.frame: Frame = Frame(master)
        self.frame.pack(fill="both", expand=True)

        self.frame.columnconfigure(0, weight=2)
        self.frame.columnconfigure(1, weight=1)

        self.windows_attributes_var: Variable = Variable(
            value=list(map(lambda x: x.process_name, self._settings_manager.windows_attributes)))

        self.start_stop_buttons = HorizontalButtons(self.frame, 2)
        self.start_stop_buttons.frame_grid(column=0, row=0, sticky="nw", pady=10, padx=(5, 0))
        self.start_stop_buttons.configure_button(0, text="Start processing", command=self.start_processing)
        self.start_stop_buttons.configure_button(1, text="Stop processing", command=self.stop_processing)

        self.windows_attributes_label: Label = Label(self.frame, text="Process list")
        self.windows_attributes_label.grid(column=0, row=1, sticky="nw", padx=(5, 0))

        self.windows_attributes_listbox: Listbox = Listbox(self.frame, listvariable=self.windows_attributes_var)
        self.windows_attributes_listbox.grid(column=0, row=2, sticky="nwse", columnspan=2, padx=(5, 0))

        self.windows_attributes_scrollbar: Scrollbar = Scrollbar(self.frame)
        self.windows_attributes_scrollbar.grid(column=2, row=2, sticky="ns")

        # connect listbox with scrollbar
        self.windows_attributes_listbox["yscrollcommand"] = self.windows_attributes_scrollbar.set
        self.windows_attributes_scrollbar.config(command=self.windows_attributes_listbox.yview)
        self.windows_attributes_listbox.bind("<Double-1>", self.edit_window_attributes)

        self.list_control_button = ListControlButtons(self.frame, 3)
        self.list_control_button.frame_grid(column=3, row=2, sticky="nsew")

        # setup buttons
        self.list_control_button.configure_button(0, text="+", command=self.add_window_attributes)
        self.list_control_button.configure_button(1, text="-", command=self.remove_window_attributes)
        self.list_control_button.configure_button(2, text="Edit", command=self.edit_window_attributes)

        self.enable_controls()

    def start_processing(self, event: Event = None):
        """
        Handler for button. Start processing windows.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        self.is_processing = True
        self.disable_controls()
        self._process_start_handles()
        self._settings_manager.is_running = True
        processing_start(self._settings_manager)

    def stop_processing(self, event: Event = None):
        """
        Handler for button. Stop processing windows.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        self._settings_manager.is_running = False
        self.is_processing = False
        self.enable_controls()
        self._process_stop_handles()

    def add_window_attributes(self, event: Event = None):
        """
        Handler for button. If the window attributes are saved, the window attributes will be added to the list.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        window_attributes_edit = self.get_window_attributes_element()
        exclude_window_element = WindowAttributesElement(window_attributes_edit,
                                                         self._settings_manager.windows_attributes, -1)

    def remove_window_attributes(self, event: Event = None):
        """
        Handler for button. Removes a window attributes from the list.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        cur_selection = self.windows_attributes_listbox.curselection()
        if len(cur_selection) == 0:
            messagebox.showerror("Deleting error", "Please select which item you want to delete", parent=self.master)
        else:
            self.windows_attributes_listbox.delete(cur_selection)
            self._settings_manager.windows_attributes.pop(cur_selection[0])
            self.update_windows_attributes_var()

    def edit_window_attributes(self, event: Event = None):
        """
        Handler for button. Editing a selected window attributes.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        cur_selection = self.windows_attributes_listbox.curselection()
        if len(cur_selection) == 0:
            messagebox.showerror("Editing error", "Please select which item you want to edit", parent=self.master)
        # editing is possible if window processing is not started
        elif not self.is_processing:
            window_attributes_idx = cur_selection[0]
            window_attributes_edit = self.get_window_attributes_element()
            window_attributes = self._settings_manager.windows_attributes[window_attributes_idx]
            window_attributes_element = WindowAttributesElement(window_attributes_edit,
                                                                self._settings_manager.windows_attributes,
                                                                window_attributes_idx)

    def get_window_attributes_element(self, event: Event = None) -> Toplevel:
        """
        Creating a new window where the window attributes will be placed.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.

        Returns:
            Window in which to place the elements.
        """
        window_attributes_element = Toplevel(self.frame)
        window_attributes_element.geometry("330x460")
        window_attributes_element.resizable(0, 0)
        window_attributes_element.title("View window attributes")
        window_attributes_element.bind("<Destroy>", self.update_windows_attributes_var)
        return window_attributes_element

    def update_windows_attributes_var(self, event: Event = None):
        """
        Updating the field responsible for representing the list of process name for each window attributes.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        self.windows_attributes_var.set(list(map(lambda x: x.process_name, self._settings_manager.windows_attributes)))

    def disable_controls(self):
        """Disables user interaction with specified buttons."""
        self.list_control_button.disable()
        self.start_stop_buttons.configure_button(0, state="disabled")
        self.start_stop_buttons.configure_button(1, state="normal")

    def enable_controls(self):
        """Enables user interaction with specified buttons."""
        self.list_control_button.enable()
        self.start_stop_buttons.configure_button(0, state="normal")
        self.start_stop_buttons.configure_button(1, state="disabled")

    def add_start_handle(self, handle: Callable):
        """
        Add the object to be called to the list of objects to be called before window processing.

        Args:
            handle (Callable): Instance that will be added to the list
        """
        self._start_handle_list.append(handle)

    def add_stop_handle(self, handle: Callable):
        """
        Add the object to be called to the list of objects to be called after window processing.

        Args:
            handle (Callable): Instance that will be added to the list
        """
        self._stop_handle_list.append(handle)

    def _process_start_handles(self):
        """Calling all callable objects that are in the list to be called before starting window processing"""
        for handle in self._start_handle_list:
            handle()

    def _process_stop_handles(self):
        """Calling all callable objects that are in the list to be called after starting window processing"""
        for handle in self._stop_handle_list:
            handle()
