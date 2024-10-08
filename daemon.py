import ctypes
import time
from collections import defaultdict
from ctypes import wintypes
from math import sqrt
from multiprocessing import get_context
from pathlib import Path
from typing import List, Set, Dict, Optional, ItemsView

import win32api
import win32con
import win32gui
import win32process

from settings import WindowAttributes, SettingsManager, Cell, ExcludeWindow

DWMWA_EXTENDED_FRAME_BOUNDS = 9


class MouseTracker:
    """
    Class for tracking mouse actions.

    Attributes:
        is_holding (bool): Indicates if the left mouse button is held down.
        hold_start_time (float): Left mouse button press time.
        hold_threshold (float): Threshold value after which we consider that the left mouse button is held down, not just clicked.
    """

    def __init__(self, hold_threshold: float):
        self.is_holding: bool = False
        self.hold_start_time: float = time.time()
        self.hold_threshold: float = hold_threshold

    def is_left_mouse_button_down(self) -> bool:
        """
        Checking whether the left mouse button is pressed.

        Returns:
            True if the left mouse button is pressed otherwise False.
        """
        # VK_LBUTTON is the virtual-key code for the left mouse button
        return win32api.GetKeyState(0x01) & 0x8000 > 0

    def is_left_mouse_button_hold(self) -> bool:
        """
        Check that the left button is held down.

        Returns:
            True if the left mouse button is held down otherwise False
        """
        if self.is_left_mouse_button_down():
            # If the button has not been pressed before, we initiate the tracking fields
            if not self.is_holding:
                self.hold_start_time = time.time()
                self.is_holding = True
            # If the time elapsed from pressing the button is more than the threshold value,
            # then the button is considered to be held down
            elif time.time() - self.hold_start_time >= self.hold_threshold:
                return True
        else:
            # If the button has been pressed before, unset is_holding
            if self.is_holding:
                if time.time() - self.hold_start_time < self.hold_threshold:
                    return False
                self.is_holding = False

        return False


