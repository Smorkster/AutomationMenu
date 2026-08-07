"""
Create widgts for each input parameter

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from functools import partial
from tkinter import Canvas, Tk
from tkinter.ttk import Frame
from typing import Callable

from automation_menu.models.presetparam import PreSetParam
from automation_menu.models.script_input_argument import InputArgument
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.scriptinputparameter import ScriptInputParameter
from automation_menu.ui.components.script_input_form import clear_previous_values, collect_entered_input, create_input_widgets
from automation_menu.ui.panels.script_input_panel import create_input_root, on_canvas_config, on_frame_config, on_mousewheel, script_name_set
from automation_menu.ui.types.input_ui import InputUi
from automation_menu.ui.i18n.language_manager import LanguageManager


class InputManager:
    """ Manage creation, display, and collection of script input widgets."""

    def __init__( self, root: Tk, language_manager: LanguageManager ) -> None:
        """ Initialize the input manager.

        Args:
            root (Tk): Main window to attach widgets to.
            language_manager (LanguageManager): Manager used to handle translations and localization.
        """

        self._language_manager: LanguageManager = language_manager

        self._current_script_info: ScriptInfo
        self._current_frame: Frame | None = None

        self._input_widgets: InputUi = create_input_root( add_translate_callback = language_manager.add_translatable_widget, parent= root )
        self._input_widgets.abort_btn.config( command = self.hide_input_frame )
        self._input_widgets.input_container.bind( '<Configure>', partial( on_frame_config, self._input_widgets ) )
        self._input_widgets.container_canvas.bind( '<Configure>', partial( on_canvas_config, self._input_widgets ) )
        self._input_widgets.container_canvas.bind_all( '<MouseWheel>', partial( on_mousewheel, self._input_widgets ) )

        self.hide_input_frame()


    def _display_frame( self, param_frame: Frame, script_info: ScriptInfo, submit_input_callback: Callable ) -> None:
        """ Display the input frame for a script.

        Args:
            param_frame (Frame): Frame to display.
            script_info (ScriptInfo): Script info to load as current.
            submit_input_callback (Callable): Callback used to submit entered input data.
        """

        self._input_widgets.send_input_btn.config( command = submit_input_callback )

        self._current_frame = param_frame
        self._current_script_info = script_info
        script_name_set( ui = self._input_widgets, name = script_info.filename )
        self._input_widgets.root_input_frame.grid()
        self._input_widgets.root_input_frame.bind_all( '<MouseWheel>' , partial( on_mousewheel, self._input_widgets ) )


    def _get_or_create_input_frame( self, script_info: ScriptInfo ) -> Frame:
        """ Create or rebuild the parameter input frame for a script.

        Args:
            script_info (ScriptInfo): Script info to build the input frame for.

        Returns:
            Frame: Created parameter input frame.
        """

        return create_input_widgets( parameters = script_info.scriptmeta.script_input_parameters,
                                    container = self._input_widgets.input_container,
                                    pre_set_parameters = None,
                                    canvas = self._input_widgets.container_canvas )


    def collect_entered_input( self, frame_to_search: Frame | None = None ) -> list[ InputArgument ]:
        """ Collect entered input values from a frame.

        Args:
            frame_to_search (Frame | None): Specific frame to search for input values. If not provided, the current visible input frame is used.

        Returns:
            list[ InputArgument ]: Entered input values as preset parameters.
        """

        if frame_to_search is not None:

            return collect_entered_input( frame_to_search = frame_to_search )

        if not self.is_visible() or self._current_frame is None:

            return []

        return collect_entered_input( self._current_frame )


    def hide_input_frame( self ) -> None:
        """ Hide the input frame and clear any entered values."""

        if self._current_frame:
            clear_previous_values( input_frame = self._current_frame )

        if self._input_widgets.root_input_frame:
            self._input_widgets.root_input_frame.grid_remove()

        self._current_frame = None


    def is_visible( self ) -> bool:
        """ Check whether the input frame is currently visible.

        Returns:
            bool: True if the input frame is visible, otherwise False.
        """

        return self._input_widgets.root_input_frame.winfo_ismapped()


    def show_for_step( self, parameters: list[ ScriptInputParameter ],
                      container: Frame,
                      pre_set_parameters: list[ PreSetParam ],
                      canvas: Canvas ) -> Frame:
        """ Create input widgets for a sequence step.

        Args:
            parameters (list[ScriptInputParameter]): Input parameters to build widgets for.
            container (Frame): Frame to attach the input widgets to.
            pre_set_parameters (list[PreSetParam]): Predefined parameter values to populate.
            canvas (Canvas): Canvas containing the input widgets.

        Returns:
            Frame: Frame containing the created input widgets.
        """

        return create_input_widgets( parameters = parameters,
                                    container = container,
                                    pre_set_parameters = pre_set_parameters,
                                    canvas = canvas )


    def show_for_script( self, script_info: ScriptInfo, submit_input_callback: Callable ) -> None:
        """ Show input widgets for a script.

        Args:
            script_info (ScriptInfo): Script info for the script about to start.
            submit_input_callback (Callable): Callback bound to the submit button.
        """

        param_frame: Frame = self._get_or_create_input_frame( script_info = script_info )
        self._display_frame( param_frame = param_frame,
                            script_info = script_info,
                            submit_input_callback = submit_input_callback )
