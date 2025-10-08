from tkinter import LabelFrame, ttk


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
