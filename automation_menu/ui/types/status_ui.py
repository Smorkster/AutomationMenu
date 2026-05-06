"""
Define widget references used by the status bar UI.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
from tkinter.ttk import Frame, Label, Progressbar, Separator


class StatusUi():
    """ Store widget references used by the status bar UI."""

    def __init__( self ) -> None:
        """ Initialize the status bar UI widget reference container."""

        pass


    text_status_tt: AlwaysOnTopToolTip

    status_bar: Frame

    text_status: Label

    progressbar: Progressbar

    separator: Separator

