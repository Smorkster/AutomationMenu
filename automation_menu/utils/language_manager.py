"""
Manager of language change and ui widget updating

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from __future__ import annotations

from gettext import GNUTranslations
from tkinter import Toplevel
from tkinter.ttk import Button, Checkbutton, Combobox, Frame, Label, Treeview

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
        self._: GNUTranslations = _
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


    def _update_button( self, widget: WidgetForTranslation ) -> None:
        """ Update text for ttk.Button

        Args:
            widget (WidgetForTranslation): Tuple of button to update and string, as translation key
        """

        widget.widget.config( text = self.translate( text = widget.default_text ) )


    def _update_checkbutton( self, widget: WidgetForTranslation ) -> None:
        """ Update text for ttk.Checkbutton

        Args:
            widget (WidgetForTranslation): Tuple of checkbutton to update and string, as translation key
        """

        widget.widget.config( text = self.translate( text = widget.default_text ) )


    def _update_combobox( self, widget: WidgetForTranslation ) -> None:
        """ Update combobox items

        Args:
            widget (WidgetForTranslation): Tuple of combobox to update and tuple of strings corresponding to items, as translation key
        """

        pass


    def _update_frame( self, widget: WidgetForTranslation ) -> None:
        """ Update text for Frame

        Args:
            widget (WidgetForTranslation): Tuple of frame to update and string, as translation key
        """

        idx: int = widget.widget.master.winfo_children().index( widget.widget )
        widget.widget.master.tab( idx, text = self.translate( text = widget.default_text ) )
        widget.widget.update_idletasks()


    def _update_label( self, widget: WidgetForTranslation ) -> None:
        """ Update label text

        Args:
            widget (WidgetForTranslation): Tuple of label to update and string, as translation key
        """

        widget.widget.config( text = self.translate( widget.default_text ) )


    def _update_treeview( self, widget: WidgetForTranslation ) -> None:
        """ Update column headers for Treeview

        Args:
            widget (WidgetForTranslation): Holder for translation
        """

        for i, s in widget.default_text.items():
            widget.widget.heading( i, text = self.translate( text = s[ 0 ] ) )


    def _update_toplevel( self, widget: WidgetForTranslation ) -> None:
        """ Update text for Toplevel

        Args:
            widget (WidgetForTranslation): Tuple of Toplevel to update and string, as translation key
        """

        widget.widget.title( self.translate( widget.default_text ) )
        widget.widget.update_idletasks()
        pass


    def _update_tt( self, widget: WidgetForTranslation ) -> None:
        """ Update text for AlwaysOnTopTooltip

        Args:
            widget (WidgetForTranslation): Tuple of tooltip to update, a string, as translation key and two booleans:
                if development information should be added
                if application test information should be aded
        """

        new_text: str = self.translate( widget.default_text )
        if widget.script_state == ScriptState.DEV:
            dev_text: str = self.translate( 'In development, and should only be run by its developer.' )
            new_text += f'\n\n{ dev_text }'

        elif widget.include_application_test_info:
            test_text: str = self.translate( 'Application test script, only used to test application functionality' )
            new_text += f'\n\n{ test_text }'

        widget.widget.config( new_text = new_text )


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
                    self._update_tt( widget_holder )

                elif isinstance( widget_holder.widget, Button ):
                    self._update_button( widget_holder )

                elif isinstance( widget_holder.widget, Checkbutton ):
                    self._update_checkbutton( widget_holder )

                elif isinstance( widget_holder.widget, Combobox ):
                    self._update_combobox( widget_holder )

                elif isinstance( widget_holder.widget, Frame ):
                    self._update_frame( widget_holder )

                elif isinstance( widget_holder.widget, Label ):
                    self._update_label( widget_holder )

                elif isinstance( widget_holder.widget, Treeview ):
                    self._update_treeview( widget_holder )

                elif isinstance( widget_holder.widget, Toplevel ):
                    self._update_toplevel( widget_holder )

            except Exception as e:
                raise e
