

from tkinter import BooleanVar, StringVar
from tkinter.ttk import Button, Checkbutton, Combobox, Entry, Treeview
from typing import TypedDict


class SettingsUiDict( TypedDict ):
    """ Defined dict for settings widgets """

    chbTopMost: Checkbutton
    chbMinimizeOnRunning: Checkbutton
    chb_force_focus_post_execution: Checkbutton
    cmbCurrentLanguage: Combobox
    keepass_shortcut_ctrl: Checkbutton
    keepass_shortcut_ctrl_val: BooleanVar
    keepass_shortcut_alt: Checkbutton
    keepass_shortcut_alt_val: BooleanVar
    keepass_shortcut_shift: Checkbutton
    keepass_shortcut_shift_val: BooleanVar
    keepass_shortcut_key: Entry
    keepass_shortcut_key_val: StringVar
    chbSendMailOnError: Checkbutton
    chbIncludeSsInErrorMail: Checkbutton
    script_folders_list: Treeview
    script_folder_btn_add: Button
    script_folder_btn_remove: Button
