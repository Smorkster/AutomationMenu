"""
Define widget references used by the persistent GUI display management UI.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter import Tk
from tkinter.scrolledtext import ScrolledText

from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
from tkinter.ttk import Button, Frame, Label, Notebook, Treeview

from automation_menu.ui.types.op_persistent_buttons_ui import OpPersistentButtonsUi


class PersistentUi():
    """ Container object for widgets used by the persistent scripts tab. """

    def __init__( self ) -> None:
        """ Allow attributes to be attached as widgets are created. """

        pass


    info_full_path: AlwaysOnTopToolTip

    kill_btn: Button
    resume_btn: Button
    pause_btn: Button
    show_btn: Button
    stop_btn: Button

    info_display: Frame
    main_frame: Frame

    info_error_title: Label
    info_output_title: Label
    info_name: Label
    info_name_title: Label
    info_progress: Label
    info_progress_title: Label
    info_state: Label
    info_state_title: Label
    info_status: Label
    info_status_title: Label

    tab_control: Notebook

    op_buttons: OpPersistentButtonsUi

    info_error: ScrolledText
    info_output: ScrolledText

    root: Tk

    running_scripts: Treeview
