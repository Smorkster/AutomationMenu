"""
Create widgts for each input parameter

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-31
"""


from tkinter import E, N, S, W, Canvas, StringVar
from tkinter.ttk import Button, Combobox, Entry, Frame, Label, Labelframe, Scrollbar
from typing import Callable

from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.scriptinputparameter import ScriptInputParameter

class InputManager:

    def __init__( self, root, language_manager ):
        self._master_root = root
        self._language_manager = language_manager

        self._cached_input_frames = {}
        self._current_script_info: ScriptInfo = None
        self._current_frame = None
        self._input_widgets = {}

        self._create_input_root()
        self.hide_input_frame()


    def _clear_previous_values( self ) -> None:
        """ Remove any entered input values """

        for w in self._current_frame.winfo_children():

            if isinstance( w, Entry ):
                w.delete( 0, 'end' )

            elif isinstance( w, Combobox ):
                w.set = ''


    #from automation_menu.ui.main_window import AutomationMenuWindow
    #def get_input_widgets( master_self: AutomationMenuWindow ):
    def _create_input_root( self ) -> None:
        """ Create root container for input parameters """

        from automation_menu.utils.localization import _

        title_frame = Frame()
        title_frame.grid_columnconfigure( index = 0, weight = 1 )
        title_frame.grid_columnconfigure( index = 1, weight = 1 )
        frame_title = Label( master = title_frame, style = 'LabelFrameTitle.TLabel', text = _( 'Input parameters for ' ) )
        frame_title.grid( column = 0, row = 0, sticky = ( N, W ) )
        frame_scriptname = Label( master = title_frame, style = 'LabelFrameTitle.TLabel' )
        frame_scriptname.grid( column = 1, row = 0, sticky = ( N, W ) )
        self._current_script_name = StringVar( master = frame_scriptname )
        frame_scriptname.config( textvariable = self._current_script_name )
        self._language_manager.add_translatable_widget( ( frame_title, 'Input parameters for ' ) )

        root_input_frame = Labelframe( master = self._master_root, labelwidget = title_frame )
        root_input_frame.grid( column = 0, columnspan = 2, row = 1, sticky = ( N, S, W, E ) )
        root_input_frame.grid_columnconfigure( index = 0, weight = 1 )
        root_input_frame.grid_rowconfigure( index = 0, weight = 1 )
        root_input_frame.grid_rowconfigure( index = 1, weight = 0 )

        send_input_btn = Button( master = root_input_frame, text = _( 'Send to script' ) )
        send_input_btn.grid( column = 0, columnspan = 2, row = 1, sticky = ( S, E ) )

        param_frame = Frame( master = root_input_frame, borderwidth = 0.1, relief = 'solid' )
        param_frame.grid( column = 0, row = 0, sticky = ( N, S, W, E ) )
        param_frame.grid_columnconfigure( index = 0, weight = 1 )
        param_frame.grid_columnconfigure( index = 1, weight = 0 )

        container_canvas = Canvas( master = param_frame, height = 150, highlightthickness = 0 )
        container_canvas.grid( sticky = ( N, S, W, E ) )
        container_canvas.grid_columnconfigure( index = 0, weight = 1 )
        container_canvas.bind_all( '<MouseWheel>' , self._on_mousewheel )

        container_scrollbar = Scrollbar( master = param_frame, orient = 'vertical', command = container_canvas.yview )
        container_scrollbar.grid( column = 1, row = 0, sticky = ( N, S ) )

        container_canvas.configure( yscrollcommand = container_scrollbar.set )

        self._input_widgets[ 'container_canvas' ] = container_canvas
        self._input_widgets[ 'input_send_btn' ] = send_input_btn
        self._input_widgets[ 'input_frame' ] = root_input_frame


    def _create_input_widgets( self,
                              parameters: list[ ScriptInputParameter ]
                             ) -> Frame:
        """ Create input widgets for each parameter

        Args:
            container_canvas (tk.Canvas): The canvas containing all input widgets
            parameters (): List of parameters to set up
        """

        from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
        from automation_menu.utils.localization import _

        column_count = 0
        number_of_columns = 2
        row = 0

        input_container = Frame( master = self._input_widgets[ 'container_canvas' ] )
        input_container.grid( sticky = ( N, S, W, E ) )
        input_container.bind( '<Configure>', lambda e: self._input_widgets[ 'container_canvas' ].configure( scrollregion = self._input_widgets[ 'container_canvas' ].bbox( 'all' ) ) )

        for i in range( number_of_columns ):
            input_container.grid_columnconfigure( index = i, weight = 1, uniform = 'params' )

        for param in parameters:
            param_frame = Labelframe( master = input_container )
            param_frame.grid( column = column_count, row = row, sticky = ( N, S, W, E ) )
            param_frame.grid_columnconfigure( index = 0, weight = 1 )

            param_title_frame = Frame( master = input_container )
            param_title_frame.grid_columnconfigure( index = 0, weight = 0 )
            param_title_frame.grid_columnconfigure( index = 1, weight = 1 )
            param_name = Label( master = param_title_frame, text = param.name, style = 'LabelFrameTitle.TLabel' )
            param_name.grid( column = 0, row = 0, sticky = ( N, W ) )
            param_desc = Label( master = param_title_frame, text = param.description, style = 'LabelFrameTitleDescription.TLabel' )
            param_desc.grid( column = 1, row = 0, sticky = ( W, E ) )

            param_frame.config( labelwidget = param_title_frame )

            if len( param.alternatives ) > 0:
                param_input = Combobox( master = param_frame, style = 'Input.TCombobox', values = param.alternatives, state = 'readonly' )

            else:
                param_input = Entry( master = param_frame, style = 'Input.TEntry' )

            param_input.bind( '<FocusIn>', lambda e: self._on_keyboard_focus( e.widget, self._input_widgets[ 'container_canvas' ] ) )
            param_input.bind( '<Key>', self._on_key_press )
            param_input.grid( padx = 5, pady = 5, sticky = ( N, S, W, E ) )

            AlwaysOnTopToolTip( widget = param_desc, msg = param.description )

            column_count += 1
            if column_count == number_of_columns:
                row = row + 1
                input_container.grid_rowconfigure( index = row, weight = 1 )
                column_count = 0

        input_container.update_idletasks()

        return input_container


    def _on_key_press( self, event ) -> None:
        """ Prevent new line characters """

        if event.keysym == 'Return':
            return 'break'


    def _on_keyboard_focus( self, widget: Entry, canvas: Canvas ) -> None:
        """ Focus on entry widget when tabbing """

        canvas.update_idletasks()

        param_frame = widget.master
        widget_y = param_frame.winfo_y()
        canvas_height = canvas.winfo_height()
        bbox = canvas.bbox( 'all' )

        if not bbox:
            return

        total_height = bbox[ 3 ] - bbox[ 1 ]

        if total_height <= canvas_height:
            return

        target_y = widget_y - 10

        scroll_fraction = target_y / total_height
        scroll_fraction = max( 0.0, min( 1.0, scroll_fraction ) )

        canvas.yview_moveto( scroll_fraction )


    def _on_mousewheel( self, event ) -> None:
        """ Bind mouse wheel scrolling """

        self._input_widgets[ 'container_canvas' ].yview_scroll( int( -1 * ( event.delta / 120 ) ), 'units' )


    def _script_name_set( self, name: str ) -> None:
        """ Set title for input labelframe """

        self._current_script_name.set( name )


    def collect_entered_input( self ) -> str:
        """ Collect all entered input

        Returns:
            str: Entered input as composite list
        """

        entered_input = []

        if self.is_visible():

            for widget in [ w.winfo_children()[0] for w in self._current_frame.winfo_children() if type(w) == Labelframe ]:
                if type( widget ) == Combobox:
                    param_text = str( widget.get() ).strip()
                else:
                    param_text = str( widget.get() ).strip()

                if str( param_text ).strip() != '':
                    param_name = self._current_frame.nametowidget( widget.master.cget( 'labelwidget' ) ).children[ '!label' ].cget( 'text' )
                    entered_input.append( f'--{ param_name.strip() }' )
                    entered_input.append( param_text )

                widget.delete( 0, 'end' )

        return entered_input


    def hide_input_frame( self ) -> None:
        """ Input is done, hide input """

        if self._current_frame:
            self._clear_previous_values()
            self._current_frame.grid_remove()

        self._input_widgets[ 'input_frame' ].grid_remove()
        self._current_frame = None


    def is_visible( self ) -> bool:
        """ Is the input frame visible/in use """

        return self._input_widgets[ 'input_frame' ].winfo_ismapped()


    def show_for_script( self, script_info: ScriptInfo, submit_input_callback: Callable ) -> None:
        """ Show input widgets for assigned script

        Args:
            script_info (ScriptInfo): ScriptInfo for script about to start
            submit_input_callback (Callable): Run function to bind to the submit button
        """

        if script_info == self._current_script_info and self.is_visible():

            return

        if self._current_frame:
            self._current_frame.grid_remove()

        param_frame = self._get_or_create_input_frame( script_info = script_info )
        self._display_frame( param_frame = param_frame, script_info = script_info, submit_input_callback = submit_input_callback )


    def _get_or_create_input_frame( self, script_info: ScriptInfo ) -> Frame:
        """  """

        if script_info.filename not in self._cached_input_frames:
            param_frame = self._create_input_widgets( script_info.scriptmeta.script_input_parameters )
            self._cached_input_frames[ script_info.filename ] = param_frame

            return param_frame

        param_frame = self._cached_input_frames[ script_info.filename ]
        #self._clear_previous_values()

        return param_frame


    def _display_frame( self, param_frame: Frame, script_info: ScriptInfo, submit_input_callback: Callable ) -> None:
        """  """

        self._input_widgets[ 'input_send_btn' ].config( command = submit_input_callback )
        param_frame.grid()
        self._current_frame = param_frame
        self._current_script_info = script_info
        self._script_name_set( script_info.filename )
        self._input_widgets[ 'input_frame' ].grid()
