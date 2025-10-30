
from tkinter import ttk


def set_ui_style( style: ttk.Style ):
    """ 

    Args:
        style (ttk.Style): Main style to set
    """

    style.theme_use( 'clam' )

    ##################
    # Notebook styling
    style.configure( 'TNotebook',
                    tabmargins = [ 0, 1, 2, 0 ],  #[left, top, right, bottom]
                    background = 'lightgray'
    )
    style.configure( 'TNotebook.Tab',
                    padding = [ 25, 1.5 ], 
                    font = ( 'Calibri', 13, 'bold' ),
                    relief = 'flat'
    )
    style.map( 'TNotebook.Tab',
                background = [ ( 'selected', '#f1f1f1' ),
                              ( 'active', 'lightblue' ) ],
                padding = [ ( 'selected', ( 25, 1.5 ) ),
                           ( 'active', ( 25, 1.5 ) ),
                           ( '!selected', ( 25, 1.5 ) ) ],
                foreground = [ ( 'selected', 'green' ), ( 'active', 'black' ) ]
    )

    ###############
    # Label styling
    style.configure( 'ScriptHover.TLabel',
                    background = '#c2e6f3',
                    font = ( 'Calibri', 12, 'normal' )
    )
    style.configure( 'ScriptNormal.TLabel',
                    background = 'SystemButtonFace',
                    font = ( 'Calibri', 12, 'normal' )
    )
    style.configure( 'DevHover.TLabel',
                    background = '#c2e6f3',
                    font = ( 'Calibri', 12, 'bold' )
    )
    style.configure( 'DevNormal.TLabel',
                    background = 'SystemButtonFace',
                    font = ( 'Calibri', 12, 'bold' )
    )
    style.configure( 'History.TLabel',
                    font = ( 'Calibri', 12, 'bold' )
    )
    style.configure( 'LabelFrameTitle.TLabel',
                    font = ( 'Calibri', 13, 'bold' )

    )
    style.configure( 'TLabel',
                    font = ( 'Calibri', 10, 'normal' ),
                    padding = ( 5, 5 )
    )

    ################
    # Button styling
    btn_padding = ( 10, 5 )
    style.configure( 'TButton',
                    font = ( 'Calibri', 12, 'normal' ),
                    padding = btn_padding
    )
    style.configure( 'BlinkBg.TButton',
                    background = '#5ad5be',
                    font = ( 'Calibri', 12, 'normal' ),
                    padding = btn_padding
    )

    ####################
    # LabelFrame styling
    style.configure( 'TLabelframe',
                    padding = ( 10, 5 ),
                    width = 500
    )

    ####################
    # Checbutton styling
    style.configure( 'TCheckbutton',
                    padding = ( 10, 5 )
    )


def set_output_styles( widget ) -> None:
    """ Setup Text widget tag configurations"""

    widget.tag_config( tagName = 'suite_error', foreground = 'Red', font = ( 'Arial', 12, 'bold' ) )
    widget.tag_config( tagName = 'suite_info', foreground = 'Blue', font = ( 'Arial', 12 , 'bold' ) )
    widget.tag_config( tagName = 'suite_success', foreground = 'Green', font = ( 'Arial', 12 , 'bold' ) )
    widget.tag_config( tagName = 'suite_warning', foreground = 'Orange', font = ( 'Arial', 12 ) )
    widget.tag_config( tagName = 'suite_syserror', foreground = 'Red', font = ( 'Arial', 12, 'italic' ) )
    widget.tag_config( tagName = 'suite_sysinfo', foreground = 'Black', font = ( 'Arial', 12, 'italic' ) )
    widget.tag_config( tagName = 'suite_syswarning', foreground = 'Orange', font = ( 'Arial', 12, 'italic' ) )
