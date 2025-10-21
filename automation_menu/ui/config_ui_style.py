
from tkinter import ttk


def set_ui_style( style: ttk.Style, main_self ):
    """ 
    
    Args:
        style (ttk.Style): Main style to set
        main_self (AutomationMenuWindow): Main UI object to set
    """

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
    style.configure( 'TButton',
                    font = ( 'Calibri', 12, 'normal' ),
                    padding = ( 2, 4 )
    )
    style.configure( 'TLabelFrame',
                    padding = ( 10, 5 ),
                    width = 500
    )
    style.configure( 'TCheckbutton',
                    padding = ( 10, 5 )
    )
    style.configure( 'History.TLabel',
                    font = ( 'Calibri', 12, 'bold' )
    )

    main_self.tbOutput.tag_config( tagName = 'suite_error', foreground = 'Red', font = ( 'Arial', 12, 'bold' ) )
    main_self.tbOutput.tag_config( tagName = 'suite_info', foreground = 'Blue', font = ( 'Arial', 12 , 'bold' ) )
    main_self.tbOutput.tag_config( tagName = 'suite_success', foreground = 'Green', font = ( 'Arial', 12 , 'bold' ) )
    main_self.tbOutput.tag_config( tagName = 'suite_warning', foreground = 'Orange', font = ( 'Arial', 12 ) )
    main_self.tbOutput.tag_config( tagName = 'suite_syserror', foreground = 'Red', font = ( 'Arial', 12, 'italic' ) )
    main_self.tbOutput.tag_config( tagName = 'suite_sysinfo', foreground = 'Black', font = ( 'Arial', 12, 'italic' ) )
    main_self.tbOutput.tag_config( tagName = 'suite_syswarning', foreground = 'Orange', font = ( 'Arial', 12, 'italic' ) )
