"""
Manager of language change and ui widget updating

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from __future__ import annotations

from tkinter import Toplevel
from tkinter.ttk import Button, Checkbutton, Combobox, Frame, Label, Notebook, Treeview
from typing import cast

from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip

from automation_menu.models.enums import ScriptState
from automation_menu.models.widget_for_translation import WidgetForTranslation
from automation_menu.utils.localization import change_language

class LanguageManager:
    def __init__( self, current_language: str = 'sv_SE' ) -> None:
        """ Manage language change and GUI update

        Args:
            current_language (str): Language currently used
        """

        from automation_menu.utils.localization import _

        self._widgets_to_update: list[ WidgetForTranslation ] = []
        self._current_language: str = current_language
        self._ = _
        self._current_language: str = current_language


    def translate( self, text: str ) -> str:
        """ Translate string

        Args:
            text (str): Text to translate

        Returns:
            tt (str): The translated string
        """

        t: str = '{}'.format( text )
        tt: str = self._( message = t )

        return tt


    def _update_button( self, widget: Button, text: str ) -> None:
        """ Update text for ttk.Button

        Args:
            widget (Button): Button to update
            text (str): Text to set in the button
        """

        widget.config( text = self.translate( text = text ) )


    def _update_checkbutton( self, widget: Checkbutton, text: str ) -> None:
        """ Update text for ttk.Checkbutton

        Args:
            widget (Checkbutton): Checkbutton to update
            text (str): String, as translation key
        """

        widget.config( text = self.translate( text = text ) )


    def _update_combobox( self, widget: Combobox, texts: list[ str ] ) -> None:
        """ Update combobox items

        Args:
            widget (Combobox): Combobox to update
            texts (list[ str ]): List of strings, as translation keys
        """

        pass


    def _update_frame( self, widget: Frame, text: str ) -> None:
        """ Update text for Frame

        Args:
            widget (Frame): Frame to update
            text (str): String, as translation key
        """

        idx: int = widget.master.winfo_children().index( widget )
        cast( Notebook, widget.master ).tab( idx, text = self.translate( text = text ) )
        widget.update_idletasks()


    def _update_label( self, widget: Label, text: str ) -> None:
        """ Update label text

        Args:
            widget (Label): Tuple of label to update
            text (str): String, as translation key
        """

        widget.config( text = self.translate( text ) )


    def _update_treeview( self, widget: Treeview, texts: dict[ str, list[ str | int ] ] ) -> None:
        """ Update column headers for Treeview

        Args:
            widget (Treeview): Holder for translation
            texts (dict[ str, list[ str | int ] ]): Dict with column names and strings, as translation key
        """

        for i, s in texts.items():
            widget.heading( i, text = self.translate( text = cast( str, s[ 0 ] ) ) )


    def _update_toplevel( self, widget: Toplevel, text: str ) -> None:
        """ Update text for Toplevel

        Args:
            widget (Toplevel): Tuple of Toplevel to update and string, as translation key
            text (str): String, as translation key
        """

        widget.title( self.translate( text ) )
        widget.update_idletasks()
        pass


    def _update_tt( self, widget: AlwaysOnTopToolTip, text: str, script_state: ScriptState, include_application_test_info: bool ) -> None:
        """ Update text for AlwaysOnTopTooltip

        Args:
            widget (AlwaysOnTopToolTip): Tooltip to update
            text (str): String, as translation key
            script_state (ScriptState): State for if development information should be added
            include_application_test_info (bool): Should information about application test information be aded
        """

        new_text: str = self.translate( text )
        if script_state == ScriptState.DEV:
            dev_text: str = self.translate( 'In development, and should only be run by its developer.' )
            new_text += f'\n\n{ dev_text }'

        elif include_application_test_info:
            test_text: str = self.translate( 'Application test script, only used to test application functionality' )
            new_text += f'\n\n{ test_text }'

        widget.config( new_text = new_text )


    def add_translatable_widget( self, widget: WidgetForTranslation ) -> None:
        """ Add a widget to list for later translation

        Args:
            widget (WidgetForTranslation): Widget holder to be translatable
        """

        self._widgets_to_update.append( widget )


    def change_app_language( self, new_language: str ) -> None:
        """ Change application language and reconfigure widgets
        Loop all registered widgets that should be updated

        Args:
            new_language (str): Language key to switch to
        """

        self._current_language = new_language
        change_language( language_code = new_language )

        from automation_menu.utils.localization import _

        self._ = _

        for widget_holder in self._widgets_to_update:
            try:
                if isinstance( widget_holder.widget, AlwaysOnTopToolTip ):
                    tt_text: str = cast( str,  widget_holder.default_text )
                    self._update_tt( widget = widget_holder.widget, text = tt_text, script_state = widget_holder.script_state, include_application_test_info = widget_holder.include_application_test_info )

                elif isinstance( widget_holder.widget, Button ):
                    btn_text: str = cast( str,  widget_holder.default_text )
                    self._update_button( widget = widget_holder.widget, text = btn_text )

                elif isinstance( widget_holder.widget, Checkbutton ):
                    chb_text: str = cast( str,  widget_holder.default_text )
                    self._update_checkbutton( widget = widget_holder.widget, text = chb_text )

                elif isinstance( widget_holder.widget, Combobox ):
                    cb_text: list[ str ] = cast( list[ str ],  widget_holder.default_text )
                    self._update_combobox( widget = widget_holder.widget, texts = cb_text )

                elif isinstance( widget_holder.widget, Frame ):
                    fr_text: str = cast( str,  widget_holder.default_text )
                    self._update_frame( widget = widget_holder.widget, text = fr_text )

                elif isinstance( widget_holder.widget, Label ):
                    lbl_text: str = cast( str,  widget_holder.default_text )
                    self._update_label( widget = widget_holder.widget, text = lbl_text )

                elif isinstance( widget_holder.widget, Treeview ):
                    tv_text: dict[ str, list[ str | int ] ] = cast( dict[ str, list[ str | int ] ],  widget_holder.default_text )
                    self._update_treeview( widget = widget_holder.widget, texts = tv_text )

                elif isinstance( widget_holder.widget, Toplevel ):
                    tl_text: str = cast( str,  widget_holder.default_text )
                    self._update_toplevel( widget = widget_holder.widget, text = tl_text )

            except Exception as e:
                raise e
