import multiprocessing
import os
import sys
from tkinter import Tk, Menu
from tkinter.messagebox import askyesno
from tkinter.ttk import Notebook

import pystray
from PIL import Image
from pystray import MenuItem

from gui.elements.grid_tab import GridTabWindow
from gui.elements.main_tab import MainTabWindow
from gui.elements.settings_control_menu import SettingsControlMenu
from settings import get_settings, SettingsManager

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        multiprocessing.freeze_support()

    # Create main window
    root = Tk()
    root.title("Resizer")
    root.geometry("260x280")

    application_path = ""
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    elif __file__:
        application_path = os.path.dirname(__file__)

    icon_file = 'favicon.ico'

    root.iconbitmap(default=os.path.join(application_path, icon_file))

    # Create tabs control
    tab_control = Notebook(root)
    tab_control.pack(expand=True, fill="both")

    settings = get_settings()
    settings_manager = SettingsManager(settings)

    # Create menu
    main_menu = Menu(root)
    root.config(menu=main_menu)
    settings_menu = SettingsControlMenu(main_menu, settings_manager)

    main_menu.add_cascade(label="File", menu=settings_menu.file_menu)

    # Create tabs object
    main_tab = MainTabWindow(tab_control, settings_menu.settings_manager)
    grid_tab = GridTabWindow(tab_control, settings_menu.settings_manager)

    # Add handle to update when new settings are loaded
    settings_menu.add_handle(main_tab.update_windows_attributes_var)
    settings_menu.add_handle(grid_tab.update_cells_var)
    settings_menu.add_handle(grid_tab.update_use_grid_var)

    # Add handle to change objects at processing start
    main_tab.add_start_handle(settings_menu.disable)
    main_tab.add_start_handle(lambda: tab_control.tab(1, state="disabled"))

    # Add handle to change objects at processing stop
    main_tab.add_stop_handle(settings_menu.enable)
    main_tab.add_stop_handle(lambda: tab_control.tab(1, state="normal"))


    # Handler for the tray menu item "Quit"
    def quit_window(icon, item):
        root.after(0, root.deiconify)
        result = askyesno(title="Program closing",
                          message="The program will stop working. Are you sure you want to shut it down?")
        if result:
            icon.stop()
            main_tab.stop_processing()
            root.destroy()
        else:
            icon.stop()


    # Handler for the tray menu item "Show"
    def show_window(icon, item):
        icon.stop()
        root.after(0, root.deiconify)


    # Redefinition function when main tab close
    def withdraw_window():
        root.withdraw()
        image = Image.open(os.path.join(application_path, icon_file))
        menu = (MenuItem("Show", show_window),
                MenuItem(lambda text: "Stop processing" if main_tab.is_processing else "Start processing",
                         lambda x: main_tab.stop_processing() if main_tab.is_processing else main_tab.start_processing()),
                MenuItem("Exit", quit_window),
                )
        icon = pystray.Icon("resizer_icon", image, "Resizer", menu)
        icon.run()


    root.protocol("WM_DELETE_WINDOW", withdraw_window)

    tab_control.add(main_tab.frame, text="Window settings")
    tab_control.add(grid_tab.frame, text="Grid settings")

    root.mainloop()
