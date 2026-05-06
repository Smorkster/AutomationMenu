"""
Manager of language change and ui widget updating

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
from tkinter import Toplevel
from tkinter.ttk import Button, Checkbutton, Combobox, Frame, Label, Notebook, Treeview
from typing import cast

from automation_menu.models.enums import ScriptState
from automation_menu.ui.types.widget_for_translation import WidgetForTranslation
from automation_menu.utils.localization import change_language, translate

class LanguageManager:
    """ Manage application language changes and translation updates for registered widgets."""

    def __init__( self, current_language: str = 'sv_SE' ) -> None:
        """ Initialize the language manager.

        Args:
            current_language (str): Language currently in use.
        """

        from automation_menu.utils.localization import _

        self._widgets_to_update: list[ WidgetForTranslation ] = []
        self._current_language: str = current_language
        self._ = _
        self._current_language: str = current_language


    def _update_button( self, widget: Button, text: str ) -> None:
        """ Update translated text for a button widget.

        Args:
            widget (Button): Button to update.
            text (str): Translation key for the button text.
        """

        widget.config( text = translate( text = text ) )


    def _update_checkbutton( self, widget: Checkbutton, text: str ) -> None:
        """ Update translated text for a checkbutton widget.

        Args:
            widget (Checkbutton): Checkbutton to update.
            text (str): Translation key for the checkbutton text.
        """

        widget.config( text = translate( text = text ) )


    def _update_combobox( self, widget: Combobox, texts: list[ str ] ) -> None:
        """ Update translated items for a combobox widget.

        Args:
            widget (Combobox): Combobox to update.
            texts (list[str]): Translation keys for the combobox items.
        """

        pass


    def _update_frame( self, widget: Frame, text: str ) -> None:
        """ Update translated tab text for a frame inside a notebook.

        Args:
            widget (Frame): Frame whose notebook tab text should be updated.
            text (str): Translation key for the tab text.
        """

        idx: int = widget.master.winfo_children().index( widget )
        cast( Notebook, widget.master ).tab( idx, text = translate( text = text ) )
        widget.update_idletasks()


    def _update_label( self, widget: Label, text: str ) -> None:
        """ Update translated text for a label widget.

        Args:
            widget (Label): Label to update.
            text (str): Translation key for the label text.
        """

        widget.config( text = translate( text ) )


    def _update_treeview( self, widget: Treeview, texts: dict[ str, list[ str | int ] ] ) -> None:
        """ Update translated column headers for a treeview widget.

        Args:
            widget (Treeview): Treeview to update.
            texts (dict[str, list[str | int]]): Mapping of column IDs to translated header definitions.
        """

        for i, s in texts.items():
            widget.heading( i, text = translate( text = cast( str, s[ 0 ] ) ) )


    def _update_toplevel( self, widget: Toplevel, text: str ) -> None:
        """ Update translated title text for a toplevel window.

        Args:
            widget (Toplevel): Toplevel window to update.
            text (str): Translation key for the window title.
        """

        widget.title( translate( text ) )
        widget.update_idletasks()
        pass


    def _update_tt( self, widget: AlwaysOnTopToolTip, text: str, script_state: ScriptState, include_application_test_info: bool ) -> None:
        """ Update translated text for a tooltip.

        Args:
            widget (AlwaysOnTopToolTip): Tooltip to update.
            text (str): Translation key for the tooltip text.
            script_state (ScriptState): Script state used to determine whether development information should be added.
            include_application_test_info (bool): Whether application test information should be added.
        """

        new_text: str = translate( text )
        if script_state == ScriptState.DEV:
            dev_text: str = translate( 'In development, and should only be run by its developer.' )
            new_text += f'\n\n{ dev_text }'

        elif include_application_test_info:
            test_text: str = translate( 'Application test script, only used to test application functionality' )
            new_text += f'\n\n{ test_text }'

        widget.config( new_text = new_text )


    def add_translatable_widget( self, widget: WidgetForTranslation ) -> None:
        """ Register a widget for later translation updates.

        Args:
            widget (WidgetForTranslation): Widget holder to register as translatable.
        """

        self._widgets_to_update.append( widget )


    def change_app_language( self, new_language: str ) -> None:
        """ Change the application language and update registered widgets.

        Args:
            new_language (str): Language key to switch to.
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
