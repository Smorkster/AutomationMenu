"""
Control execution-related UI state and interactions.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from __future__ import annotations
from tkinter import END
from tkinter.ttk import Frame
from typing import cast, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.ui.windows.main_window import AutomationMenuWindow

from automation_menu.models.application_state import ApplicationState
from automation_menu.models.enums import OutputStyleTags
from automation_menu.models.geometry import Geometry
from automation_menu.ui.types.exec_button_refs import ExecutionButtonRefs
from automation_menu.ui.types.exec_min_max_refs import ExecutionMinMaxRefs
from automation_menu.ui.types.exec_post_work_refs import ExecutionPostWorkRefs
from automation_menu.ui.types.exec_pre_work_refs import ExecutionPreWorkRefs
from automation_menu.ui.types.exec_refs import ExecRefs
from automation_menu.ui.types.exec_status_refs import ExecutionStatusRefs
from automation_menu.utils.decorators import ui_guard_method


class ExecutionUiController:
    """ Control execution-related UI state before, during, and after script runs."""

    def __init__( self, window: 'AutomationMenuWindow', app_context: ApplicationContext, app_state: ApplicationState, exec_bindings: ExecRefs ) -> None:
        """ Initialize the execution UI controller.

        Args:
            window ('AutomationMenuWindow'): Main application window.
            app_context (ApplicationContext): Shared application context.
            app_state (ApplicationState): Shared application state.
            exec_bindings (ExecRefs): Collected execution-related widget references.

        Raises:
            ValueError: If execution bindings are missing.
        """

        self.app_context = app_context
        self.main_window = window
        self._app_state = app_state

        # Visual execution states
        self._old_window_geometry: Geometry = Geometry()
        self._blink_active: bool = False
        self._blink_job: str = ''
        self._blink_state: bool = False
        self._progressbar_visible: bool = False


        if exec_bindings is None:

            raise ValueError( 'Execution bindings cant be empty' )

        self._pre_work_refs: ExecutionPreWorkRefs = exec_bindings.ExecutionPreWorkRefs
        self._post_work_refs: ExecutionPostWorkRefs = exec_bindings.ExecutionPostWorkRefs
        self._button_refs: ExecutionButtonRefs = exec_bindings.ExecutionButtonRefs
        self._min_max_refs: ExecutionMinMaxRefs = exec_bindings.ExecutionMinMaxRefs
        self._status_refs: ExecutionStatusRefs = exec_bindings.ExecutionStatusRefs


    # region pre/post run
    @ui_guard_method( when_message = 'Doing execution post work' )
    def execution_post_work( self, disable_minimize: bool = False, is_sequence: bool = False ) -> None:
        """ Reset UI state and controls after script or sequence execution.

        Args:
            disable_minimize (bool): Whether minimization is disabled through settings.
            is_sequence (bool): Whether the caller is a sequence.
        """

        self.main_window.disable_pause_script_button()
        self.main_window.disable_stop_script_button()

        if self._app_state.settings.get( 'minimize_on_running' ) and not disable_minimize:
            self.min_max_on_running()

        self._minimize_show_controls()

        if self._app_state.settings.force_focus_post_execution:
            self._post_work_refs.root.focus_force()


    @ui_guard_method( when_message = 'Doing execution pre work' )
    def execution_pre_work( self, disable_minimize: bool = False, is_sequence: bool = False ) -> None:
        """ Prepare UI state and controls before script or sequence execution.

        Args:
            disable_minimize (bool): Whether minimization is disabled through settings.
            is_sequence (bool): Whether the caller is a sequence.
        """

        from automation_menu.utils.localization import _

        self._pre_work_refs.tab_control.select( 0 )
        self._pre_work_refs.textbox_output.config( state = 'normal' )
        self._pre_work_refs.textbox_output.delete( '1.0', END )
        self._pre_work_refs.textbox_output.config( state = 'disabled' )

        self.app_context.InputManager.hide_input_frame()

        if self._app_state.settings.get( 'minimize_on_running' ):
            if disable_minimize:
                self.app_context.OutputQueue.put( {
                    'line': _( 'The script has \'DisableMinimizeOnRunning\', meaning the window will not be minimized.' ),
                    'tag': OutputStyleTags.SYSINFO
                } )

            else:
                self._minimize_hide_controls()
                old_geometry = Geometry( height = self._pre_work_refs.root.winfo_height(),
                                        width = self._pre_work_refs.root.winfo_width(),
                                        x = self._pre_work_refs.root.winfo_x(),
                                        y = self._pre_work_refs.root.winfo_y()
                                        )
                self.min_max_on_running( old_geometry )
    # endregion pre/post run


    # region button execution
    @ui_guard_method( when_message = 'Pausing/resuming execution' )
    def pause_resume_script( self ) -> None:
        """ Pause or resume the currently running script."""

        from automation_menu.utils.localization import _

        if self.app_context.ExecutionManager.is_paused():
            if self.app_context.ExecutionManager.resume_current_script():
                self.app_context.OutputQueue.put( { 'line': _( 'Process was resumed' ),
                                                    'tag': OutputStyleTags.SYSINFO
                                                    } )
                self._button_refs.btnPauseResumeScript.config( text = _( 'Pause' ) )

                self._blink_active = False
                self.stop_pause_button_blinking()

        else:
            if self.app_context.ExecutionManager.pause_current_script():
                self.app_context.OutputQueue.put( { 'line': _( 'Process was paused' ),
                                                    'tag': OutputStyleTags.SYSINFO
                                                    } )
                self._button_refs.btnPauseResumeScript.config( text = _( 'Resume' ) )
                self._blink_active = True
                self.pause_button_blinking()


    @ui_guard_method( when_message = 'Pausing button blinking' )
    def pause_button_blinking( self ) -> None:
        """ Start or continue the blinking effect for the pause button."""

        if not self._blink_active:

            return

        self._blink_state = not self._blink_state

        self._button_refs.root.after( 100, lambda: self._button_refs.btnPauseResumeScript.config( style = 'BlinkBg.TButton' if self._blink_state else 'TButton' ) )

        self._blink_job = self.main_window.root.after( 600, self.pause_button_blinking )


    @ui_guard_method( when_message = 'Stopping script' )
    def stop_script( self ) -> None:
        """ Stop the currently running script."""

        self.app_context.ExecutionManager.stop_current_script()
        self.stop_pause_button_blinking()


    @ui_guard_method( when_message = 'Stopping blinking of pause button' )
    def stop_pause_button_blinking( self ) -> None:
        """ Stop the blinking effect for the pause button."""

        self._blink_active = False

        if self._blink_job:
            self._button_refs.root.after_cancel( self._blink_job )
            self._blink_job = ''
    # endregion button execution


    # region min/max execution
    @ui_guard_method( when_message = 'Down-/resizing window before/after script execution' )
    def min_max_on_running( self, old_geometry: Geometry | None = None ) -> None:
        """ Resize or restore the main window during script execution.

        Args:
            old_geometry (Geometry | None): Main window geometry before script execution.
        """

        win_width: int = 400
        win_height: int = 200

        if old_geometry:
            self._old_window_geometry = old_geometry
            self._minimize_hide_controls()
            self._min_max_refs.root.geometry( newGeometry = f'{ win_width }x{ win_height }+{ self._min_max_refs.root.winfo_screenwidth() - win_width  }+{ self._min_max_refs.root.winfo_screenheight() - win_height - 100 }' )

        else:
            self._min_max_refs.root.geometry( newGeometry = self._old_window_geometry.to_string() )
            self._minimize_show_controls()

        self._min_max_refs.root.update_idletasks()


    def _minimize_hide_controls( self ) -> None:
        """ Hide UI controls while the window is minimized during execution."""

        self._min_max_refs.tab_control.config( style = 'HiddenTabs.TNotebook' )
        self._min_max_refs.status_ui.separator.grid_remove()
        self._min_max_refs.status_ui.text_status.grid_remove()
        self._min_max_refs.status_ui.status_bar.grid_remove()
        self._min_max_refs.status_ui.status_bar.grid_columnconfigure( index = 0, weight = 0 )
        self._min_max_refs.status_ui.status_bar.grid_columnconfigure( index = 1, weight = 0 )

        self._min_max_refs.op_buttons.menu_frame.grid_remove()
        self._min_max_refs.op_buttons.btn_continue_breakpoint.config( style = 'RunningSmall.TButton' )
        self._min_max_refs.op_buttons.btn_stop_script.config( style = 'RunningSmall.TButton' )
        self._min_max_refs.op_buttons.btn_pause_resume_script.config( style = 'RunningSmall.TButton' )

        self._min_max_refs.status_ui.progressbar.config( style = 'RunningSmall.TProgressbar' )

        self._min_max_refs.root.overrideredirect( True )  # Remove window decorations


    def _minimize_show_controls( self ) -> None:
        """ Show previously hidden UI controls after execution finishes."""

        self._min_max_refs.tab_control.config( style = self.main_window.tab_style )
        self._min_max_refs.status_ui.status_bar.grid()
        self._min_max_refs.status_ui.separator.grid()
        self._min_max_refs.status_ui.text_status.grid()
        self._min_max_refs.status_ui.status_bar.grid_columnconfigure( index = 0, weight = 1 )
        self._min_max_refs.status_ui.status_bar.grid_columnconfigure( index = 1, weight = 0 )

        self._min_max_refs.op_buttons.menu_frame.grid()
        self._min_max_refs.op_buttons.btn_continue_breakpoint.config( style = 'TButton' )
        self._min_max_refs.op_buttons.btn_stop_script.config( style = 'TButton' )
        self._min_max_refs.op_buttons.btn_pause_resume_script.config( style = 'TButton' )

        self._min_max_refs.status_ui.progressbar.config( style = 'TProgressbar' )

        self._min_max_refs.root.overrideredirect( False )  # Reapply window decorations
    # endregion min/max execution


    # region status execution
    @ui_guard_method( when_message = 'API hide progressbar' )
    def hide_progress( self, *args: Tuple ) -> None:
        """ Hide the execution progress bar.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        if self._progressbar_visible:
            self._status_refs.progressbar.grid_remove()
            self._status_refs.separator.grid_remove()
            self._progressbar_visible = False


    @ui_guard_method( when_message = 'API show progressbar' )
    def show_progress( self, *args: Tuple ) -> None:
        """ Show the execution progress bar.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        if not self._progressbar_visible:
            self._status_refs.progressbar.grid()
            self._progressbar_visible = True


    @ui_guard_method( when_message = 'API set progressbar determinate' )
    def set_progress_determined( self, *args: Tuple ) -> None:
        """ Set the progress bar to determinate mode.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        if not self._status_refs.progressbar.winfo_ismapped():
            self._status_refs.progressbar.grid()

        self._status_refs.progressbar.config( mode = 'determinate' )
        self._status_refs.progressbar.stop()


    @ui_guard_method( when_message = 'API set progressbar indeterminate' )
    def set_progress_indetermined( self, *args: Tuple ) -> None:
        """ Set the progress bar to indeterminate mode.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        if not self._status_refs.progressbar.winfo_ismapped():
            self._status_refs.progressbar.grid()

        self._status_refs.progressbar.start( interval = 10 )
        self._status_refs.progressbar.config( mode = 'indeterminate' )


    @ui_guard_method( when_message = 'API update progressbar' )
    def update_progress( self, update_data: float | int | dict ) -> None:
        """ Update the progress bar value.

        Args:
            update_data (float | int | dict): Precalculated value or payload used to update the progress bar.
        """

        new_percentage = 0

        if not self._status_refs.progressbar.master.winfo_ismapped():
            cast( Frame, self._status_refs.progressbar.master ).grid()

        if not self._status_refs.progressbar.winfo_ismapped():
            self._status_refs.progressbar.grid()

        if isinstance( update_data, ( float, int ) ):
            if update_data >= 100:
                new_percentage = 99.99999999999

            else:
                new_percentage = update_data

        else:
            if update_data[ 'percent' ] >= 100:
                new_percentage = 99.99999999999

            else:
                new_percentage = update_data[ 'percent' ]

        if not self._progressbar_visible:
            self.show_progress()

        self._status_refs.progressbar.config( value = new_percentage )


    @ui_guard_method( when_message = 'API clear status' )
    def clear_status( self, *args: Tuple ) -> None:
        """ Clear all status text.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        self._status_refs.text_status.config( text = '' )


    @ui_guard_method( when_message = 'API get status' )
    def get_status( self, *args: Tuple ) -> None:
        """ Send the current status text back to the active runner.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        runner = self.app_context.ExecutionManager.current_runner

        if runner is None:
            return

        status = self._status_refs.text_status.cget( 'text' )
        self._status_refs.root.after( 10, lambda: runner.send_api_response( response = status ) )


    @ui_guard_method( when_message = 'API get status' )
    def set_status( self, set_data: dict ) -> None:
        """ Set the displayed status text.

        Args:
            set_data (dict): Dictionary describing the status text to set.
        """

        text: str = ''

        if set_data.get( 'append' ):
            text = self._status_refs.text_status.cget( 'text' ) + set_data[ 'set' ]

        else:
            text = set_data[ 'set' ]

        text = text.replace( '\r\n', ' ' )
        self._status_refs.text_status.config( text = text )
    # endregion status execution
