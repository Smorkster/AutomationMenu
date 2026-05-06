"""
Creates a custom simple menu, based on a button and popup window

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from tkinter import Canvas, Event, Misc, Scrollbar, Toplevel
from tkinter.ttk import Button, Frame

if TYPE_CHECKING:
    from automation_menu.ui.windows.main_window import AutomationMenuWindow

from automation_menu.core.sequence_menu_item import SequenceMenuItem
from automation_menu.core.script_menu_item import ScriptMenuItem
from automation_menu.models import ScriptInfo
from automation_menu.models.sequence import Sequence


class CustomMenu:
    """ Create and manage a custom popup menu for scripts or sequences."""

    def __init__( self, parent: Frame, text: str, exec_list: dict[ str, Sequence ] | list[ ScriptInfo ], main_object: AutomationMenuWindow ) -> None:
        """ Initialize a custom popup menu button and popup window.

        Args:
            parent (Frame): Parent widget to attach the menu button to.
            text (str): Text to display on the menu button.
            exec_list (dict[str, Sequence] | list[ScriptInfo]): Items to display in the popup menu.
            main_object (AutomationMenuWindow): Main window object used by menu items.
        """

        self.parent: Frame = parent
        self.exec_list: dict[ str, Sequence ] | list[ ScriptInfo ] = exec_list
        self.main_object: AutomationMenuWindow = main_object

        self._max_height: int = 500
        self._skip_next_open:bool = False
        self._visible: bool = False

        # Button that acts as menu base
        self.menu_button: Button = Button( master = parent, text = text, command = self.show_popup_menu )

        self.popup: Toplevel = Toplevel( parent )

        self._frame: Frame = Frame( master = self.popup )
        self._frame.grid( sticky = 'nswe' )
        self._frame.grid_columnconfigure( 0, weight = 1 )
        self._frame.grid_columnconfigure( 1, weight = 0 )
        self._frame.grid_rowconfigure( 0, weight = 1 )

        self._canvas: Canvas = Canvas( master = self._frame, height = self._max_height, highlightthickness = 0 )
        self._canvas.grid( row = 0, column = 0, sticky = 'nswe' )

        self._scrollbar: Scrollbar = Scrollbar( master = self._frame, orient = 'vertical', command = self._canvas.yview )
        self._scrollbar.grid( row = 0, column = 1, sticky = 'ns' )

        self._canvas.configure( yscrollcommand = self._scrollbar.set )

        self._menu_container: Frame = Frame( master = self._canvas )
        self._window_id: int = self._canvas.create_window( ( 0, 0 ), window = self._menu_container, anchor = 'nw' )

        self.popup.withdraw()
        self.popup.overrideredirect( True )  # Remove window decorations
        self.popup.config( relief = 'flat', borderwidth = 2, highlightcolor = "#6F7577", highlightthickness = 2 )

        self.popup.bind( '<Escape>', self._on_escape_popup )
        self.popup.bind( '<FocusOut>', self._on_popup_focus_set )
        self.popup.bind( '<Button-1>', self._check_click_outside )

        self._menu_container.bind( '<Configure>', self._on_container_config )
        self._canvas.bind( '<Configure>', self._on_canvas_config )


    def _check_click_outside( self, event: Event ) -> None:
        """ Hide the popup menu if a click occurs outside its bounds.

        Args:
            event (Event): Event that triggered the handler.
        """

        widget: Misc | None = event.widget.winfo_containing( event.x_root, event.y_root )

        if widget not in [ self.popup ] + list( self.popup.winfo_children() ):
            self.hide_popup_menu()


    def _create_popup_content( self ) -> None:
        """ Create the popup menu content and bind menu item hover handlers."""

        items: list[ ScriptInfo ] | list[ Sequence ]

        if isinstance( self.exec_list, dict ):
            items = list( self.exec_list.values() )

        else:
            items = self.exec_list

        for i, item_info in enumerate( items ):
            menu_item: SequenceMenuItem | ScriptMenuItem | None = None

            if isinstance( item_info, ScriptInfo ):
                menu_item = ScriptMenuItem( script_menu = self._menu_container, script_info = item_info, main_object = self.main_object, menu_hide_callback = self.hide_popup_menu )

            else:
                menu_item = SequenceMenuItem( sequence_menu = self._menu_container, sequence = item_info, main_object = self.main_object, menu_hide_callback = self.hide_popup_menu )

            menu_item.menu_button.bind( '<Enter>' , menu_item.on_enter, add = '+' )
            menu_item.menu_button.bind( '<Leave>' , menu_item.on_leave, add = '+' )

            menu_item.menu_button.grid( row = i, column = 0, sticky = 'we', padx = 2, pady = 1 )

        self.popup.update_idletasks()


    def _on_canvas_config( self, event: Event ) -> None:
        """ Resize the inner popup window to match the canvas width.

        Args:
            event (Event): Event that triggered the handler.
        """

        self._canvas.itemconfig( self._window_id, width = event.width )


    def _on_container_config( self, event: Event ) -> None:
        """ Update popup scroll region, visible size, and scrollbar state.

        Args:
            event (Event): Event that triggered the handler.
        """

        self._canvas.configure( scrollregion = self._canvas.bbox( self._window_id ) )

        content_height: int = event.height
        visible_height: int = min( content_height, self._max_height )
        self._canvas.configure( height = visible_height )
        self._canvas.configure( width = event.width )

        # Toggle scrollbar visibility
        if content_height > self._max_height:
            self._scrollbar.grid( row = 0, column = 1, sticky = 'ns' )

        else:
            self._scrollbar.grid_remove()


    def _on_escape_popup( self, event: Event ) -> str:
        """ Handle Escape key presses while the popup menu is open.

        Args:
            event (Event): Event that triggered the handler.

        Returns:
            (str): Tkinter event handling instruction string.
        """

        if not self._visible:

            return 'break'

        self.hide_popup_menu()
        self.menu_button.focus_set()

        return 'break'


    def _on_mousewheel( self, event: Event ) -> None:
        """ Scroll the popup menu content with the mouse wheel.

        Args:
            event (Event): Event that triggered the handler.
        """

        self._canvas.yview_scroll( int( -1 * ( event.delta / 120 ) ), 'units' )


    def _on_popup_focus_set( self, event: Event ) -> None:
        """ Handle the popup menu losing focus.

        Args:
            event (Event): Event that triggered the handler.
        """

        if not self._visible:

            return

        widget = self.parent.winfo_containing(
            self.parent.winfo_pointerx(),
            self.parent.winfo_pointery()
        )

        self._skip_next_open = widget is self.menu_button
        self.hide_popup_menu()


    def hide_popup_menu( self, *args: Any ) -> None:
        """ Hide the popup menu.

        Args:
            args (Any): Unused positional arguments accepted by the handler.
        """

        self.popup.withdraw()
        self.popup.unbind_all( '<MouseWheel>' )
        self._visible = False


    def rebuild_menu( self, exec_list: dict[ str, Sequence ] | list[ ScriptInfo ] ) -> None:
        """ Rebuild the popup menu when the displayed items change.

        Args:
            exec_list (dict[str, Sequence] | list[ScriptInfo]): Content to display in the menu.
        """

        self.exec_list: dict[ str, Sequence ] | list[ ScriptInfo ] = exec_list

        for c in self._menu_container.winfo_children():
            c.destroy()

        self._create_popup_content()

        content_width: int = self._menu_container.winfo_reqwidth()
        content_height: int = self._menu_container.winfo_reqheight()

        visible_height: int = min( content_height, self._max_height )

        self._canvas.configure(
            width = content_width,
            height = visible_height,
            scrollregion = self._canvas.bbox( self._window_id )
        )

        if self._visible:
            self.popup.update_idletasks()
            x: int = self.menu_button.winfo_rootx()
            y: int = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()
            self.popup.geometry( f'+{ x }+{ y }' )


    def show_popup_menu( self ) -> None:
        """ Show the popup menu and position it below the menu button."""

        if self._skip_next_open:
            self._skip_next_open = False

            return

        if self._visible:
            self.hide_popup_menu()

            return

        if len( self._menu_container.winfo_children() ) == 0:
            self._create_popup_content()

        content_width: int = self._menu_container.winfo_reqwidth()
        content_height: int = self._menu_container.winfo_reqheight()

        visible_height: int = min( content_height, self._max_height )
        self._canvas.configure( height = visible_height )

        if content_height > self._max_height:
            scrollbar_width: int = self._scrollbar.winfo_reqwidth() + 10

        else:
            scrollbar_width: int = 10

        total_width: int = content_width + scrollbar_width

        self._canvas.itemconfig( self._window_id, width = content_width )
        self._canvas.configure( width = content_width )

        x: int = self.menu_button.winfo_rootx()
        y: int = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()

        self.popup.geometry( f'{ total_width }x{ visible_height + 10 }+{ x }+{ y }' )
        self.popup.deiconify()
        self.popup.focus_set()
        self.popup.bind_all( '<MouseWheel>', self._on_mousewheel )

        self._visible = True
