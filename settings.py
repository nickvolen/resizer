from multiprocessing import Value
from pathlib import Path
from typing import List, Dict, Optional, Union

import yaml
from pydantic import Field, RootModel
from pydantic.dataclasses import dataclass


class IndentDumper(yaml.Dumper):
    """Class to indent yaml dumps"""

    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)


@dataclass
class ExcludeWindow:
    """
    Class that describes the windows to be excluded from processing.

    Attributes:
        name (str): Window title.
    """
    name: str = Field("")


@dataclass
class WindowAttributes:
    """
    Class to describe how the window must be displayed

    Attributes:
        process_name (str): Name of the process to be processed.
        width (int): Window width.
        height (int): Window height.
        x (int): Window X coordinate on screen.
        y (int): Window Y coordinate on screen.
        use_coordinates (bool): Whether to display windows of the specified process name at the specified coordinates.
        exclude_windows (list): List of windows to be excluded from processing.
        additional_width (int): Additional width for accurate sizing.
        additional_height (int): Additional height for accurate sizing.
    """
    process_name: str = Field("")
    width: int = Field(0)
    height: int = Field(0)
    x: int = Field(0)
    y: int = Field(0)
    use_coordinates: bool = Field(False)
    exclude_windows: Union[List[Dict[str, ExcludeWindow]], List[ExcludeWindow]] = Field(default_factory=list)
    additional_width: int = Field(0, exclude=True)
    additional_height: int = Field(0, exclude=True)


@dataclass
class Cell:
    """
    Class for describing a grid cell.

    Attributes:
        id (int): Cell sequence number.
        x (int): Cell X coordinate on screen.
        y (int): Cell Y coordinate on screen.
        hwnd (int): Specifies the window handle to which this cell is owned.
    """
    id: int = Field(1)
    x: int = Field(0)
    y: int = Field(0)
    hwnd: int = Field(0, exclude=True)

    def __lt__(self, other: "Cell") -> bool:
        if self.x != other.x:
            return self.x < other.x
        else:
            return self.y < other.y

    def get_coords_str(self) -> str:
        """
        Return another string representation of Cell class.

        Returns:
            String representation of Cell class.
        """
        return f"x={self.x}, y={self.y}"


@dataclass
class Settings:
    """
    Class to describe settings.

    Attributes:
        windows_attributes (list): List of 'WindowAttributes' class.
        using_grid (bool): Whether to use a grid.
        grid (list): List of 'Cell' class.
    """
    windows_attributes: Union[List[Dict[str, WindowAttributes]], List[WindowAttributes]] = Field(default_factory=list)
    using_grid: bool = Field(False)
    grid: Union[List[Dict[str, Cell]], List[Cell]] = Field(default_factory=list)


def get_settings(path_str: str = "settings.yaml") -> Optional[Settings]:
    """
    Read settings file and return Settings instance.

    Args:
        path_str (str): Path to the settings file.
    Returns:
        The Settings instance if file reading was completed without errors, otherwise None
    """
    # if file don't exist - save default settings
    if not Path(path_str).exists():
        with open(path_str, "w") as f:
            settings = Settings()
            dump_of_model = RootModel[Settings](settings).model_dump(by_alias=True)
            yaml.dump(dump_of_model, f, Dumper=IndentDumper, sort_keys=False)
    # read file
    with open(path_str, "r") as f:
        yaml_dict = {}
        try:
            yaml_dict = yaml.safe_load(f)
        except Exception as e:
            print("Invalid setting!")
            print(f"Reason:\n {e}")
    res = None
    if yaml_dict is None:
        return res
    # passing dict from yaml file to Settings
    try:
        res = Settings(**yaml_dict)
    except Exception as e:
        print("Invalid setting!")
        print(f"Reason:\n {e}")

    return res


def save_settings(settings: Settings, path_str: str = "settings.yaml"):
    """
    Save settings to file

    Args:
        settings (Settings): The Settings instance.
        path_str (str): Path to the file where the settings are to be saved.
    """
    # rearrange the id's so that they are in order
    for i in range(len(settings.grid)):
        settings.grid[i].id = i + 1
    dump_of_model = RootModel[Settings](settings).model_dump(by_alias=True)
    # save to file
    with open(path_str, "w") as f:
        yaml.dump(dump_of_model, f, Dumper=IndentDumper)


class SettingsManager:
    """
    Class which is a representation of a class Settings.
    """

    def __init__(self, settings: Optional[Settings]):
        """
        __init__ method.
        Args:
            settings: The Settings instance.
        """
        self._settings: Optional[Settings] = settings
        self._error: bool = False if settings is not None else True
        self._windows_attributes: List[WindowAttributes] = []
        self._grid: List[Cell] = []

        self._is_running: Value = Value("i", 0)
        """Value: process communication field"""
        if not self._error:
            if len(self._settings.windows_attributes) > 0:
                self._prepare_windows_attributes()
            if len(self._settings.grid) > 0:
                self._prepare_grid()

            self._settings.windows_attributes = self._windows_attributes
            self._settings.grid = self._grid

    def _prepare_windows_attributes(self):
        if isinstance(self._settings.windows_attributes[0], dict):
            for window_attributes_dict in self._settings.windows_attributes:
                # get WindowAttributes from dict
                window_attributes = next(iter(window_attributes_dict.values()))

                current_exclude_windows_list = []
                # getting ExcludeWindow for this WindowAttributes
                if len(window_attributes.exclude_windows) > 0:

                    if isinstance(window_attributes.exclude_windows[0], dict):
                        for exclude_window_dict in window_attributes.exclude_windows:
                            # get ExcludeWindow from dict
                            exclude_window = next(iter(exclude_window_dict.values()))
                            current_exclude_windows_list.append(exclude_window)
                    else:
                        current_exclude_windows_list = window_attributes.exclude_windows

                window_attributes.exclude_windows = current_exclude_windows_list

                self._windows_attributes.append(window_attributes)
        else:
            for window_attributes in self._settings.windows_attributes:
                self._windows_attributes.append(window_attributes)

    def _prepare_grid(self):
        if isinstance(self._settings.grid[0], dict):
            # get one value (Cell) from dict.values() and make list of them
            self._grid = list(map(lambda x: next(iter(x.values())), self._settings.grid))
            self._grid.sort(key=lambda x: x.id)
        else:
            for cell in self._settings.grid:
                self._grid.append(cell)

    def reconfigure(self, settings: Optional[Settings]):
        """
        Update fields from Settings instance.
        Args:
            settings: The Settings instance.
        """
        new_setting_manager = SettingsManager(settings)
        self._settings = settings
        self._error = new_setting_manager._error
        self._windows_attributes = new_setting_manager._windows_attributes
        self._grid = new_setting_manager._grid
        self._is_running = new_setting_manager._is_running

    @property
    def error(self) -> bool:
        """bool: Indicates the existence of a Settings instance."""
        return self._error

    @property
    def settings(self) -> Optional[Settings]:
        """Settings: The Settings instance."""
        return self._settings

    @property
    def windows_attributes(self) -> List[WindowAttributes]:
        """list: The list of WindowAttributes."""
        return self._windows_attributes

    @property
    def grid(self) -> List[Cell]:
        """list: The list of Cell"""
        return self._grid

    @property
    def is_running(self) -> bool:
        """bool: Indicates whether the core algorithm is running."""
        return bool(self._is_running.value)

    @is_running.setter
    def is_running(self, value: bool):
        with self._is_running.get_lock():
            self._is_running.value = int(value)
