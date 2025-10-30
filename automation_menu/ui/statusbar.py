"""
Create a statusbar for displaying text and a progressbar

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0.0
Created: 2025-09-25
"""


from tkinter import E, N, S, W, Tk
from tkinter.ttk import Frame, Label, Progressbar, Separator

from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip


def get_statusbar( master_root: Tk ):
    """ """

    status_frame = Frame( master = master_root )
    status_frame.grid( columnspan = 2, row = 3, sticky = ( W, E, S ) )

    status_frame.columnconfigure( index = 0, weight = 1 )
    status_frame.columnconfigure( index = 1, weight = 0 )
    status_frame.columnconfigure( index = 2, weight = 1 )

    column_separator = Separator( master = status_frame, orient = 'vertical' )
    column_separator.grid( column = 1, sticky = ( N, S ) )

    text_status, status_tt = _create_status_textfield( status_frame = status_frame )

    return {
        'text_status': text_status,
        'text_status_tt': status_tt,
        'progressbar': _create_progressbar( status_frame = status_frame ),
        'separator': column_separator
    }


def _create_status_textfield( status_frame: Frame ) -> Label:
    """ Create a Label widget to display execution status """

    execution_status = Label( master = status_frame, padding = ( 5, 5 ) )
    execution_status.grid( column = 0, row = 0, sticky = ( W, E ) )

    status_tt = AlwaysOnTopToolTip( widget = execution_status, msg = 'Execution status can be updated from the running script' )

    return execution_status, status_tt


def _create_progressbar( status_frame: Frame ) -> Progressbar:
    """ """

    execution_progress = Progressbar( master = status_frame )
    execution_progress.grid( column = 2, row = 0, padx = 5, pady = 5, sticky = ( W, E ) )
    execution_progress.grid_remove()

    return execution_progress
