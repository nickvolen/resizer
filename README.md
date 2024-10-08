# Resizer

Resizer is free, open-source application that allows you to set and maintain a specified window size for an application in Windows OS.
- [About](#about)
- [GUI usage](#GUI)
- [Build](#build)

## About

Resizer is app for Windows OS that uses Windows API calls to set the window size of selected application. Moreover, it has an option to set the grid on which the windows will be placed and move or replace windows between grid cells.

## GUI

<details>
  <summary><b>How to add new process for processing its windows?</b></summary>
    On the main screen, select a <i>Window settings</i> tab and press 1.<br>
    <img src="assets/add_new_proc_1.png" alt="Add new process screenshot 1"><br>
    After that a window will open in which you need to fill in. The <i>Use coordinates?</i> flag indicates whether all windows of this process should open in the given coordinates or not.<br>
    <img src="assets/add_new_proc_2.png" alt="Add new process screenshot 2"><br>
    After you have filled out this window, <b>make sure</b> to click the <b>Save</b> button or nothing will be saved.
</details>

<details>
  <summary><b>How to edit process windows attributes or cell coordinates?</b></summary>
    To edit the attributes of a process window or coordinates of cell, you must select it from the list. Then double-click on it or click on the <i>Edit</i> button (1 on the screenshot).<br>
    <img src="assets/edit_proc_1.png" alt="Edit process windows attributes screenshot 1"><br>
    After that, a window will open where you can edit attributes of a process window.
</details>

<details>
  <summary><b>How to add process window names to be ignored?</b></summary>
    You can do this when adding new process for processing its windows or editing a selected process windows attributes. To do this, in the window for editing the process window attributes, press on 1.<br>
    <img src="assets/add_exclude_window_1.png" alt="Add exclude windows name screenshot 1"><br>
    This will open a window where you need to enter the <b>exact</b> name of the window you want to ignore.<br>
    <img src="assets/add_exclude_window_2.png" alt="Add exclude windows name  screenshot 2"><br>
    After you have filled out this window, <b>make sure</b> to click the <b>Save</b> button or nothing will be saved. Also, don't forget to save the attributes of the process window.
</details>

<details>
  <summary><b>How do you use grid layout?</b></summary>
    In the program you can set the grid layout for the windows of the processed processes.<br>
    For this, on the main screen, select a <i>Grid settings</i> tab and enable the <i>Use grid?</i> flag. Note that this method has a higher priority than using coordinates in the process window attributes.<br>
    <img src="assets/use_grid_1.png" alt="Use grid screenshot 1"><br>
    After that, you will have an area that shows the cells of the grid.<br>
    <img src="assets/use_grid_2.png" alt="Use grid screenshot 2"><br>
</details>

<details>
  <summary><b>How to add a new cell to a grid?</b></summary>
    When using grid layout, you can add a new cell using the button 1.<br>
    <img src="assets/add_new_cell_1.png" alt="Add new grid cell screenshot 1"><br>
    After that, the window for filling in the cell coordinates will open.<br>
    <img src="assets/add_new_cell_2.png" alt="Add new grid cell screenshot 2"><br>
    Accordingly, the upper left corners of the processed process windows will be located in the entered cell coordinates.
</details>

<details>
  <summary><b>How to change the grid cell priority?</b></summary>
    The process windows are placed in the cell in the order in which they appear in the list. That is, the windows will be placed in cell 1 first, followed by cell 2, and so on.<br>
    <img src="assets/cell_priority_1.png" alt="Cell priority screenshot 1"><br>
    To change the priority of a cell, select it. If you want to increase the priority, press button 1, otherwise press button 2.
    <img src="assets/cell_priority_2.png" alt="Cell priority screenshot 2"><br>
</details>

<details>
  <summary><b>How to save the settings?</b></summary>
    To save the settings, you must select <i>File->Save</i> from the top menu.<br>
    <img src="assets/save_settings_1.png" alt="Save settings screenshot 1"><br>
    After that, a window will open where you will need to specify the locations and file names. The default settings file is named
</details>

<details>
  <summary><b>How to exit?</b></summary>
    The standard program closing logic is overridden to minimize the program. So, to exit the program, you must either select <i>Exit</i> from the minimized application menu or select <i>File->Exit</i> from the top menu when the program is shown.<br>
    <img src="assets/app_exit_1.png" alt="Exit the application when it is shown"><img src="assets/app_exit_2.png" alt="Exit an application when it is minimized">
</details>

## Build

Tested for **python 3.10**

1. Clone the repository: `git clone https://github.com/nickvolen/resizer.git`.
2. Install dependencies `pip intall -r requirements.txt`
3. Build application `pyintaller --distpath <DIST_PATH> resizer_gui.spec`

You can use the console version of the application, but all settings will have to be done manually in the settings.yaml file, which is there by default as a template.

To build the console version, you need to follow steps 1-2 from the previous step and `pyintaller --distpath <DIST_PATH> resizer.spec`