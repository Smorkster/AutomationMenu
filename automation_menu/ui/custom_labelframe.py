from tkinter import LabelFrame, ttk


class CustomLabelFrame( LabelFrame ):
    def __init__( self, *args, **kwargs ):
        super().__init__( *args, **kwargs )

        self.bind( '<Enter>', self._on_enter )
        self.bind( '<Leave>', self._on_leave )


    def _on_enter( self, event ):
        if isinstance( event.widget, CustomLabelFrame ):
            event.widget.config( font = ( 'Calibri', 9, 'bold' ) )


    def _on_leave( self, event ):
        if isinstance( event.widget, CustomLabelFrame ):
            event.widget.config( font = ( 'Calibri', 9, 'normal' ) )
