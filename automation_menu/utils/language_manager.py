"""
Manager of language change and ui widget updating

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from re import T
from tkinter import Menu, Toplevel
from tkinter.ttk import Button, Checkbutton, Combobox, Notebook

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

    def add_widget( self, widget: any ) -> None:
        """ Add a widget to list for later translation

        Args:
            widget (tuple(widget, str | tuple)): Tuple of widget to translate and one or more strings, as translation keys, depending och widget type
        """

        self._widgets_to_update.append( widget )

    def change_language( self, new_language: str ) -> None:
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
                if isinstance( widget[ 0 ], Toplevel ):
                    self.update_toplevel( widget )
                elif isinstance( widget[ 0 ], Notebook ):
                    self.update_notebook( widget )
                elif isinstance( widget[ 0 ], Menu ):
                    self.update_menu( widget )
                elif isinstance( widget[ 0 ], Checkbutton ):
                    self.update_checkbutton( widget )
                elif isinstance( widget[ 0 ], AlwaysOnTopToolTip ):
                    self.update_tt( widget )
                elif isinstance( widget[ 0 ], Button ):
                    self.update_button( widget )
                elif isinstance( widget[ 0 ], Combobox ):
                    self.update_combobox( widget )
            except Exception as e:
                raise e

    def update_toplevel( self, widget ) -> None:
        """ Update text for Toplevel

        Args:
            widget (tuple[ Toplevel, (str) ]): Tuple of Toplevel to update and string, as translation key
        """

        pass

    def update_frame( self, widget ) -> None:
        """ Update text for Frame

        Args:
            widget (tuple[ Frame, (str) ]): Tuple of fram to update and string, as translation key
        """

        pass

    def update_menu( self, widget ) -> None:
        """ Update text for Menu
        Enumerate the strings and translate each topmenu (cascade) with the corresponding enum index

        Args:
            widget (tuple[ Menu, (str) ]): Tuple of menu to update and tuple of strings corresponding to topmenus, as translation key
        """

        for i, translation_key in enumerate( widget[ 1 ] ):
            t = self._translate( text = translation_key )
            a: Menu = widget[ 0 ]
            a.entryconfigure( i+1, label = t )

    def update_checkbutton( self, widget ) -> None:
        """ Update text for ttk.Checkbutton

        Args:
            widget (tuple[ Checkbutton, str ]): Tuple of checkbutton to update and string, as translation key
        """

        widget[ 0 ].config( text = self._translate( text = widget[ 1 ] ) )

    def update_notebook( self, widget ) -> None:
        """ Update text for ttk.Notebook

        Args:
            widget (tuple[ Notebook, str ]): Tuple of Notebook to update and string, as translation key
        """

        for i, t in enumerate( widget[ 1 ] ):
            widget[ 0 ].tab( i, text = self._translate( text = t ) )

    def update_button( self, widget ) -> None:
        """ Update text for ttk.Button

        Args:
            widget (tuple[ Button, str ]): Tuple of button to update and string, as translation key
        """

        widget[ 0 ].config( text = self._translate( text = widget[ 1 ] ) )

    def update_tt( self, widget: tuple[ AlwaysOnTopToolTip, str ] ) -> None:
        """ Update text for AlwaysOnTopTooltip

        Args:
            widget (tuple[ AlwaysOnTopToolTip, str ]): Tuple of tooltip to update and string, as translation key
        """

        if widget[ 2 ]:
            new_text = '{desc}\n\n{dev}'.format( desc = widget[1], dev = self._translate( 'In development, and should only be run by its developer.' ) )
        else:
            new_text = widget[ 1 ]
        widget[ 0 ].config( new_text = new_text )

    def update_combobox( self, widget ):
        """ Update combobox items
        
        Args:
            widget (tuple[ Combobox, str ]): Tuple of combobox to update and tuple of strings corresponding to topmenus, as translation key
        """

        pass