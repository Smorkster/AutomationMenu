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

from tkinter import E, N, S, W, Canvas, Event, Scrollbar, Tk
from tkinter.ttk import Button, Frame

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
        self._max_height = 500

        # Button that acts as menu base
        self.menu_button = Button( master = parent, text = text, command = self.show_popup_menu )

        self.popup = tk.Toplevel( parent )

        self._frame = Frame( master = self.popup )
        self._frame.grid( sticky = ( N, S, W, E ) )
        self._frame.grid_columnconfigure( 0, weight = 1 )
        self._frame.grid_columnconfigure( 1, weight = 0 )
        self._frame.grid_rowconfigure( 0, weight = 1 )

        self._canvas = Canvas( master = self._frame, height = self._max_height, highlightthickness = 0 )
        self._canvas.grid( row = 0, column = 0, sticky = ( N, S, W, E ) )

        self._scrollbar = Scrollbar( master = self._frame, orient = 'vertical', command = self._canvas.yview )
        self._scrollbar.grid( row = 0, column = 1, sticky = ( N, S ) )

        self._canvas.configure( yscrollcommand = self._scrollbar.set )

        self._menu_container = Frame( master = self._canvas )
        self._window_id = self._canvas.create_window( ( 0, 0 ), window = self._menu_container, anchor = 'nw' )

        self.popup.withdraw()
        self.popup.overrideredirect( True )  # Remove window decorations
        self.popup.config( relief = 'flat', borderwidth = 2, highlightcolor = "#6F7577", highlightthickness = 2 )

        self.popup.bind( '<Escape>', self.hide_popup_menu )
        self.popup.bind( '<FocusOut>', self.hide_popup_menu )
        self.popup.bind( '<Button-1>', self._check_click_outside )

        self._menu_container.bind( '<Configure>', self._on_container_config )
        self._canvas.bind( '<Configure>', self._on_canvas_config )

        self._create_popup_content()


    def _check_click_outside( self, event: Event ) -> None:
        """ Check if click was outside popup bounds

        Args:
            event (Event): Event that triggered handler
        """

        widget = event.widget.winfo_containing( event.x_root, event.y_root )

        if widget not in [ self.popup ] + list( self.popup.winfo_children() ):
            self.hide_popup_menu()


    def _create_popup_content( self ) -> None:
        """ Create the popup menu content, with tooltips """

        for i, item_info in enumerate( self.exec_list ):
            if isinstance( item_info, ScriptInfo ):
                menu_item = ScriptMenuItem( script_menu = self._menu_container, script_info = item_info, main_object = self.main_object, menu_hide_callback = self.hide_popup_menu )

            else:
                menu_item = SequenceMenuItem( sequence_menu = self._menu_container, sequence = self.exec_list[ item_info ], main_object = self.main_object, menu_hide_callback = self.hide_popup_menu )

            menu_item.menu_button.bind( '<Enter>' , menu_item.on_enter, add = '+' )
            menu_item.menu_button.bind( '<Leave>' , menu_item.on_leave, add = '+' )

            menu_item.menu_button.grid( row = i, column = 0, sticky = ( W, E ), padx = 2, pady = 1 )

        self._menu_container.update_idletasks()
        self._canvas.update_idletasks()
        self.popup.update_idletasks()


    def _on_canvas_config( self, event: Event ) -> None:
        """ Canvas got a resize, set inner window to same size

        Args:
            event (Event): Event that triggered handler
        """

        self._canvas.itemconfig( self._window_id, width = event.width )


    def _on_container_config( self, event: Event ) -> None:
        """ Update scrollregion, clamp height, and toggle scrollbar

        Args:
            event (Event): Event that triggered handler
        """

        self._canvas.configure( scrollregion = self._canvas.bbox( self._window_id ) )

        content_height = event.height
        visible_height = min( content_height, self._max_height )
        self._canvas.configure( height = visible_height )
        self._canvas.configure( width = event.width )

        # Toggle scrollbar visibility
        if content_height > self._max_height:
            self._scrollbar.grid( row = 0, column = 1, sticky = ( N, S ) )

        else:
            self._scrollbar.grid_remove()


    def _on_mousewheel( self, event: Event ) -> None:
        """ Bind mouse wheel scrolling

        Args:
            event (Event): Event that triggered handler
        """

        self._canvas.yview_scroll( int( -1 * ( event.delta / 120 ) ), 'units' )


    def hide_popup_menu( self, *args: Any ) -> None:
        """ Hide the popup menu

        Args:
            args: Any arguments catcher
        """

        self.popup.withdraw()
        self._visible = False


    def rebuild_menu( self, exec_list: dict | list[ ScriptInfo ] ) -> None:
        """ Rebuild the popup menu when the script/sequence list changes

        Args:
            exec_list (dict | list[ ScriptInfo ]): Content to display in menu
        """

        self.exec_list = exec_list

        for c in self._menu_container.winfo_children():
            c.destroy()

        self._create_popup_content()

        self._menu_container.update_idletasks()

        content_width  = self._menu_container.winfo_reqwidth()
        content_height = self._menu_container.winfo_reqheight()

        visible_height = min( content_height, self._max_height )

        self._canvas.configure(
            width = content_width,
            height = visible_height,
            scrollregion = self._canvas.bbox( self._window_id )
        )

        if self._visible:
            self.popup.update_idletasks()
            x = self.menu_button.winfo_rootx()
            y = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()
            self.popup.geometry( f'+{ x }+{ y }' )


    def show_popup_menu( self ) -> None:
        """ Show the popup menu """

        if self._visible:
            self.popup.withdraw()
            self._visible = False

            return

        self._menu_container.update_idletasks()
        self.popup.update_idletasks()

        content_width  = self._menu_container.winfo_reqwidth()
        content_height = self._menu_container.winfo_reqheight()

        visible_height = min( content_height, self._max_height )
        self._canvas.configure( height = visible_height )

        if content_height > self._max_height:
            scrollbar_width = self._scrollbar.winfo_reqwidth() + 10

        else:
            scrollbar_width = 10

        total_width = content_width + scrollbar_width

        self._canvas.itemconfig( self._window_id, width = content_width )
        self._canvas.configure( width = content_width )

        x = self.menu_button.winfo_rootx()
        y = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()

        self.popup.geometry( f'{ total_width }x{ visible_height + 10 }+{ x }+{ y }' )
        self.popup.deiconify()
        self.popup.focus_set()
        self.popup.bind_all( '<MouseWheel>', self._on_mousewheel )

        self._visible = True
