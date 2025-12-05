"""
Create a Frame and a Text widget for displaying output from a running script

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from tkinter import E, N, S, W, Text, ttk
from typing import Callable


def get_output_tab( tabcontrol: ttk.Notebook, translate_callback: Callable ) -> tuple[ ttk.Frame, Text ]:
    """ Create a frame used as tab to display output data from script execution

    Args:
        tabcontrol (Notebook): Tabcontrol (Notebook) to place the frame in
    """

    from automation_menu.utils.localization import _

    tabOutput = ttk.Frame( master = tabcontrol , padding = ( 5, 5, 5, 5 ) )
    tabOutput.columnconfigure( index = 0, weight = 1 )
    tabOutput.rowconfigure( index = 0, weight = 1 )
    tabOutput.grid( sticky = ( N, S, E, W ) )

    tabcontrol.add( child = tabOutput, text = _( 'Script output' ) )
    translate_callback( ( tabOutput, 'Script output' ) )

    output = Text( master = tabOutput, wrap = 'word', font = ( 'Calibri', 12 ) )
    output.config( state = 'disabled' )
    output.grid( column = 0, row = 0, sticky = ( N, S, E, W ) )

    scrollbar = ttk.Scrollbar( master = tabOutput, orient='vertical', command = output.yview )
    scrollbar.grid( column = 1, row = 0, sticky = ( N , S , E ) )
    output.config( yscrollcommand = scrollbar.set )

    return tabOutput, output
