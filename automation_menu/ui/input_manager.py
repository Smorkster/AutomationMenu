"""
Create widgts for each input parameter

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-31
"""

from __future__ import annotations
from typing import TYPE_CHECKING, cast

from automation_menu.models.presetparam import PreSetParam

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext

from tkinter import E, N, S, W, Canvas, Event, StringVar, Tk
from tkinter.ttk import Button, Combobox, Entry, Frame, Label, LabelFrame, Labelframe, Scrollbar, Widget
from typing import Callable

from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.scriptinputparameter import ScriptInputParameter
from automation_menu.models.widget_for_translation import WidgetForTranslation
from automation_menu.utils.language_manager import LanguageManager


class InputManager:
    def __init__( self, root: Tk, language_manager: LanguageManager ) -> None:
        """ Manager class to create, display and retrive data from input widgets

        Args:
            root (Tk): Main window to attach widgets to
            language_manager (LanguageManager): Manager to handle translations/localizations
        """

        self._master_root: Tk = root
        self._language_manager: LanguageManager = language_manager

        self._current_script_info: ScriptInfo
        self._current_frame: Frame | None = None
        self._input_widgets: dict[ str, Button | Canvas | Frame | LabelFrame ] = {}
        self._input_container: Frame
        self._container_canvas: Canvas
        self._input_send_btn: Button
        self._input_frame: LabelFrame
        self._container_window: int

        self._create_input_root()
        self.hide_input_frame()


    def _clear_previous_values( self ) -> None:
        """ Remove any entered input values """

        if not self._current_frame:
            return

        for w in self._current_frame.winfo_children():

            if isinstance( w, Entry ):
                w.delete( 0, 'end' )

            elif isinstance( w, Combobox ):
                w.set( '' )


    def _create_input_root( self ) -> None:
        """ Create root container for input parameters """

        from automation_menu.utils.localization import _

        title_frame: Frame = Frame()
        title_frame.grid_columnconfigure( index = 0, weight = 1 )
        title_frame.grid_columnconfigure( index = 1, weight = 1 )

        frame_title: Label = Label( master = title_frame, style = 'LabelFrameTitle.TLabel', text = _( 'Input parameters for ' ) )
        frame_title.grid( column = 0, row = 0, sticky = 'nw' )

        frame_scriptname: Label = Label( master = title_frame, style = 'LabelFrameTitle.TLabel' )
        frame_scriptname.grid( column = 1, row = 0, sticky = 'nw' )
        self._current_script_name: StringVar = StringVar( master = frame_scriptname )
        frame_scriptname.config( textvariable = self._current_script_name )

        wft: WidgetForTranslation = WidgetForTranslation( widget = frame_title, default_text = 'Input parameters for ' )
        self._language_manager.add_translatable_widget( wft )

        root_input_frame: Labelframe = Labelframe( master = self._master_root, labelwidget = title_frame )
        root_input_frame.grid( column = 0, columnspan = 2, row = 1, sticky = 'nswe' )
        root_input_frame.grid_columnconfigure( index = 0, weight = 1 )
        root_input_frame.grid_columnconfigure( index = 1, weight = 1 )
        root_input_frame.grid_rowconfigure( index = 0, weight = 1 )
        root_input_frame.grid_rowconfigure( index = 1, weight = 0 )

        abort_btn: Button = Button( master = root_input_frame, text = _( 'Abort' ) )
        abort_btn.grid( column = 0, row = 1, sticky = 'sw' )
        abort_btn.config( command = self.hide_input_frame )

        send_input_btn: Button = Button( master = root_input_frame, text = _( 'Send to script' ) )
        send_input_btn.grid( column = 1, row = 1, sticky = 'se' )

        param_list_frame: Frame = Frame( master = root_input_frame, borderwidth = 0.1, relief = 'solid' )
        param_list_frame.grid( column = 0, columnspan = 2, row = 0, sticky = 'nswe' )
        param_list_frame.grid_columnconfigure( index = 0, weight = 1 )
        param_list_frame.grid_columnconfigure( index = 1, weight = 0 )
        param_list_frame.grid_rowconfigure( index = 0, weight = 1 )

        container_canvas: Canvas = Canvas( master = param_list_frame, height = 150, highlightthickness = 0 )
        container_canvas.grid( sticky = 'nswe' )
        container_canvas.grid_columnconfigure( index = 0, weight = 1 )

        container_scrollbar: Scrollbar = Scrollbar( master = param_list_frame, orient = 'vertical', command = container_canvas.yview )
        container_scrollbar.grid( column = 1, row = 0, sticky = 'ns' )

        container_canvas.configure( yscrollcommand = container_scrollbar.set )

        input_container: Frame = Frame( master = container_canvas )
        window_id: int = container_canvas.create_window( ( 0, 0 ), window = input_container, anchor = 'nw' )

        self._container_window = window_id
        self._input_container = input_container
        self._container_canvas = container_canvas
        self._input_send_btn = send_input_btn
        self._input_frame = root_input_frame

        input_container.bind( '<Configure>', self._on_frame_config )
        container_canvas.bind( '<Configure>', self._on_canvas_config )
        container_canvas.bind_all( '<MouseWheel>', self._on_mousewheel )


    def _display_frame( self, param_frame: Frame, script_info: ScriptInfo, submit_input_callback: Callable ) -> None:
        """ Show the input frame for a script

        Args:
            param_frame (Frame): Frame to be displayed
            script_info (ScriptInfo): Script info that will be loaded as current
            submit_input_callback (Callable): Function callback for submitting input data
        """

        self._input_send_btn.config( command = submit_input_callback )

        self._current_frame = param_frame
        self._current_script_info = script_info
        self._script_name_set( script_info.filename )
        self._input_frame.grid()
        self._input_frame.bind_all( '<MouseWheel>' , self._on_mousewheel )


    def _get_or_create_input_frame( self, script_info: ScriptInfo ) -> Frame:
        """ Create (or rebuild) the parameter frame for a script

        Args:
            script_info (ScriptInfo): Script info to build frame for
        """

        return self.create_input_widgets(
            script_info.scriptmeta.script_input_parameters
        )


    def _on_canvas_config( self, event: Event ) -> None:
        """ Update canvas width when canvas window changes

        Args:
            event (Event): Event triggering this handler
        """

        self._container_canvas.itemconfig( self._container_window, width = event.width )


    def _on_frame_config( self, event: Event ) -> None:
        """ Update scrollregion when frame region changes

        Args:
            event (Event): Event triggering this handler
        """

        self._container_canvas.configure( scrollregion = self._container_canvas.bbox( 'all' ) )


    def _on_key_press( self, event: Event ) -> str | None:
        """ Prevent new line characters

        Args:
            event (Event): Event triggering this handler
        """

        if event.keysym == 'Return':

            return 'break'
        
        return


    def _on_keyboard_focus( self, widget: Entry, canvas: Canvas ) -> None:
        """ Focus on entry widget when tabbing

        Args:
            widget (Entry): Entry triggering this handler
            canvas (Canvas): Canvas containing Entry widget
        """

        canvas.update_idletasks()

        param_frame: Frame = cast( Frame, widget.master )
        widget_y: int = param_frame.winfo_y()
        canvas_height: int = canvas.winfo_height()
        bbox: tuple[ int, int, int, int ] = canvas.bbox( 'all' )

        if not bbox:

            return

        total_height: int = bbox[ 3 ] - bbox[ 1 ]

        if total_height <= canvas_height:

            return

        target_y: int = widget_y - 10

        scroll_fraction: float = target_y / total_height
        scroll_fraction: float = max( 0.0, min( 1.0, scroll_fraction ) )

        canvas.yview_moveto( scroll_fraction )


    def _on_mousewheel( self, event: Event ) -> None:
        """ Bind mouse wheel scrolling

        Args:
            event (Event): Event triggering this handler
        """

        self._container_canvas.yview_scroll( int( -1 * ( event.delta / 120 ) ), 'units' )


    def _script_name_set( self, name: str ) -> None:
        """ Set title for input labelframe

        Args:
            name (str): Name of script for current input frame
        """

        self._current_script_name.set( name )


    def collect_entered_input( self, frame_to_search: Frame | None = None ) -> list[ PreSetParam ]:
        """ Collect all entered input

        Args:
            frame_to_search (Frame | None): If provided, a separate frame to search for input

        Returns:
            entered_input (list[ str ]) Entered input as composite list
        """

        entered_input: list[ PreSetParam ] = []

        if self.is_visible() or frame_to_search:

            frame: Frame | None
            if frame_to_search is None:
                frame = self._current_frame

            else:
                frame = frame_to_search

            if frame is None:
                return []

            for widget in [ w for w in frame.winfo_children() ]:
                children = widget.winfo_children()

                if len( children ) < 2:
                    continue

                candidate = children[ 1 ]

                if not isinstance( candidate, ( Combobox, Entry ) ):
                    continue

                input: Combobox | Entry = candidate

                if type( input ) == Combobox:
                    param_text: str = str( input.get() ).strip()

                else:
                    param_text: str = str( input.get() ).strip()

                if str( param_text ).strip() != '':
                    param_name: str = widget.children[ '!label' ].cget( 'text' )

                    entered_input.append( PreSetParam( name = param_name, set = param_text ) )

                #input.delete( 0, 'end' )

        return entered_input


    def create_input_widgets( self, parameters: list[ ScriptInputParameter ], parent: Widget | None = None, pre_set_parameters: list[ PreSetParam ] | None = None ) -> Frame:
        """ Create input widgets for each parameter

        Args:
            parameters (list[ ScriptInputParameter ]): Input parameters asked for by script
            parent (Widget | None): Widget to attach input frame to
            pre_set_parameters (list[ PreSetParam ] | None): List of predefined values for parameters
        """

        from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
        from automation_menu.utils.localization import _

        column_count: int = 0
        number_of_columns: int = 2
        row: int = 0

        if parent:
            # Create a frame for use for sequence step
            input_container: Frame = Frame( master = parent )

        else:
            # Reuse the frame that lives inside the canvas window
            input_container: Frame = self._input_container

        # Clear any old widgets (from previous script)
        for child in input_container.winfo_children():
            child.destroy()

        # Layout config for the grid of parameter frames
        for i in range( number_of_columns ):
            input_container.grid_columnconfigure( index = i, weight = 1, uniform = 'params' )

        for param in parameters:
            parameter_frame: Frame = Frame( master = input_container )
            parameter_frame.grid( column = column_count, row = row, sticky = 'nswe', padx = 2, pady = 2 )
            parameter_frame.grid_columnconfigure( index = 0, weight = 0, uniform = 'name' )
            parameter_frame.grid_columnconfigure( index = 1, weight = 1 )

            param_name: Label = Label( master = parameter_frame, text = param.name, style = 'LabelFrameTitle.TLabel', width = 15 )
            param_name.grid( column = 0, row = 0, sticky = 'nw' )

            param_input: Combobox | Entry
            # Create input widget
            if param.alternatives and len( param.alternatives ) > 0:
                param_input = Combobox(
                    master = parameter_frame,
                    style = 'Input.TCombobox',
                    values = param.alternatives,
                    state = 'readonly'
                )

                if pre_set_parameters and param.name in [ k[ 'name' ] for k in pre_set_parameters ]:
                    param_input.set( next( k for k in pre_set_parameters if k[ 'name' ] == param.name )[ 'set' ] )

            else:
                param_input = Entry(
                    master = parameter_frame,
                    style = 'Input.TEntry'
                )

                if pre_set_parameters and param.name in [ k[ 'name' ] for k in pre_set_parameters ]:
                    param_input.delete( 0, 'end' )
                    param_input.insert( 'end', next( k for k in pre_set_parameters if k[ 'name' ] == param.name )[ 'set' ] )

            param_input.bind(
                '<FocusIn>',
                lambda e, c = self._container_canvas:
                    self._on_keyboard_focus( e.widget, c )
            )
            param_input.bind( '<Key>', self._on_key_press )
            param_input.grid( column = 1, row = 0, padx = 5, pady = 5, sticky = 'nswe' )

            AlwaysOnTopToolTip( widget = param_name, msg = param.description )

            column_count += 1
            if column_count == number_of_columns:
                row += 1
                input_container.grid_rowconfigure( index = row, weight = 1 )
                column_count = 0

        input_container.update_idletasks()

        canvas: Canvas = self._container_canvas
        required_height: int = input_container.winfo_reqheight()
        canvas.configure( height = min( required_height, 150 ) )

        return input_container


    def hide_input_frame( self ) -> None:
        """ Input is done, hide input """

        if self._current_frame:
            self._clear_previous_values()

        if self._input_frame:
            self._input_frame.grid_remove()

        self._current_frame = None


    def is_visible( self ) -> bool:
        """ Is the input frame visible/in use """

        return self._input_frame.winfo_ismapped()


    def show_for_script( self, script_info: ScriptInfo, submit_input_callback: Callable ) -> None:
        """ Show input widgets for assigned script

        Args:
            script_info (ScriptInfo): ScriptInfo for script about to start
            submit_input_callback (Callable): Run function to bind to the submit button
        """

        param_frame: Frame = self._get_or_create_input_frame( script_info = script_info )
        self._display_frame( param_frame = param_frame, script_info = script_info, submit_input_callback = submit_input_callback )
