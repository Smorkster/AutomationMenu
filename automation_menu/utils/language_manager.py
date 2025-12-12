"""
Manager of language change and ui widget updating

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from __future__ import annotations

from tkinter import Menu, Toplevel
from tkinter.ttk import Button, Checkbutton, Combobox, Frame, Label, Notebook

from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip

from automation_menu.utils.localization import change_language

class LanguageManager:
    def __init__( self, current_language: str = 'sv_SE' ) -> None:
        """ Manage language change and GUI update

        Args:
            current_language (str): Language currently used
        """

        from automation_menu.utils.localization import _

        self._widgets_to_update = []
        self._current_language = current_language
        self._ = _


    def _translate( self, text: str ) -> str:
        """ Translate string

        Args:
            text (str): Text to translate

        Returns:
            tt (str): The translated string
        """

        t = '{}'.format( text )
        tt = self._( message = t )

        return tt


    def _update_button( self, widget: tuple[ Button, str ] ) -> None:
        """ Update text for ttk.Button

        Args:
            widget (tuple[ Button, str ]): Tuple of button to update and string, as translation key
        """

        widget[ 0 ].config( text = self._translate( text = widget[ 1 ] ) )


    def _update_checkbutton( self, widget: tuple[ Checkbutton, str ] ) -> None:
        """ Update text for ttk.Checkbutton

        Args:
            widget (tuple[ Checkbutton, str ]): Tuple of checkbutton to update and string, as translation key
        """

        widget[ 0 ].config( text = self._translate( text = widget[ 1 ] ) )


    def _update_combobox( self, widget: tuple[ Combobox, str ] ) -> None:
        """ Update combobox items

        Args:
            widget (tuple[ Combobox, str ]): Tuple of combobox to update and tuple of strings corresponding to topmenus, as translation key
        """

        pass


    def _update_frame( self, widget: tuple[ Frame, str ] ) -> None:
        """ Update text for Frame

        Args:
            widget (tuple[ Frame, str ]): Tuple of frame to update and string, as translation key
        """

        idx = widget[ 0 ].master.winfo_children().index( widget[ 0 ] )
        widget[ 0 ].master.tab( idx, text = self._translate( text = widget[ 1 ] ) )
        widget[ 0 ].update_idletasks()


    def _update_label( self, widget: tuple[ Label, str ] ) -> None:
        """ Update label text

        Args:
            widget (tuple[ Label, str ]): Tuple of label to update and string, as translation key
        """

        widget[ 0 ].config( text = self._translate( widget[ 1 ] ) )


    def _update_menu( self, widget: tuple[ Menu, tuple[ str, ... ] ] ) -> None:
        """ Update text for Menu
        Enumerate the strings and translate each topmenu (cascade) with the corresponding enum index

        Args:
            widget (tuple[ Menu, (str) ]): Tuple of menu to update and tuple of strings corresponding to topmenus, as translation key
        """

        for i, translation_key in enumerate( widget[ 1 ] ):
            t = self._translate( text = translation_key )
            a: Menu = widget[ 0 ]
            a.entryconfigure( i+1, label = t )
            a.update_idletasks()


    def _update_notebook( self, widget: tuple[ Notebook, tuple[ str, ... ] ] ) -> None:
        """ Update text for ttk.Notebook

        Args:
            widget (tuple[ Notebook, tuple[ str, ... ] ]): Tuple of Notebook to update and a tuple of strings, as translation keys
        """

        for i, t in enumerate( widget[ 1 ] ):
            widget[ 0 ].tab( i, text = self._translate( text = t ) )


    def _update_toplevel( self, widget: tuple[ Toplevel, str ] ) -> None:
        """ Update text for Toplevel

        Args:
            widget (tuple[ Toplevel, (str) ]): Tuple of Toplevel to update and string, as translation key
        """

        widget[ 0 ].title(self._translate( widget[ 1 ] ) )
        widget[ 0 ].update_idletasks()
        pass


    def _update_tt( self, widget: tuple[ AlwaysOnTopToolTip, str, bool, bool ] ) -> None:
        """ Update text for AlwaysOnTopTooltip

        Args:
            widget (tuple[ AlwaysOnTopToolTip, str, bool, bool ]): Tuple of tooltip to update, a string, as translation key and two booleans:
                if development information should be added
                if application test information should be aded
        """

        new_text = self._translate( widget[ 1 ] )
        if widget[ 2 ]:
            dev_text = self._translate( 'In development, and should only be run by its developer.' )
            new_text += f'\n\n{ dev_text }'

        elif widget[ 3 ]:
            test_text = self._translate( 'Application test script, only used to test application functionality' )
            new_text += f'\n\n{ test_text }'

        widget[ 0 ].config( new_text = new_text )


    def add_translatable_widget( self, widget: any ) -> None:
        """ Add a widget to list for later translation

        Args:
            widget (tuple(widget, str | tuple)): Tuple of widget to translate and one or more strings, as translation keys, depending och widget type
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

        for widget in self._widgets_to_update:
            try:
                if isinstance( widget[ 0 ], AlwaysOnTopToolTip ):
                    self._update_tt( widget )

                elif isinstance( widget[ 0 ], Button ):
                    self._update_button( widget )

                elif isinstance( widget[ 0 ], Checkbutton ):
                    self._update_checkbutton( widget )

                elif isinstance( widget[ 0 ], Combobox ):
                    self._update_combobox( widget )

                elif isinstance( widget[ 0 ], Frame ):
                    self._update_frame( widget )

                elif isinstance( widget[ 0 ], Label ):
                    self._update_label( widget )

                elif isinstance( widget[ 0 ], Menu ):
                    self._update_menu( widget )

                elif isinstance( widget[ 0 ], Notebook ):
                    self._update_notebook( widget )

                elif isinstance( widget[ 0 ], Toplevel ):
                    self._update_toplevel( widget )

            except Exception as e:
                raise e
