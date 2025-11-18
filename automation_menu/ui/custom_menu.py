"""
Creates a custom simple menu, based on a button and popup window

Author: Smorkster
GitHub:
License: MIT
Version: 1.0.0
Created: 2025-09-25
"""

import tkinter as tk
from tkinter import E, W, Tk, ttk

from automation_menu.core.script_menu_item import ScriptMenuItem
from automation_menu.models import ScriptInfo


class CustomMenu:
    def __init__( self, parent: Tk, text: str, scripts: list[ ScriptInfo ], main_object ):
        """ Create a custom meny of a button, a window and labels for each menuitem

        Args:
            parent (Tk): The parent window/widget to attach the button to
            text (str): String to display in the button
            scripts (list[ ScriptInfo ]): A list of items to be displayed in the menu
            main_object (AutomationMenuWindow): The main object, is used in each menuitem
        """

        self.parent = parent
        self.scripts = scripts
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


    def _check_click_outside( self, event ):
        """ Check if click was outside popup bounds """

        widget = event.widget.winfo_containing( event.x_root, event.y_root )

        if widget not in [ self.popup ] + list( self.popup.winfo_children() ):
            self.hide_popup_menu()


    def _create_popup_content( self ):
        """ Create the popup menu content, with tooltips """

        for i, script_info in enumerate( self.scripts ):
            script_object = ScriptMenuItem( script_menu = self.popup, script_info = script_info, main_object = self.main_object )
            script_object.script_button.bind( '<Enter>' , script_object.on_enter )
            script_object.script_button.bind( '<Leave>' , script_object.on_leave )

            script_object.script_button.grid( row = i, column = 0, sticky = ( W, E ), padx = 2, pady = 1 )


    def show_popup_menu( self ):
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


    def hide_popup_menu( self, *args ) -> None:
        """ Hide the popup menu """

        self.popup.withdraw()
        self._visible = False
