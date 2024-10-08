import multiprocessing
import sys
from time import sleep

import keyboard

from daemon import processing_start
from settings import get_settings, SettingsManager

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        # On Windows calling this function is necessary.
        multiprocessing.freeze_support()
    print("Program work! Press 'ctrl+q' for exit.")
    settings = get_settings()
    settings_manager = SettingsManager(settings)
    settings_manager.is_running = True
    if not settings_manager.error:
        processing_start(settings_manager)
        keyboard.wait('ctrl+q')
        settings_manager.is_running = False
        print("\nExit!")
        sleep(3)
