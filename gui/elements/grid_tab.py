from tkinter import Frame, Variable, Label, Listbox, Scrollbar, Event, messagebox, Toplevel, IntVar, Checkbutton

from gui.elements.cell import CellElement
from gui.elements.list_control import ListControlButtons
from settings import SettingsManager


class GridTabWindow:
    """
    Class describing how the grid settings tab should look like.

    Attributes:
        master: Parent window.
        frame: Frame that will contain all elements.
        is_use_grid: Field indicating whether the grid will be used or not.
        use_grid_check: Checkbox that represents the state of the is_use_grid field.
        cells_var: Field representing the list of cell coordinates.
        cells_label: Label in front of listbox displaying grid cells.
        cells_listbox: Listbox that displays grid cells.
        cells_scrollbar: Scrollbar to scroll through the list of grid cells.
        list_control_button (ListControlButtons): Buttons that let manage the cells in the list.
    """

    def __init__(self, master, settings_manager: SettingsManager):
        """
        Construct a tab for viewing grid as cells list.

        Args:
            master: Parent window.
            settings_manager (SettingsManager): Instance of SettingsManager which contains the grid settings.
        """
        self.master = master
        self._settings_manager = settings_manager

        self.frame: Frame = Frame(master)
        self.frame.pack(fill="both", expand=True)

        self.frame.columnconfigure(0, weight=2)
        self.frame.columnconfigure(1, weight=1)

        self.is_use_grid: IntVar = IntVar()
        self.is_use_grid.set(self._settings_manager.settings.using_grid)
        self.use_grid_check: Checkbutton = Checkbutton(self.frame, text="Use grid?", variable=self.is_use_grid,
                                                       command=self.change_visible)
        self.use_grid_check.grid(column=0, row=0, padx=(5, 0), sticky="nw", pady=(5, 0))

        self.cells_var: Variable = Variable(value=list(map(lambda x: x.get_coords_str(), self._settings_manager.grid)))

        self.cells_label: Label = Label(self.frame, text="Cells list")
        self.cells_label.grid(column=0, row=1, sticky="nw", padx=(5, 0))

        self.cells_listbox: Listbox = Listbox(self.frame, listvariable=self.cells_var)
        self.cells_listbox.grid(column=0, row=2, sticky="nwse", columnspan=2, padx=(5, 0))

        self.cells_scrollbar: Scrollbar = Scrollbar(self.frame)
        self.cells_scrollbar.grid(column=2, row=2, sticky="ns")

        # connect listbox with scrollbar
        self.cells_listbox["yscrollcommand"] = self.cells_scrollbar.set
        self.cells_scrollbar.config(command=self.cells_listbox.yview)
        self.cells_listbox.bind("<Double-1>", self.edit_cell)

        self.list_control_button = ListControlButtons(self.frame, 5)
        self.list_control_button.frame_grid(column=3, row=2, sticky="nsew")

        # setup buttons
        self.list_control_button.configure_button(0, text="↑", command=self.up_cell)
        self.list_control_button.configure_button(1, text="↓", command=self.down_cell)
        self.list_control_button.configure_button(2, text="+", command=self.add_cell)
        self.list_control_button.configure_button(3, text="-", command=self.remove_cell)
        self.list_control_button.configure_button(4, text="Edit", command=self.edit_cell)

    def up_cell(self, event: Event = None):
        """
        Handler for button. Move cell up in priority.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        cur_selection = self.cells_listbox.curselection()
        if len(cur_selection) == 0:
            messagebox.showerror("Moving error", "Please select which item you want to move", parent=self.master)
        else:
            cell_idx = cur_selection[0]
            # Check that the cell is no already the first cell and there is a place to lift it to
            if cell_idx != 0 and len(self._settings_manager.grid) > 1:
                # swap cell id
                self._settings_manager.grid[cell_idx].id, self._settings_manager.grid[cell_idx - 1].id = \
                    self._settings_manager.grid[cell_idx - 1].id, self._settings_manager.grid[cell_idx].id

                # swap cell
                self._settings_manager.grid[cell_idx], self._settings_manager.grid[cell_idx - 1] = \
                    self._settings_manager.grid[cell_idx - 1], self._settings_manager.grid[cell_idx]

                self.cells_listbox.selection_clear(cell_idx)
                self.cells_listbox.selection_set(cell_idx - 1)
                self.update_cells_var()

    def down_cell(self, event: Event = None):
        """
        Handler for button. Move cell down in priority.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        cur_selection = self.cells_listbox.curselection()
        if len(cur_selection) == 0:
            messagebox.showerror("Moving error", "Please select which item you want to move", parent=self.master)
        else:
            cell_idx = cur_selection[0]
            # Check that the cell is no already the last cell and there is a place to lower it to
            if cell_idx != self.cells_listbox.size() - 1 and len(self._settings_manager.grid) > 1:
                # swap cell id
                self._settings_manager.grid[cell_idx].id, self._settings_manager.grid[cell_idx + 1].id = \
                    self._settings_manager.grid[cell_idx + 1].id, self._settings_manager.grid[cell_idx].id

                # swap cell
                self._settings_manager.grid[cell_idx], self._settings_manager.grid[cell_idx + 1] = \
                    self._settings_manager.grid[cell_idx + 1], self._settings_manager.grid[cell_idx]

                self.cells_listbox.selection_clear(cell_idx)
                self.cells_listbox.selection_set(cell_idx + 1)
                self.update_cells_var()

    def add_cell(self, event: Event = None):
        """
        Handler for button. If the cell attributes are saved, the cell will be added to the list.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        cell_window = self.get_cell_window()
        cell_element = CellElement(cell_window, self._settings_manager.grid, -1)

    def remove_cell(self, event: Event = None):
        """
        Handler for button. Removes a cell from the list.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        cur_selection = self.cells_listbox.curselection()
        if len(cur_selection) == 0:
            messagebox.showerror("Deleting error", "Please select which item you want to delete", parent=self.master)
        else:
            self.cells_listbox.delete(cur_selection)
            self._settings_manager.grid.pop(cur_selection[0])
            self.update_cells_var()

    def edit_cell(self, event: Event = None):
        """
        Handler for button. Editing a selected cell.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        cur_selection = self.cells_listbox.curselection()
        if len(cur_selection) == 0:
            messagebox.showerror("Editing error", "Please select which item you want to edit", parent=self.master)
        else:
            cell_idx = cur_selection[0]
            cell_window = self.get_cell_window()
            cell = self._settings_manager.grid[cell_idx]
            cell_element = CellElement(cell_window, self._settings_manager.grid, cell_idx)

    def get_cell_window(self, event: Event = None) -> Toplevel:
        """
        Creating a new window where the cell attributes will be placed.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.

        Returns:
            Window in which to place the elements.
        """
        cell_window = Toplevel(self.frame)
        cell_window.geometry("220x100")
        cell_window.resizable(0, 0)
        cell_window.title("View cell")
        cell_window.bind("<Destroy>", self.update_cells_var)
        return cell_window

    def update_cells_var(self, event: Event = None):
        """
        Updating the field responsible for representing the list of cell coordinates.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        self.cells_var.set(list(map(lambda x: x.get_coords_str(), self._settings_manager.grid)))

    def update_use_grid_var(self, event: Event = None):
        """
        Update the field responsible for whether the grid will be used or not

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        self.is_use_grid.set(self._settings_manager.settings.using_grid)
        self.change_visible(event)

    def change_visible(self, event: Event = None):
        """
        Changing the visibility of the cell list depending on the grid usage checkbox value.

        Args:
            event (:obj:`Event`, optional): The instance of Event which contains information about what action happened. Defaults to None.
        """
        if self.is_use_grid.get():
            self.cells_label.grid()
            self.cells_listbox.grid()
            self.cells_scrollbar.grid()
            self.list_control_button.frame_grid()
            self._settings_manager.settings.using_grid = True

        else:
            self.cells_label.grid_remove()
            self.cells_listbox.grid_remove()
            self.cells_scrollbar.grid_remove()
            self.list_control_button.button_frame.grid_remove()
            self._settings_manager.settings.using_grid = False
