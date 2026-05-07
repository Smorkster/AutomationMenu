"""
Define widget references used by the execution history UI.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter import Text
from tkinter.ttk import Frame, Treeview


class HistoryUi():
    """ Store widget references used by the history UI."""

    def __init__( self ) -> None:
        """ Initialize the history UI widget reference container."""

        pass

    history_item_display: Frame
    tabHistory: Frame

    duration: Text
    item_end: Text
    item_output: Text
    item_start: Text

    history_tree: Treeview
