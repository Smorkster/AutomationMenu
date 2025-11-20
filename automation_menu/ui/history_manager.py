"""
Create a Frame widget for displaying execution history

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-08
"""

from datetime import timedelta
from tkinter import END, N, S, W, E, Text, ttk

from automation_menu.models import ExecHistory

#from automation_menu.ui.main_window import AutomationMenuWindow

class HistoryManager:
    def __init__( self ):
        """ Manage execution history items UI widgets for display """
        self._historylist = []


    def _format_duration( self, duration: timedelta ):
        """ Format duration of script execution
        Current format is: x d x h x m x s
        Meanin days, hours, minutes, seconds

        Args:
            duration (timedelta): Time difference between start and finish
        """

        from automation_menu.utils.localization import _

        text_parts = []
        days = duration.days
        hours, remainder = divmod( duration.seconds, 3600 )
        minutes, seconds = divmod( remainder, 60 )

        if days > 0:
            text_parts.append( _( '{d} d' ).format( d = days ) )

        if hours > 0:
            text_parts.append( _( '{h} h' ).format( h = hours ) )

        if minutes > 0:
            text_parts.append( _( '{m} m' ).format( m = minutes ) )

        if seconds > 0:
            text_parts.append( _( '{s} s' ).format( s = seconds ) )

        return " ".join( text_parts )


    def _history_item_selected( self, event ):
        """ Eventhandler for when tree item has been selected """

        from automation_menu.utils.localization import _
        id = event.widget.selection()[ 0 ]

        self.duration.config( state = 'normal' )

        item = [ a for a in self._historylist if a['id'] == id ][ 0 ][ 'item' ]

        self.item_start.config( state = 'normal' )
        self.item_start.delete( '1.0', END )
        self.item_start.insert( 'end', item.start.strftime( '%Y-%m-%d : %H:%M:%S' ) )
        self.item_start.config( state = 'disabled' )

        self.item_end.config( state = 'normal' )
        self.item_end.delete( '1.0', END )
        self.item_end.insert( 'end', item.end.strftime( '%Y-%m-%d : %H:%M:%S' ) )
        self.item_end.config( state = 'disabled' )

        self.duration.config( state = 'normal' )
        self.duration.delete( '1.0', END )
        duration = self._format_duration( duration = ( item.end - item.start ) )
        self.duration.insert( 'end', duration )
        self.duration.config( state = 'disabled' )

        self.item_output.config( state = 'normal' )
        self.item_output.delete( '1.0', END )
        for o in item.output:
            self.item_output.insert( 'end', f'{ str( o ) }\n' )
        self.item_output.config( state = 'disabled' )


    def add_history_item( self, item: ExecHistory ):
        """ Adds a new item to the treewidget, and history list

        Args:
            item (ExecHistory): Execution history to add
        """

        tree_id = self.history_tree.insert( parent = '',
                                 index = 0,
                                 text = f'{ item.start.strftime( '%m / %d : %H:%M:%S' ) }',
                                 values = ( item.script_info.get_attr( 'filename' ) )
                                )

        self._historylist.append( { 'id': tree_id, 'item': item } )


    def get_history_list( self ) -> str:
        """ Summarize execution history list to a string"""

        return [ item[ 'item' ].to_dict() for item in self._historylist ]


    #def get_history_tab( tabcontrol: ttk.Notebook, history_list: list[ ExecHistory ], main_self: AutomationMenuWindow ):
    def get_history_tab( self, tabcontrol: ttk.Notebook, main_self ):
        """ Creates the widgets to display execution history

        Args:
            tabcontrol (ttk.Notebook): A notebook widget to attach the widgets to
            main_self (AutomationMenuWindow): Main window, and object, to make language manager available
        """

        from automation_menu.utils.localization import _

        self.tabHistory = ttk.Frame( tabcontrol )
        self.tabHistory.grid( column = 0, row = 0, sticky = ( N, S, W, E ) )
        self.tabHistory.columnconfigure( index = 0, weight = 0 )
        self.tabHistory.columnconfigure( index = 1, weight = 1 )
        self.tabHistory.rowconfigure( index = 0, weight = 1 )

        self.history_tree = ttk.Treeview( self.tabHistory, columns = ( 'name' ) )
        self.history_tree.heading( '#0', text = _( 'Started' ) )
        self.history_tree.column( '#0', minwidth = 130, width = 130 )
        self.history_tree.heading( 'name', text = _( 'Name' ) )
        self.history_tree.grid( column = 0, rowspan = 3, sticky = ( N, S, W ) )
        self.history_tree.bind( '<<TreeviewSelect>>', self._history_item_selected )

        self.history_item_display = ttk.Frame( self.tabHistory )
        self.history_item_display.grid( column = 1, row = 0, sticky = ( N, S, W, E ) )
        self.history_item_display.columnconfigure( index = 0, weight = 0 )
        self.history_item_display.columnconfigure( index = 1, weight = 1 )
        self.history_item_display.rowconfigure( index = 0, weight = 0 )
        self.history_item_display.rowconfigure( index = 1, weight = 0 )
        self.history_item_display.rowconfigure( index = 2, weight = 0 )
        self.history_item_display.rowconfigure( index = 3, weight = 0 )
        self.history_item_display.rowconfigure( index = 4, weight = 1 )

        item_start_title = ttk.Label( master = self.history_item_display, text = _( 'Started' ), style = 'History.TLabel' )
        item_start_title.grid( column = 0, row = 0, padx = 5, pady = 5, sticky = ( N, W ) )
        main_self.app_context.language_manager.add_translatable_widget( ( item_start_title, 'Started' ) )

        self.item_start = Text( master = self.history_item_display, height = 1, state = 'disabled', font = ( 'Calibri', 12, 'normal' ) )
        self.item_start.grid( column = 1, row = 0, padx = 5, pady = 5, sticky = ( W, E ) )

        item_end_title = ttk.Label( master = self.history_item_display, text = _( 'Ended' ), style = 'History.TLabel' )
        item_end_title.grid( column = 0, row = 1, padx = 5, pady = 5, sticky = ( N, W ) )
        main_self.app_context.language_manager.add_translatable_widget( ( item_end_title, 'Ended' ) )

        self.item_end = Text( master = self.history_item_display, height = 1, state = 'disabled', font = ( 'Calibri', 12, 'normal' ) )
        self.item_end.grid( column = 1, row = 1, padx = 5, pady = 5, sticky = ( W, E ) )

        duration_title = ttk.Label( master = self.history_item_display, text = _( 'Duration' ), style = 'History.TLabel' )
        duration_title.grid( column = 0, row = 2, padx = 5, pady = 5, sticky = ( N, W ) )
        main_self.app_context.language_manager.add_translatable_widget( ( duration_title, 'Duration' ) )

        self.duration = Text( master = self.history_item_display, height = 1, state = 'disabled', font = ( 'Calibri', 12, 'normal' ) )
        self.duration.grid( column = 1, row = 2, padx = 5, pady = 5, sticky = ( W, E ) )

        item_output_title = ttk.Label( master = self.history_item_display, text = _( 'Generated output' ), style = 'History.TLabel' )
        item_output_title.grid( column = 0, columnspan = 2, row = 3, padx = 5, pady = 5, sticky = ( N, W ) )
        main_self.app_context.language_manager.add_translatable_widget( ( item_output_title, 'Generated output' ) )

        self.item_output = Text( master = self.history_item_display, state = 'disabled', font = ( 'Calibri', 12, 'normal' ) )
        self.item_output.grid( column = 0, columnspan = 2, row = 4, padx = 5, pady = 5, sticky = ( N, S, W, E ) )

        return self.tabHistory
