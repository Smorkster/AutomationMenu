"""
Create a Frame and a Text widget for displaying output from a running script

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from tkinter import Text
from tkinter.ttk import Frame, Notebook, Scrollbar
from typing import Callable

from automation_menu.ui.types.widget_for_translation import WidgetForTranslation


def get_output_tab( tabcontrol: Notebook, translate_callback: Callable ) -> tuple[ Frame, Text ]:
    """ Create the output tab used to display script execution output.

    Args:
        tabcontrol (Notebook): Notebook widget to attach the output tab to.
        translate_callback (Callable): Callback used to register widgets for translation.

    Returns:
        tuple[Frame, Text]: Created output tab frame and output text widget.
    """

    from automation_menu.utils.localization import _

    tabOutput: Frame = Frame( master = tabcontrol , padding = ( 5, 5, 5, 5 ) )
    tabOutput.columnconfigure( index = 0, weight = 1 )
    tabOutput.rowconfigure( index = 0, weight = 1 )
    tabOutput.grid( sticky = 'nswe' )

    tabcontrol.add( child = tabOutput, text = _( 'Script output' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = tabOutput, default_text = 'Script output' )
    translate_callback( wft )

    output: Text = Text( master = tabOutput, wrap = 'word', font = ( 'Calibri', 12 ) )
    output.config( state = 'disabled' )
    output.grid( column = 0, row = 0, sticky = 'nswe' )

    scrollbar: Scrollbar = Scrollbar( master = tabOutput, orient='vertical', command = output.yview )
    scrollbar.grid( column = 1, row = 0, sticky = 'nse' )
    output.config( yscrollcommand = scrollbar.set )

    return tabOutput, output
