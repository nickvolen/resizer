from tkinter import Frame, Button
from typing import List


class ListControlButtons:
    """
    Class that provides the ability to create a specified number of buttons to control listbox items.

    Attributes:
        button_frame: Frame in which the buttons are located.
    """

    def __init__(self, master, count: int):
        """
        Construct a frame with a specified number of buttons.

        Args:
            master: Parent window.
            count (int): Needed number of buttons.
        Raise:
            ValueError: If number of buttons to be passed is a negative number.
        """
        if count <= 0:
            raise ValueError("Number of buttons must be a positive number.")
        self.button_frame: Frame = Frame(master)
        self._count = count
        self._button_list: List[Button] = []
        """list: List of all created buttons"""

        # setup buttons
        for i in range(count):
            self._button_list.append(Button(self.button_frame))
            self._button_list[i].grid(column=0, row=i, sticky="nwe", pady=(5, 0))

        self._button_list[0].grid(column=0, row=0, sticky="nwe", pady=0)

    def frame_grid(self, **kwargs):
        """
        Lets to pass parameters to the function that controls the grid setting for the main frame.

        Args:
            **kwargs: Arbitrary keyword arguments.
        """
        self.button_frame.grid(**kwargs)

    def configure_button(self, idx, **kwargs):
        """
        Lets to pass parameters to the function that configures the specified button.

        Args:
            idx (int): number of the button to be configured.
            **kwargs: Arbitrary keyword arguments.
        """
        self._button_list[idx].configure(**kwargs)

    def disable(self):
        """Disables user interaction with all buttons."""
        for button in self._button_list:
            button.configure(state="disabled")

    def enable(self):
        """Enables user interaction with all buttons."""
        for button in self._button_list:
            button.configure(state="normal")
