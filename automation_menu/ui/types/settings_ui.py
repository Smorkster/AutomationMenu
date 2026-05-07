"""
Define widget references used by the settings UI.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter import BooleanVar, StringVar
from tkinter.ttk import Button, Checkbutton, Combobox, Entry, Treeview


class SettingsUi():
    """ Store widget references used by the settings UI."""

    def __init__( self ) -> None:
        """ Initialize the settings UI widget reference container."""

        pass


    keepass_shortcut_alt_val: BooleanVar | None
    keepass_shortcut_ctrl_val: BooleanVar | None
    keepass_shortcut_shift_val: BooleanVar | None

    cmb_current_language_val: StringVar | None

    script_folder_btn_add: Button | None
    script_folder_btn_remove: Button | None

    chb_force_focus_post_execution: Checkbutton | None
    chb_include_ss_in_error_mail: Checkbutton | None
    chb_minimize_on_running: Checkbutton | None
    chb_send_mail_on_error: Checkbutton | None
    chb_top_most: Checkbutton | None
    keepass_shortcut_ctrl: Checkbutton | None
    keepass_shortcut_alt: Checkbutton | None
    keepass_shortcut_shift: Checkbutton | None

    cmb_current_language: Combobox | None

    keepass_shortcut_key: Entry | None

    keepass_shortcut_key_val: StringVar | None

    script_folders_list: Treeview | None
