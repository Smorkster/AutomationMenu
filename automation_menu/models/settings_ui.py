

from tkinter import BooleanVar, StringVar
from tkinter.ttk import Button, Checkbutton, Combobox, Entry, Treeview


class SettingsUi():
    """ Defined dict for settings widgets """

    def __init__(self) -> None:
        """ Widget storage for settings ui """

        pass

    keepass_shortcut_ctrl_val: BooleanVar | None
    keepass_shortcut_alt_val: BooleanVar | None
    keepass_shortcut_shift_val: BooleanVar | None

    cmbCurrentLanguage_val: StringVar | None

    script_folder_btn_add: Button | None
    script_folder_btn_remove: Button | None

    chbTopMost: Checkbutton | None
    chbMinimizeOnRunning: Checkbutton | None
    chb_force_focus_post_execution: Checkbutton | None
    keepass_shortcut_ctrl: Checkbutton | None
    keepass_shortcut_alt: Checkbutton | None
    keepass_shortcut_shift: Checkbutton | None
    chbSendMailOnError: Checkbutton | None
    chbIncludeSsInErrorMail: Checkbutton | None

    cmbCurrentLanguage: Combobox | None

    keepass_shortcut_key: Entry | None

    keepass_shortcut_key_val: StringVar | None

    script_folders_list: Treeview | None
