"""
Create a Frame and a Text widget for displaying output from a running script

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from tkinter import Text
from tkinter.ttk import Frame, Notebook, Scrollbar
from typing import Callable

from automation_menu.ui.components.op_buttons import get_op_buttons
from automation_menu.ui.components.statusbar import get_statusbar
from automation_menu.ui.i18n.widget_for_translation import WidgetForTranslation
from automation_menu.ui.types.op_buttons_ui import OpButtonsUi
from automation_menu.ui.types.status_ui import StatusUi


def get_output_tab( tabcontrol: Notebook, translate_callback: Callable, op_callbacks: dict ) -> tuple[ Frame, Text, OpButtonsUi, StatusUi ]:
    """ Create the output tab used to display script execution output.

    Args:
        tabcontrol (Notebook): Notebook widget to attach the output tab to.
        translate_callback (Callable): Callback used to register widgets for translation.
        op_callbacks (dict): Callbacks invoked by the created
        buttons.

    Returns:
        tuple[Frame, Text]: Created output tab frame and output text widget.
    """

    from automation_menu.utils.localization import _

    output_frame: Frame = Frame( master = tabcontrol , padding = ( 5, 5, 5, 5 ) )
    output_frame.columnconfigure( index = 0, weight = 1 )
    output_frame.columnconfigure( index = 1, weight = 0 )
    output_frame.columnconfigure( index = 2, weight = 0 )
    output_frame.rowconfigure( index = 0, weight = 1 )
    output_frame.rowconfigure( index = 1, weight = 0 )
    output_frame.grid( sticky = 'nswe' )

    tabcontrol.add( child = output_frame, text = _( 'Script output' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = output_frame, default_text = 'Script output' )
    translate_callback( wft )

    output: Text = Text( master = output_frame, wrap = 'word', font = ( 'Calibri', 12 ) )
    output.config( state = 'disabled' )
    output.grid( column = 0, columnspan = 3, row = 0, sticky = 'nswe' )

    scrollbar: Scrollbar = Scrollbar( master = output_frame, orient='vertical', command = output.yview )
    scrollbar.grid( column = 1, row = 0, sticky = 'nse' )
    output.config( yscrollcommand = scrollbar.set )

    op_buttons: OpButtonsUi = get_op_buttons( parent_frame = output_frame, translate_store_callback = translate_callback, op_callbacks = op_callbacks )

    # Create statusbar
    status_widgets: StatusUi = get_statusbar( parent_frame = output_frame )

    return output_frame, output, op_buttons, status_widgets
