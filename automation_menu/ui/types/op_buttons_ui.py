"""
Define widget references used by the operation buttons UI.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter.ttk import Button, Frame

from automation_menu.ui.components.custom_menu import CustomMenu


class OpButtonsUi():
    """ Store widget references used by the operation buttons UI."""

    def __init__( self ) -> None:
        """ Initialize the operation buttons UI widget reference container."""

        pass

    btn_continue_breakpoint: Button
    btn_stop_script: Button
    btn_pause_resume_script: Button

    script_menu: CustomMenu
    sequence_menu: CustomMenu

    op_buttons_frame: Frame
    menu_frame: Frame
