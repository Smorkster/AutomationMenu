"""
Compact launcher window for quickly starting scripts with simple input.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from pathlib import Path
from tkinter import Event, PhotoImage, StringVar, Tk
from tkinter.ttk import Button, Combobox, Entry, Label, Style
from typing import cast

from attr import s

from automation_menu.core.app_context import ApplicationContext
from automation_menu.core.process_execution import ProcessExecution
from automation_menu.models.application_state import ApplicationState
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.ui.styling.config_ui_style import set_ui_style
from automation_menu.utils.app_path_resolver import app_path


class AutomationMiniWindow:
    """ Present a minimal UI for selecting and running available scripts. """

    def __init__( self, app_state: ApplicationState, app_context: ApplicationContext ) -> None:
        """ Initialize the mini launcher window and its widgets.
        
        Args:
            app_state (ApplicationState): State object for application runtime state.
            app_context (ApplicationContext): Context container for managers and shared application objects.
        """

        self._app_state: ApplicationState = app_state
        self._app_context: ApplicationContext = app_context

        self._si: ScriptInfo
        self._input_var: StringVar
        self._input_desc_var: StringVar

        self._init_root()
        self._init_core_widgets()
        self._finalize_window()


    def _btn_click( self ) -> None:
        """ Start the selected script using the entered input string. """

        self._process: ProcessExecution = ProcessExecution( script_info = self._si,
                                                           python_exe_path = self._app_state.python_exe_path,
                                                           on_completion = self._empty_callback,
                                                           on_error = self._empty_callback,
                                                           on_output = self._empty_callback )
        self._input_var.get().split
        self._process.create_process( run_input = self._input_var.get().split(),
                                     persistent = self._si.scriptmeta.persistent_gui or self._si.scriptmeta.persistent_gui_multiple,
                                     monitor_completion = False,
                                     run_state = 'vscode',
                                     mini_runner = True )
        self._clear_input()


    def _center_screen( self ) -> None:
        """ Center the main window on the screen."""

        self.root.update_idletasks()
        width: int = self.root.winfo_width()
        height: int = self.root.winfo_height()

        if width <= 1 or height <= 1:
            self.root.after( 10, self._center_screen )

            return

        frm_width: int = self.root.winfo_rootx() - self.root.winfo_x()
        win_width: int = width + 2 * frm_width

        titlebar_height: int = self.root.winfo_rooty() - self.root.winfo_y()
        win_height: int = height + titlebar_height + frm_width

        x: float = self.root.winfo_screenwidth() // 2 - win_width // 2
        y: float = self.root.winfo_screenheight() // 2 - win_height // 2

        self.root.geometry( newGeometry = f'{ width }x{ height }+{ x }+{ y }' )


    def _clear_input( self ) -> None:
        """ Clear input description and text and reset widgets. """

        self._button.grid( column = 1, row = 0 )
        self._input_var.set( '' )
        self._input.grid_remove()
        self._input_desc_var.set( '' )
        self._input_desc.grid_remove()
        self.root.geometry( '' )


    def _empty_callback( self, *args: str, **kwargs: int ) -> None:
        """ Callback function doing nothing. """

        pass


    def _finalize_window( self ) -> None:
        """ Finalize window layout, bind shortcuts, and start the main event loop."""

        # Shortcuts bindings
        #self.root.bind( '<Escape>', self._on_script_menu_shortcut )

        self._input.grid_remove()

        self.root.deiconify()
        self.root.focus_force()
        self.root.after_idle( self._center_screen )

        icon_path = Path( app_path() ) / 'automation_menu' / 'assets' / 'automation_menu.png'
        self._app_icon = PhotoImage( file = icon_path )
        self.root.after( 0, lambda: self.root.iconphoto( True, self._app_icon ) )

        self.root.mainloop()


    def _init_core_widgets( self ) -> None:
        """ Initialize the main notebook, operation buttons, output tab, and status bar."""

        from automation_menu.utils.localization import _

        self._script_list: Combobox = Combobox( master = self.root,
                                               height = 35,
                                               values = [ si.filename for si in self._app_context.ScriptManager._script_list ] )
        self._script_list.grid( column = 0,
                               row = 0,
                               sticky = 'we' )
        self._script_list.bind( '<<ComboboxSelected>>', self._script_selected )

        self._button: Button = Button( master = self.root,
                                      command = self._btn_click,
                                      text = _( 'Start' ) )
        self._button.grid( column = 1, row = 0 )

        self._input_desc_var = StringVar()
        self._input_desc: Label = Label( master = self.root, textvariable = self._input_desc_var )
        self._input_desc.grid( column = 0, columnspan = 2, row = 1, sticky = 'we' )
        self._input_desc.grid_remove()

        self._input_var = StringVar()
        self._input: Entry = Entry( master = self.root, textvariable = self._input_var )
        self._input.grid( column = 0, columnspan = 2, row = 2, sticky = 'we' )
        self._input.grid_remove()


    def _init_root( self ) -> None:
        """ Create and configure the root Tk window and application styles."""

        # Create main GUI
        self.root: Tk = Tk()
        self.root.withdraw()
        self.root.geometry( '' )

        title_string: str = self._app_state.secrets[ 'mainminiwindowtitle' ]

        if self._app_context.startup_arguments[ 'app_run_state' ].name != 'PROD':
            title_string += f' <{ self._app_context.startup_arguments[ 'app_run_state' ].name }>'

        self.root.title( string = title_string )

        # Setup styles
        self._style: Style = Style()
        set_ui_style( style = self._style )

        self.root.grid_columnconfigure( index = 0, weight = 1 )
        self.root.grid_columnconfigure( index = 1, weight = 0 )
        self.root.grid_rowconfigure( index = 0, weight = 0 )
        self.root.grid_rowconfigure( index = 1, weight = 0 )
        self.root.grid_rowconfigure( index = 2, weight = 0 )
        self.root.grid_rowconfigure( index = 3, weight = 0 )


    def _on_completion( self, *args: str, **kwargs: int ) -> None:
        """ Reset the mini-window input state after a script finishes. """

        self._clear_input()


    def _script_selected( self, event: Event ) -> None:
        """ Script was selected, check if input is wanted.

        Args:
            event (Event): Virutal event triggering this handler
        """

        from automation_menu.utils.localization import _

        script: str = cast( Combobox, event.widget ).get()
        self._si: ScriptInfo = self._app_context.ScriptManager.get_script_info_by_filename( filename = script )
        inputs: list[ str ] = []
        input_desc: str = ''

        if self._si.scriptmeta.has_input_parameters():
            self._input.grid()
            self._input_desc.grid()

            for i in self._si.scriptmeta.script_input_parameters:
                input_desc += f'{ i.name } '

                input_desc += f' { _( 'Type' ) }: { i.type }'

                if i.type == 'bool':
                    input_desc += '[Enter this as is] '

                if len( i.default ) > 0:
                    if i.type == 'bool':
                        inputs.append( f'--{ i.name }')

                    else:
                        input_desc += f' [{ i.default }]'
                        inputs.append( f'--{ i.name } { i.default }' )

                input_desc += f'\n\t{ i.description }\n'

            self._input_desc_var.set( input_desc.strip() )
            self._input_var.set( ' '.join( inputs ) )

            self._button.grid( column = 1, row = 3 )
            self.root.geometry( '' )

        else:
            self._clear_input()