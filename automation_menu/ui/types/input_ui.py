"""
Define widget references used by the script input UI.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter import Canvas, StringVar
from tkinter.ttk import Button, Frame, Label, Labelframe, Scrollbar


class InputUi():
    """ Store widget references used by the script input UI."""

    def __init__( self ) -> None:
        """ Initialize the script input UI widget reference container."""

        pass

    window_id: int

    current_script_name: StringVar

    abort_btn: Button
    send_input_btn: Button

    container_canvas: Canvas

    input_container: Frame
    param_list_frame: Frame
    title_frame: Frame

    frame_scriptname: Label
    frame_title: Label

    root_input_frame: Labelframe

    container_scrollbar: Scrollbar
