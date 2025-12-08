"""
Collected UI styling for main window

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-08
"""

from __future__ import annotations

from tkinter.ttk import Entry, Style


def set_output_styles( widget: Entry ) -> None:
    """ Setup Text widget tag configurations

    Args:
        widget (ttk.Entry): Widget to set text tags for
    """

    widget.tag_config( tagName = 'suite_error', foreground = 'Red', font = ( 'Arial', 12, 'bold' ) )
    widget.tag_config( tagName = 'suite_info', foreground = 'Blue', font = ( 'Arial', 12 , 'bold' ) )
    widget.tag_config( tagName = 'suite_success', foreground = 'Green', font = ( 'Arial', 12 , 'bold' ) )
    widget.tag_config( tagName = 'suite_warning', foreground = 'Orange', font = ( 'Arial', 12 ) )
    widget.tag_config( tagName = 'suite_syserror', foreground = 'Red', font = ( 'Arial', 12, 'italic' ) )
    widget.tag_config( tagName = 'suite_sysinfo', foreground = 'Black', font = ( 'Arial', 12, 'italic' ) )
    widget.tag_config( tagName = 'suite_syswarning', foreground = 'Orange', font = ( 'Arial', 12, 'italic' ) )


def set_ui_style( style: Style ) -> None:
    """ Configure widget styles

    Args:
        style (ttk.Style): Main style to set
    """

    style.theme_use( 'clam' )

    ################
    # Button styling
    # region
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
    style.configure( 'RunningSmall.TButton',
                   font = ( 'Calibri', 9, 'normal' ),
                   padding = ( 2, 1 )
    )
    # endregion

    ###############
    # Entry styling
    # region
    style.configure( 'Input.TEntry',
                    font = ( 'Calibri', 10, 'normal' ),
                    relief = 'flat',
                    fieldbackground = 'white'
    )
    style.map( 'Input.TEntry',
                fieldbackground = [ ( 'focus', "#c5faff" ) ]
    )
    # endregion

    ####################
    # Checbutton styling
    # region
    style.configure( 'TCheckbutton',
                    padding = ( 10, 5 )
    )
    # endregion

    ##################
    # Combobox styling
    # region
    style.configure( 'Input.TCombobox',
                    font = ( 'Calibri', 10, 'normal' ),
                    padding = ( 2, 2 )
    )
    style.map( 'Input.TCombobox',
                fieldbackground = [ ( 'focus', "#c5faff" ) ]
    )
    # endregion

    ###############
    # Frame styling
    # region
    style.configure( 'SequenceStep.TFrame',
                    highlightcolor = '#FFFFFF',
                    highlightthickness = '2'
     )
    # endregion

    ###############
    # Label styling
    # region
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
    style.configure( 'BiggerTitle.TLabel',
                    font = ( 'Calibri', 15, 'bold' )
    )
    style.configure( 'LabelFrameTitle.TLabel',
                    font = ( 'Calibri', 13, 'bold' )
    )
    style.configure( 'LabelFrameTitleDescription.TLabel',
                    font = ( 'Calibri', 10, 'normal' )
    )
    style.configure( 'TLabel',
                    font = ( 'Calibri', 10, 'normal' ),
                    padding = ( 2, 2 )
    )
    # endregion

    ####################
    # LabelFrame styling
    # region
    style.configure( 'TLabelframe',
                    padding = ( 10, 5 ),
                    width = 500
    )
    # endregion

    ##################
    # Notebook styling
    # region
    style.configure( 'TNotebook',
                    tabmargins = [ 0, 1, 2, 0 ],  #[left, top, right, bottom]
                    background = 'lightgray'
    )

    style.configure( 'Dev.TNotebook',
                    tabmargins = [ 0, 1, 2, 0 ],  #[left, top, right, bottom]
                    background = "#D69456"
    )

    style.configure( 'Test.TNotebook',
                    tabmargins = [ 0, 1, 2, 0 ],  #[left, top, right, bottom]
                    background = "#52F9F1"
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

    style.layout( 'HiddenTabs.TNotebook.Tab',
                 []
                 )
    style.layout('HiddenTabs.TNotebook',
                 style.layout( 'TNotebook' )
                 )

    # endregion

    #####################
    # Progressbar styling
    # region Progressbar
    style.configure( 'TProgressbar',
                    troughcolor='#E6E6E6',      # Light grey background
                    background='#4DA6FF',       # Blue filled bar
                    darkcolor='#4DA6FF',
                    lightcolor='#80C1FF',
                    bordercolor='#A0A0A0',
                    thickness = 10
    )
    style.configure( 'RunningSmall.TProgressbar',
                    troughcolor='#DDDDDD',      # slightly dimmer trough
                    background='#2F8AE3',       # deeper blue for compact layout
                    darkcolor='#2F8AE3',
                    lightcolor='#6BB6F2',
                    bordercolor='#888888',
                    thickness = 8
    )
    style.layout('TProgressbar',
             [ ( 'Horizontal.Progressbar.trough', { 'children': [
                 ( 'Horizontal.Progressbar.pbar', { 'side': 'left', 'sticky': 'ns' } )
             ],
             'sticky': 'nswe' } ) ] )
    style.layout('RunningSmall.TProgressbar',
             [ ( 'Horizontal.Progressbar.trough', { 'children': [
                 ( 'Horizontal.Progressbar.pbar', { 'side': 'left', 'sticky': 'ns' } )
             ],
             'sticky': 'nswe' } ) ] )
    # endregion Progressbar
