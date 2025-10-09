"""
Create a Frame widget for displaying execution history

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-08
"""

from tkinter import N, S, W, E, Text, ttk

from automation_menu.models import ExecHistory
#from automation_menu.ui.main_window import AutomationMenuWindow


#def get_history_tab( tabcontrol: ttk.Notebook, history_list: list[ ExecHistory ], main_self: AutomationMenuWindow ):
def get_history_tab( tabcontrol: ttk.Notebook, history_list: list[ ExecHistory ], main_self ):
    """  """

    from automation_menu.utils.localization import _

    tabHistory = ttk.Frame( tabcontrol )
    tabHistory.grid( column = 0, row = 0, sticky = ( N, S, W, E ) )
    tabHistory.columnconfigure( index = 0, weight = 0 )
    tabHistory.columnconfigure( index = 1, weight = 1 )
    tabHistory.rowconfigure( index = 0, weight = 1 )

    history_tree = ttk.Treeview( tabHistory )
    history_tree.grid( column = 0, rowspan = 3, sticky = ( N, S, W ) )

    history_item_display = ttk.Frame( tabHistory )
    history_item_display.grid( column = 1, row = 0, sticky = ( N, S, W, E ) )
    history_item_display.columnconfigure( index = 0, weight = 0 )
    history_item_display.columnconfigure( index = 1, weight = 1 )
    history_item_display.rowconfigure( index = 0, weight = 0 )
    history_item_display.rowconfigure( index = 1, weight = 0 )
    history_item_display.rowconfigure( index = 2, weight = 0 )
    history_item_display.rowconfigure( index = 3, weight = 1 )

    item_start_title = ttk.Label( master = history_item_display, text = _( 'Started' ) )
    item_start_title.grid( column = 0, row = 0, padx = 5, pady = 5, sticky = ( N, W ) )
    main_self.language_manager.add_translatable_widget( ( item_start_title, 'Started' ) )

    item_start = Text( master = history_item_display, height = 1, state = 'disabled' )
    item_start.grid( column = 1, row = 0, padx = 5, pady = 5, sticky = ( W, E ) )

    item_end_title = ttk.Label( master = history_item_display, text = _( 'Ended' ) )
    item_end_title.grid( column = 0, row = 1, padx = 5, pady = 5, sticky = ( N, W ) )
    main_self.language_manager.add_translatable_widget( ( item_end_title, 'Ended' ) )

    item_end = Text( master = history_item_display, height = 1, state = 'disabled' )
    item_end.grid( column = 1, row = 1, padx = 5, pady = 5, sticky = ( W, E ) )

    item_output_title = ttk.Label( master = history_item_display, text = _( 'Generated output' ) )
    item_output_title.grid( column = 0, columnspan = 2, row = 2, padx = 5, pady = 5, sticky = ( N, W ) )
    main_self.language_manager.add_translatable_widget( ( item_output_title, 'Generated output' ) )

    item_output = Text( master = history_item_display, state = 'disabled' )
    item_output.grid( column = 0, columnspan = 2, row = 3, padx = 5, pady = 5, sticky = ( N, S, W, E ) )

    return tabHistory