class PlacementManager:
    """
    Class, which contains structures for the core algorithm functioning.

    Attributes:
        all_hwnd (set): Set that stores handles of all detected windows.
    """

    def __init__(self, settings_manager: SettingsManager):
        self._settings_manager = settings_manager
        self._windows_attributes_name: Set[str] = set()
        """Set[str]: Stores the names of processes to be processed."""

        self._windows_attributes_dict: Dict[str, WindowAttributes] = dict()
        """Dict[str, WindowAttributes]: Maps the name of the process to its WindowAttributes."""

        self._set_pos_calls: Dict[int, int] = dict()
        """Dict[int, int]: Maps the window handle to the amount of window sizing calls made."""

        self._set_pos_max_count: int = 5
        """int: Maximum number of size selection calls."""

        self._hwnd_to_cels: Dict[int, Cell] = dict()
        """Dict[int, Cell]: Maps the window handle to its Cell in grid."""

        self._exclude_window_names: Dict[str, Set[str]] = defaultdict(set)
        """Dict[str, Set[str]]: Maps the name of the process to its exclude window name."""

        self._hwnd_to_name: Dict[int, str] = dict()
        """Dict[int, str]: Maps the window handle to the process name."""

        self.all_hwnd: Set[int] = set()

        for window_attributes in self._settings_manager.windows_attributes:
            self._windows_attributes_name.add(window_attributes.process_name)
            self._windows_attributes_dict[window_attributes.process_name] = window_attributes

            for exclude_window in window_attributes.exclude_windows:
                exclude_window: ExcludeWindow
                self._exclude_window_names[window_attributes.process_name].add(exclude_window.name)

    @property
    def windows_attributes(self) -> List[WindowAttributes]:
        return self._settings_manager.windows_attributes

    @property
    def lookup_names(self) -> Set[str]:
        """Set[str]: Set with the names of the processes we select."""
        return self._windows_attributes_name

    def get_window_attributes(self, process_name: str) -> WindowAttributes:
        """
        Get WindowAttributes by process name.

        Args:
            process_name (str): A process name.
        Returns:
            WindowAttributes: WindowAttributes which is associated with the passed process name.
        """
        return self._windows_attributes_dict[process_name]

    def need_set_pos_call(self, hwnd: int) -> bool:
        """
        Checking whether sizing is necessary.

        Args:
            hwnd (int): Window handle that needs checking.
        Returns:
            bool: True if for a window handle needs to call sizing otherwise False.
        """
        return self._set_pos_calls.setdefault(hwnd, 0) < self._set_pos_max_count

    def increase_set_pos_call_count(self, hwnd: int):
        """
        Increased number of sizing calls for a given window handle.

        Args:
            hwnd (int): Window handle for which the number of sizing calls need to be increased.
        """
        self._set_pos_calls[hwnd] += 1

    def is_exclude_window(self, proc_name: str, window_name: str) -> bool:
        """
        Checking whether the window name is excluded from processing.

        Args:
            proc_name (str): Name of the process to be checked.
            window_name (str): Name of the window to be checked.
        Returns:
            True, if the gotten window name is to be excluded from processing otherwise False.
        """
        return window_name in self._exclude_window_names[proc_name]

    @property
    def is_using_grid(self) -> bool:
        """bool: True if you need to use grid window placement otherwise False"""
        return self._settings_manager.settings.using_grid

    def link_cell(self, hwnd: int, cell: Cell):
        """
        Make a link between the getting cell and the window handle.

        Args:
            hwnd (int): Window handle to be associated with a cell.
            cell (Cell): Cell to be associated with this window handleю
        """
        cell.hwnd = hwnd
        self._hwnd_to_cels[hwnd] = cell

    def unlink_cell(self, hwnd: int, cell: Cell):
        """
        Remove a link between the getting cell and the window handle.

        Args:
            hwnd (int): Window handle  to be unlinked from the cell.
            cell (Cell): Cell to be unlinked from the window handle.
        """
        cell.hwnd = 0
        if hwnd in self._hwnd_to_cels:
            del self._hwnd_to_cels[hwnd]

    def get_cell(self, hwnd: int) -> Optional[Cell]:
        """
        Getting a grid cell for a given window handle.

        Args:
            hwnd (int): Window handle, for which a cell is needed.
        Return:
            Сell if available, otherwise None.
        """
        # If the given window handle has already been assigned to a cell, return it
        if hwnd in self._hwnd_to_cels:
            return self._hwnd_to_cels[hwnd]

        # free cell search
        for cell in self._settings_manager.grid:
            # If a cell belonged to some window handle, but now it is no longer in the all_hwnd
            # it means that this window was closed, and it is possible to select the vacated cell
            if cell.hwnd not in self.all_hwnd:
                self.link_cell(hwnd, cell)
                return cell

        return None

    def search_nearest_cell(self, x: int, y: int) -> Cell:
        """
        Search for the nearest cell to the given coordinates

        Args:
             x (int): Position by x
             y (int): Position by y
        Returns:
            Cell that is near the given coordinates.
        """
        cur_cell: Cell = self._settings_manager.grid[0]
        # Finding the minimum by Euclidean norm
        min_distance = sqrt((x - cur_cell.x) ** 2 + (y - cur_cell.y) ** 2)
        for cell in self._settings_manager.grid:
            cur_distance = sqrt((x - cell.x) ** 2 + (y - cell.y) ** 2)
            if cur_distance < min_distance:
                min_distance = cur_distance
                cur_cell = cell
        return cur_cell

    def move_to_cell(self, hwnd: int, dest_cell: Cell):
        """
        Changing window binding to another cell.

        Args:
            hwnd (int): Window handle whose binding is to be changed.
            dest_cell (Cell): Cell to which the binding is to be changed.
        """
        if dest_cell.hwnd == hwnd:
            return

        curr_cell = self.get_cell(hwnd)
        if curr_cell:
            if curr_cell.x == dest_cell.x and curr_cell.y == dest_cell.y:
                return
            else:
                curr_cell.hwnd = 0
        # if the destination cell is empty
        if dest_cell.hwnd == 0:
            self.link_cell(hwnd, dest_cell)
        # if the destination cell is not empty, cell exchange
        else:
            if curr_cell:
                self.link_cell(dest_cell.hwnd, curr_cell)
                self.link_cell(hwnd, dest_cell)
            # else:
            #     self.unlink_cell(dest_cell.hwnd, dest_cell)
            #     self.link_cell(hwnd, dest_cell)

    def register_process(self, hwnd: int, process_name: str):
        """
        Makes a mapping of a window handle to its process name.

        Args:
            hwnd (int): Window handle to which to bind the process name.
            process_name (str): Process name to be bound.
        """
        self._hwnd_to_name[hwnd] = process_name

    def registered_processes_iter(self) -> ItemsView[int, str]:
        """
        Provides the possibility to get registered window handles and their process name.

        Returns:
            An iterated object consisting of pairs (hwnd, process_name).
        """
        return self._hwnd_to_name.items()

    def is_registered_hwnd(self, hwnd: int) -> bool:
        """
        Checking whether a window handler has been registered.

        Args:
            hwnd (int): Window handler to be checked.

        Returns:
            True if the window handle was registered otherwise False.
        """
        return hwnd in self._hwnd_to_name

    def reset(self):
        """Resetting the internal state."""
        self.all_hwnd.clear()
        self._hwnd_to_name.clear()


def winEnumHandler(hwnd: int, placement_manager: PlacementManager):
    """
    Window handle processing function.

    Args:
        hwnd (int): Window handle to be processed
        placement_manager (PlacementManager): Instance of PlacementManager in which data is stored for further processing
    """
    if win32gui.IsWindowVisible(hwnd):
        placement_manager.all_hwnd.add(hwnd)
        window_name: str = win32gui.GetWindowText(hwnd)
        threadId, processId = win32process.GetWindowThreadProcessId(hwnd)

        handle = None
        try:
            handle = win32api.OpenProcess(win32con.PROCESS_QUERY_LIMITED_INFORMATION, False, processId)
        except Exception as e:
            pass

        if handle is None:
            return

        proc_path: str = win32process.GetModuleFileNameEx(handle, 0)  # information about where the process is located

        proc_name = str(Path(proc_path).name)
        if proc_name in placement_manager.lookup_names and not placement_manager.is_exclude_window(proc_name,
                                                                                                   window_name):
            placement_manager.register_process(hwnd, proc_name)


