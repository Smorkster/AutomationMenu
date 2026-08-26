"""
Define widget references used by the menu buttons UI.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter.ttk import Button, Frame

from automation_menu.ui.components.custom_menu import CustomMenu


class MenuButtonsUi():
    """ Store widget references used by the menu buttons UI."""

    def __init__( self ) -> None:
        """ Initialize the operation buttons UI widget reference container."""

        pass

    script_menu: CustomMenu
    sequence_menu: CustomMenu

    menu_frame: Frame
