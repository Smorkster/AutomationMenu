"""
Object representing a menu item for a sequence

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-12-01
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Callable

from automation_menu.models.sequence import Sequence

if TYPE_CHECKING:
    from automation_menu.ui.main_window import AutomationMenuWindow

import alwaysontop_tooltip

from tkinter import Event, Toplevel
from tkinter.ttk import Frame, Label


class SequenceMenuItem:
    def __init__ ( self, sequence_menu: Frame, sequence: Sequence, main_object: AutomationMenuWindow, menu_hide_callback: Callable ) -> None:
        """ Object for representing a sequence in the menu

        Args:
            sequence_menu (Frame): Frame to attach menu item to
            sequence (Sequence): Sequence to create menuitem for
            main_object (AutomationMenuWindow): The main window
            menu_hide_callback (Callable): Function callback for hiding menu
        """

        from automation_menu.utils.localization import _

        self._sequence_menu = sequence_menu
        self._sequence = sequence
        self._main_object = main_object
        self._hide_menu = menu_hide_callback

        style = 'ScriptNormal.TLabel'
        label_text = self._sequence.name
        label_tt = self._sequence.description

        self.menu_button = Label( master = self._sequence_menu, text = label_text, style = style, borderwidth = 1, name = str( self._sequence.id ) )
        self.menu_button.bind( '<Button-1>', self._on_click )

        alwaysontop_tooltip.alwaysontop_tooltip.AlwaysOnTopToolTip( widget = self.menu_button, msg = label_tt )


    def _on_click( self, event: Event ) -> None:
        """ Handler for click on label

        Args:
            event (Event): Event that triggered handler
        """

        self._hide_menu()
        self._main_object.app_context.sequence_manager.run_sequence( id = self._sequence.id )


    def on_enter( self, event: Event ) -> None:
        """ Change label background on mouse enter

        Args:
            event: Event triggering the function
        """

        event.widget.configure( style = 'ScriptHover.TLabel' )


    def on_leave( self, event: Event ) -> None:
        """ Change label background on mouse leave

        Args:
            event: Event triggering the function
        """

        event.widget.configure( style = 'ScriptNormal.TLabel' )