def processing_detected_windows(placement_manager: PlacementManager):
    """
    Processing previously detected windows.

    Args:
        placement_manager (PlacementManager): Instance of PlacementManager which contains information on the window to be processed.
    """
    # This call allows you to ignore dpi so that window sizes do not depend on it
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
    for hwnd, proc_name in placement_manager.registered_processes_iter():
        window_attributes = placement_manager.get_window_attributes(proc_name)

        if placement_manager.need_set_pos_call(hwnd):
            move_window = win32con.SWP_NOMOVE
            if window_attributes.use_coordinates and not placement_manager.is_using_grid:
                move_window = win32con.SWP_SHOWWINDOW

            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, window_attributes.x, window_attributes.y,
                                  window_attributes.width, window_attributes.height, move_window)
            placement_manager.increase_set_pos_call_count(hwnd)

        rect = ctypes.wintypes.RECT()
        # this call allows you to get the size of the window
        # (this size is different from the size obtained with GetWindowRect)
        hresult = ctypes.windll.dwmapi.DwmGetWindowAttribute(hwnd,
                                                             DWMWA_EXTENDED_FRAME_BOUNDS,
                                                             ctypes.byref(rect),
                                                             ctypes.sizeof(rect)
                                                             )
        rect_width = rect.right - rect.left
        rect_height = rect.bottom - rect.top

        is_correct_width = rect_width == window_attributes.width
        is_correct_height = rect_height == window_attributes.height
        # if the width or height differs from the specified width or height, we calculate the added value
        if not is_correct_width:
            window_attributes.additional_width = window_attributes.width - rect_width
            window_attributes.additional_width = window_attributes.additional_width if window_attributes.additional_width > 0 else 0
        if not is_correct_height:
            window_attributes.additional_height = window_attributes.height - rect_height
            window_attributes.additional_height = window_attributes.additional_height if window_attributes.additional_height > 0 else 0

        current_left = window_attributes.x
        current_top = window_attributes.y

        # there may be a situation where the window is already closed
        try:
            current_left, current_top, _, _ = win32gui.GetWindowRect(hwnd)
        except Exception as e:
            continue

        move_window = win32con.SWP_NOMOVE
        left = window_attributes.x
        top = window_attributes.y
        is_correct_left = True
        is_correct_top = True
        if placement_manager.is_using_grid:
            cell = placement_manager.get_cell(hwnd)
            if cell:
                left = cell.x
                top = cell.y
                is_correct_left = current_left == cell.x
                is_correct_top = current_top == cell.y
                move_window = win32con.SWP_SHOWWINDOW

        if not is_correct_width or not is_correct_height or not is_correct_left or not is_correct_top:
            width = window_attributes.width + window_attributes.additional_width
            height = window_attributes.height + window_attributes.additional_height
            win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, left, top, width, height, move_window)


def processing_window_change_pos(placement_manger: PlacementManager):
    """
    Processing of window position changes.

    Args:
        placement_manger (PlacementManager): Instance of PlacementManager containing information about where the window should be placed.
    """
    cur_pos_x, cur_pos_y = win32api.GetCursorPos()
    cur_window_hwnd = win32gui.WindowFromPoint((cur_pos_x, cur_pos_y))

    if not placement_manger.is_registered_hwnd(cur_window_hwnd) or not placement_manger.is_using_grid:
        return

    current_left = cur_pos_x
    current_top = cur_pos_y

    # there may be a situation where the window is already closed
    try:
        current_left, current_top, _, _ = win32gui.GetWindowRect(cur_window_hwnd)
    except Exception as e:
        return

    cell = placement_manger.search_nearest_cell(current_left, current_top)
    placement_manger.move_to_cell(cur_window_hwnd, cell)


def resize_window(setting_manager: SettingsManager):
    """
    Function that continuously processes windows depending on the mouse state.

    Args:
        setting_manager (SettingsManager): Instance of SettingsManager which contains information on where and how the windows should be placed
    """
    placement_manager = PlacementManager(setting_manager)
    mouse_tracker = MouseTracker(0.1)
    # Indicator of whether the left mouse button has been held down before
    prev_is_hold = False
    while setting_manager.is_running:
        win32gui.EnumWindows(winEnumHandler, placement_manager)
        is_hold = mouse_tracker.is_left_mouse_button_hold()
        if not prev_is_hold and not is_hold:
            processing_detected_windows(placement_manager)
        # make window positioning when the user left mouse button is up
        if prev_is_hold and not is_hold:
            processing_window_change_pos(placement_manager)

        prev_is_hold = is_hold
        placement_manager.reset()


def processing_start(settings_manager: SettingsManager):
    """
    Function to start the process in which windows will be processed.

    Args:
        settings_manager (SettingsManager): Instance of SettingsManager which contains information on where and how the windows should be placed
    """
    mp_context = get_context('spawn')
    p = mp_context.Process(target=resize_window, args=(settings_manager,), daemon=True)
    p.start()
