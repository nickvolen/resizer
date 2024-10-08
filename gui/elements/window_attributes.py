from tkinter import Label, Entry, IntVar, Checkbutton, Variable, Listbox, Scrollbar, messagebox, Event, Toplevel
from typing import List

from gui.elements.editing_control import HorizontalButtons
from gui.elements.exclude_window import ExcludeWindowElement
from gui.elements.list_control import ListControlButtons
from gui.validators import is_positive_number, get_number
from settings import WindowAttributes


class WindowAttributesElement:
    """
    Class that describes how the window attributes editing element should look like.

    Attributes:
        master: Parent window.
        windows_attributes_list (List[Cell]): List of all window attributes.
        windows_attributes_idx (int): Index of the window attributes to be viewed.
        window_attributes (WindowAttributes): Current open window attributes.
        process_name_label: Label in front of the field for entering process name.
        process_name_entry: Field for entering process name.
        width_label: Label in front of the field for entering window width.
        width_entry: Field for entering the window width.
        height_label: Label in front of the field for entering window height.
        height_entry: Field for entering the window height.
        x_label: Label in front of the field for entering X coordinate.
        x_entry: Field for entering the X coordinate.
        y_label: Label in front of the field for entering Y coordinate.
        y_entry: Field for entering the Y coordinate.
        is_use_coords: Field indicating whether to place the window at the specified coordinates.
        use_coords_label: Label in front of the checkbox that represents the state of the is_use_coords field.
        use_coords_check: Checkbox that represents the state of the is_use_coords field.
        exclude_windows_var: Field representing the list of exclude windows name for this window attributes.
        exclude_windows_label: Label in front of listbox displaying exclude windows name for this window attributes.
        exclude_windows_listbox: Listbox that displays exclude windows name for this window attributes.
        exclude_windows_listbox_scrollbar: Scrollbar to scroll through the list of exclude windows name for this window attributes.
        list_control_button (ListControlButtons): Buttons that let manage the exclude windows in the list for this window attributes.
        editing_control_buttons (HorizontalButtons): Buttons to control the editing process.
    """
    def __init__(self, master, windows_attributes_list: List[WindowAttributes], windows_attributes_idx: int):
        """
        Construct a window for viewing cell attributes.

        Args:
            master: Parent window.
            windows_attributes_list (List[WindowAttributes]): List of all window attributes.
            windows_attributes_idx (int): Index of the window attributes to be viewed.
        """
        self.master = master
        self.windows_attributes_list = windows_attributes_list
        self.windows_attributes_idx = windows_attributes_idx

        self._number_validator = self.master.register(is_positive_number)

        self.window_attributes = WindowAttributes()
        if self.windows_attributes_idx >= 0:
            self.window_attributes = self.windows_attributes_list[self.windows_attributes_idx]
        self.process_name_label: Label = Label(master, text="Process name")
        self.process_name_label.grid(column=0, row=0, sticky="nw", padx=(5, 0))

        self.process_name_entry: Entry = Entry(master)
        self.process_name_entry.insert(0, self.window_attributes.process_name)
        self.process_name_entry.grid(column=0, row=1, padx=(5, 0))

        self.width_label: Label = Label(master, text="Width")
        self.width_label.grid(column=0, row=2, sticky="nw", pady=(15, 0), padx=(5, 0))

        self.width_entry: Entry = Entry(master, validate="key", validatecommand=(self._number_validator, "%P"))
        self.width_entry.insert(0, str(self.window_attributes.width))
        self.width_entry.grid(column=0, row=3, padx=(5, 0))

        self.height_label: Label = Label(master, text="Height")
        self.height_label.grid(column=1, row=2, sticky="nw", pady=(15, 0), padx=(15, 0))

        self.height_entry: Entry = Entry(master, validate="key", validatecommand=(self._number_validator, "%P"))
        self.height_entry.insert(0, str(self.window_attributes.height))
        self.height_entry.grid(column=1, row=3, padx=(15, 0))

        self.x_label: Label = Label(master, text="X")
        self.x_label.grid(column=0, row=4, sticky="nw", pady=(15, 0), padx=(5, 0))

        self.x_entry: Entry = Entry(master, validate="key", validatecommand=(self._number_validator, "%P"))
        self.x_entry.insert(0, str(self.window_attributes.x))
        self.x_entry.grid(column=0, row=5, padx=(5, 0))

        self.y_label: Label = Label(master, text="Y")
        self.y_label.grid(column=1, row=4, sticky="nw", pady=(15, 0), padx=(15, 0))

        self.y_entry: Entry = Entry(master, validate="key", validatecommand=(self._number_validator, "%P"))
        self.y_entry.insert(0, str(self.window_attributes.y))
        self.y_entry.grid(column=1, row=5, padx=(15, 0))

        self.use_coords_label: Label = Label(master, text="Use coordinates?")
        self.use_coords_label.grid(column=0, row=6, sticky="nw", pady=(15, 0), padx=(5, 0))

        self.is_use_coords: IntVar = IntVar()
        self.is_use_coords.set(self.window_attributes.use_coordinates)
        self.use_coords_check = Checkbutton(master, text="Yes", variable=self.is_use_coords)
        self.use_coords_check.grid(column=0, row=7, padx=(5, 0), sticky="nw")

        self.exclude_windows_label = Label(master, text="Exclude windows")
        self.exclude_windows_label.grid(column=0, row=8, pady=(15, 0), padx=(5, 0), sticky="nw")

        if self.windows_attributes_idx >= 0:
            self.exclude_windows_var: Variable = Variable(
                value=list(map(lambda x: x.name, self.window_attributes.exclude_windows)))
        else:
            self.exclude_windows_var: Variable = Variable(value=[])

        self.exclude_windows_listbox: Listbox = Listbox(master, listvariable=self.exclude_windows_var)
        self.exclude_windows_listbox.grid(column=0, row=9, sticky="nwse", columnspan=2, padx=(5, 0))
        self.exclude_windows_listbox.bind("<Double-1>", self.edit_exclude_window)

        self.exclude_windows_listbox_scrollbar: Scrollbar = Scrollbar(master)
        self.exclude_windows_listbox_scrollbar.grid(column=2, row=9, sticky="ns")

        # connect listbox with scrollbar
        self.exclude_windows_listbox["yscrollcommand"] = self.exclude_windows_listbox_scrollbar.set
        self.exclude_windows_listbox_scrollbar.config(command=self.exclude_windows_listbox.yview)

        self.list_control_button = ListControlButtons(master, 3)
        self.list_control_button.frame_grid(column=3, row=9, sticky="nsew")

        # setup buttons
        self.list_control_button.configure_button(0, text="+", command=self.add_exclude_window)
        self.list_control_button.configure_button(1, text="-", command=self.remove_exclude_window)
        self.list_control_button.configure_button(2, text="Edit", command=self.edit_exclude_window)

        self.editing_control_buttons = HorizontalButtons(master, 2)
        self.editing_control_buttons.frame_grid(column=0, row=10, sticky="nswe", pady=(15, 0), padx=(5, 0),
                                                columnspan=4)

        self.editing_control_buttons.configure_button(0, text="Save", command=self.save_window_attributes)
        self.editing_control_buttons.configure_button(1, text="Exit", command=self.exit)

    def add_exclude_window(self, event: Event = None):
        """
        Handler for button. If the exclude window are saved, the exclude window will be added to the list.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        exclude_window_edit = self.get_exclude_window_element()
        exclude_window_element = ExcludeWindowElement(exclude_window_edit, self.window_attributes.exclude_windows, -1)

    def remove_exclude_window(self, event: Event = None):
        """
        Handler for button. Removes an exclude window from the list.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        cur_selection = self.exclude_windows_listbox.curselection()
        if len(cur_selection) == 0:
            messagebox.showerror("Deleting error", "Please select which item you want to delete", parent=self.master)
        else:
            self.exclude_windows_listbox.delete(cur_selection)
            self.window_attributes.exclude_windows.pop(cur_selection[0])
            self.update_exclude_window_var()

    def edit_exclude_window(self, event: Event = None):
        """
        Handler for button. Editing a selected exclude window.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        cur_selection = self.exclude_windows_listbox.curselection()
        if len(cur_selection) == 0:
            messagebox.showerror("Editing error", "Please select which item you want to edit", parent=self.master)
        else:
            exclude_window_idx = cur_selection[0]
            exclude_window_edit = self.get_exclude_window_element()
            exclude_window_element = ExcludeWindowElement(exclude_window_edit, self.window_attributes.exclude_windows,
                                                          exclude_window_idx)

    def update_exclude_window_var(self, event: Event = None):
        """
        Updating the field responsible for representing the list of window name for each exclude window.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        self.exclude_windows_var.set(list(map(lambda x: x.name, self.window_attributes.exclude_windows)))

    def get_exclude_window_element(self, event: Event = None) -> Toplevel:
        """
         Creating a new window where the exclude window attributes will be placed.

         Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.

         Returns:
             Window in which to place the elements.
         """
        exclude_window_element = Toplevel(self.master)
        exclude_window_element.geometry("200x80")
        exclude_window_element.resizable(0, 0)
        exclude_window_element.bind("<Destroy>", self.update_exclude_window_var)
        return exclude_window_element

    def save_window_attributes(self, event: Event = None):
        """
        Saving values from interface fields to WindowAttributes instance fields.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """

        # check that the process name ends with '.exe'.
        if not self.process_name_entry.get().endswith(".exe"):
            messagebox.showerror("Invalid process name",
                                 "Invalid process name.\nThe process name must end with '.exe'",
                                 parent=self.master)
            return

        self.window_attributes.process_name = self.process_name_entry.get()
        self.window_attributes.width = get_number(self.width_entry.get())
        self.window_attributes.height = get_number(self.height_entry.get())
        self.window_attributes.x = get_number(self.x_entry.get())
        self.window_attributes.y = get_number(self.y_entry.get())
        self.window_attributes.use_coordinates = bool(self.is_use_coords.get())

        if self.windows_attributes_idx < 0:
            self.windows_attributes_list.append(self.window_attributes)

        self.exit()

    def exit(self, event: Event = None):
        """
        Closing the master window.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        self.master.destroy()
        self.master.update()
