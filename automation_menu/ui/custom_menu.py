"""
Creates a custom simple menu, based on a button and popup window

Author: Smorkster
GitHub:
License: MIT
Version: 1.0.0
Created: 2025-09-25
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from automation_menu.ui.main_window import AutomationMenuWindow

import tkinter as tk

from tkinter import E, W, Event, Tk, ttk

from automation_menu.core.sequence_menu_item import SequenceMenuItem
from automation_menu.core.script_menu_item import ScriptMenuItem
from automation_menu.models import ScriptInfo


class CustomMenu:
    def __init__( self, parent: Tk, text: str, exec_list: list[ ScriptInfo ], main_object: AutomationMenuWindow ) -> None:
        """ Create a custom meny as a button. This launches a separatewindow
        containing clickable labels for each menuitem

        Args:
            parent (Tk): The parent window/widget to attach the button to
            text (str): String to display in the button
            scripts (list[ ScriptInfo ]): A list of items to be displayed in the menu
            main_object (AutomationMenuWindow): The main object, is used in each menuitem
        """

        self.parent = parent
        self.exec_list = exec_list
        self.main_object = main_object
        self._visible = False

        # Create button that looks like a menu
        self.menu_button = ttk.Button(
            parent, 
            text = text,
            command = self.show_popup_menu
        )

        self.popup = tk.Toplevel( parent )
        self.popup.withdraw()
        self.popup.overrideredirect( True )  # Remove window decorations
        self.popup.config( relief = 'flat', borderwidth = 2, highlightcolor = '#909597', highlightthickness = 2 )

        self.popup.bind( '<Escape>', self.hide_popup_menu )
        self.popup.bind( '<FocusOut>', self.hide_popup_menu )
        self.popup.bind( '<Button-1>', self._check_click_outside )

        self._create_popup_content()


    def _check_click_outside( self, event: Event ) -> None:
        """ Check if click was outside popup bounds """

        widget = event.widget.winfo_containing( event.x_root, event.y_root )

        if widget not in [ self.popup ] + list( self.popup.winfo_children() ):
            self.hide_popup_menu()


    def _create_popup_content( self ) -> None:
        """ Create the popup menu content, with tooltips """

        for i, item_info in enumerate( self.exec_list ):
            if isinstance( item_info, ScriptInfo ):
                menu_object = ScriptMenuItem( script_menu = self.popup, script_info = item_info, main_object = self.main_object )

            else:
                menu_object = SequenceMenuItem( sequence_menu = self.popup, sequence = item_info, main_object = self.main_object )

            menu_object.menu_button.bind( '<Enter>' , menu_object.on_enter )
            menu_object.menu_button.bind( '<Leave>' , menu_object.on_leave )

            menu_object.menu_button.grid( row = i, column = 0, sticky = ( W, E ), padx = 2, pady = 1 )


    def hide_popup_menu( self, *args: Any ) -> None:
        """ Hide the popup menu """

        self.popup.withdraw()
        self._visible = False


    def show_popup_menu( self ) -> None:
        """ Show the popup menu """

        if self._visible:
            self.popup.withdraw()
            self._visible = False

        else:
            # Position popup below the button
            x = self.menu_button.winfo_rootx()
            y = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()

            self.popup.geometry( f'+{ x }+{ y }' )
            self.popup.deiconify() # Show popup

            self.popup.focus_set()
            self._visible = True
