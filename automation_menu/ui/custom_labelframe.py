"""
Creates a custom LabelFrame with built in support
for mouse movement entering and leave widget boundaries

Author: Smorkster
GitHub:
License: MIT
Version: 1.0.0
Created: 2025-09-25
"""

from tkinter import LabelFrame


class CustomLabelFrame( LabelFrame ):
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )

        self.bind( '<Enter>', self._on_enter )
        self.bind( '<Leave>', self._on_leave )


    def _on_enter( self, event ):
        """ Configure LabelFrame when mouse enters widget boundaries
        
        Args:
            event: The event triggering the function
        """

        if isinstance( event.widget, CustomLabelFrame ):
            event.widget.config( font = ( 'Calibri', 9, 'bold' ) )


    def _on_leave( self, event ):
        """ Configure LabelFrame when mouse leaves widget boundaries
        
        Args:
            event: The event triggering the function
        """

        if isinstance( event.widget, CustomLabelFrame ):
            event.widget.config( font = ( 'Calibri', 9, 'normal' ) )
