from tkinter import Label, Entry, Event
from typing import List

from gui.elements.editing_control import HorizontalButtons
from gui.validators import is_positive_number
from settings import Cell


class CellElement:
    """
    Class that describes how the cell editing window should look like.

    Attributes:
        master: Parent window.
        cells_list (List[Cell]): List of all cells.
        cell_idx (int): Index of the cell to be viewed.
        cell (Cell): Current open cell.
        x_label: Label in front of the field for entering X coordinate.
        x_entry: Field for entering the X coordinate.
        y_label: Label in front of the field for entering Y coordinate.
        y_entry: Field for entering the Y coordinate.
        editing_control_buttons (HorizontalButtons): Buttons to control the editing process.
    """

    def __init__(self, master, cells_list: List[Cell], cell_idx: int):
        """
        Construct a window for viewing cell attributes.

        Args:
            master: Parent window.
            cells_list (List[Cell]): List of all cells.
            cell_idx (int): Index of the cell to be viewed.
        """
        self.master = master
        self.cells_list = cells_list
        self.cell_idx = cell_idx

        self._number_validator = self.master.register(is_positive_number)

        self.cell = Cell()
        if self.cell_idx >= 0:
            self.cell = self.cells_list[self.cell_idx]

        self.x_label: Label = Label(master, text="X")
        self.x_label.grid(column=0, row=0, sticky="nw", pady=(10, 0), padx=(5, 0))

        self.x_entry: Entry = Entry(master, width=15, validate="key", validatecommand=(self._number_validator, "%P"))
        self.x_entry.insert(0, str(self.cell.x))
        self.x_entry.grid(column=0, row=1, padx=(5, 0))

        self.y_label: Label = Label(master, text="Y")
        self.y_label.grid(column=1, row=0, sticky="nw", pady=(10, 0), padx=(15, 0))

        self.y_entry: Entry = Entry(master, width=15, validate="key", validatecommand=(self._number_validator, "%P"))
        self.y_entry.insert(0, str(self.cell.y))
        self.y_entry.grid(column=1, row=1, padx=(15, 0))

        self.editing_control_buttons = HorizontalButtons(master, 2)
        self.editing_control_buttons.frame_grid(column=0, row=2, sticky="nswe", pady=(10, 0), padx=(5, 0), columnspan=2)

        self.editing_control_buttons.configure_button(0, text="Save", command=self.save_cell)
        self.editing_control_buttons.configure_button(1, text="Exit", command=self.exit)

    def save_cell(self, event: Event = None):
        """
        Saving values from interface fields to Cell instance fields.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        self.cell.x = int(self.x_entry.get())
        self.cell.y = int(self.y_entry.get())

        if self.cell_idx < 0:
            if len(self.cells_list) > 0:
                self.cell.id = self.cells_list[-1].id + 1
            self.cells_list.append(self.cell)

        self.exit()

    def exit(self, event: Event = None):
        """
        Closing the master window.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        self.master.destroy()
        self.master.update()
