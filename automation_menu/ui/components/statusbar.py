"""
Create a statusbar for displaying text and a progressbar

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
from tkinter import Tk
from tkinter.ttk import Frame, Label, Progressbar, Separator

from automation_menu.ui.types.status_ui import StatusUi


def _create_progressbar( status_ui: StatusUi ) -> None:
    """ Create the status bar progress bar widget.

    Args:
        status_ui (StatusUi): Status UI object to attach the progress bar to.
    """

    status_ui.progressbar = Progressbar( master = status_ui.status_bar )
    status_ui.progressbar.grid( column = 2, row = 0, padx = 5, pady = 5, sticky = 'we' )
    status_ui.progressbar.grid_remove()


def _create_status_textfield( status_ui: StatusUi ) -> None:
    """ Create the status text label and its tooltip.

    Args:
        status_ui (StatusUi): Status UI object to attach the status text field to.
    """

    from automation_menu.utils.localization import _

    status_ui.text_status = Label( master = status_ui.status_bar, padding = ( 5, 5 ) )
    status_ui.text_status.grid( column = 0, row = 0, sticky = 'we' )

    status_ui.text_status_tt = AlwaysOnTopToolTip( widget = status_ui.text_status, msg = _( 'Execution status can be updated from running script' ) )


def get_statusbar( parent_frame: Frame ) -> StatusUi:
    """ Create the status bar UI.

    Args:
        parent_frame (Frame): Window to attach the status bar to.

    Returns:
        ui (StatusUi): Created status bar UI widgets.
    """

    ui: StatusUi = StatusUi()

    ui.status_bar = Frame( master = parent_frame )
    ui.status_bar.grid( columnspan = 2, row = 3, sticky = 'wes' )

    ui.status_bar.columnconfigure( index = 0, weight = 1 )
    ui.status_bar.columnconfigure( index = 1, weight = 0 )
    ui.status_bar.columnconfigure( index = 2, weight = 1 )

    ui.separator = Separator( master = ui.status_bar, orient = 'vertical' )
    ui.separator.grid( column = 1, sticky = 'ns' )

    _create_status_textfield( status_ui = ui  )
    _create_progressbar( status_ui = ui )

    return ui
