"""
Create a Frame widget for gathering application settings
For each available setting, create appropriate control widgets

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
from tkinter import N, W, BooleanVar, StringVar, ttk

from automation_menu.models import Settings
from automation_menu.utils import language_manager

def get_settings_tab( tabcontrol: ttk.Notebook, settings: Settings, main_object ) -> ttk.Frame:
    tabSettings = ttk.Frame( tabcontrol , padding = ( 5, 5, 5, 5 ) )

    _list_settings( tab = tabSettings, settings = settings, main_object = main_object )

    return tabSettings

def _list_settings( tab: ttk.Frame, settings: Settings, main_object ):
    """ Create widgets for application settings """

    from automation_menu.utils.localization import _, get_available_languages

    val_chb_on_top = BooleanVar( value = settings.get( 'on_top' ) )
    chbTopMost = ttk.Checkbutton( master = tab,
                                 text = _( 'Set as topmost window' ),
                                 variable = val_chb_on_top,
                                 command = lambda: main_object.set_on_top( val_chb_on_top.get() ) )
    tt = AlwaysOnTopToolTip( widget = chbTopMost, msg = _ ( 'Shall the window be set as topmost, above all other windows' ) )
    chbTopMost.grid( column = 0 , row = 0, sticky = ( N, W ) )
    main_object.language_manager.add_translatable_widget( ( chbTopMost, 'Set as topmost window' ) )
    main_object.language_manager.add_translatable_widget( ( tt, 'Shall the window be set as topmost, above all other windows' , False ) )

    val_chb_minimize_on_running = BooleanVar( value = settings.get( 'minimize_on_running' ) )
    chbMinimizeOnRunning = ttk.Checkbutton( master = tab,
                                              text = _( 'Minimize size during script execution' ),
                                              variable = val_chb_minimize_on_running,
                                              command = lambda: main_object.set_minimize_on_running( val_chb_minimize_on_running.get() ) )
    tt = AlwaysOnTopToolTip( widget = chbMinimizeOnRunning, msg = _( 'Downsize the window during script execution, trying not to be in its way. This setting can be ignored in ScriptInfo-block with \'DisableMinimizeOnRunning\'.' ) )
    chbMinimizeOnRunning.grid( column = 0 , row = 1, sticky = ( N, W ) )
    main_object.language_manager.add_translatable_widget( ( chbMinimizeOnRunning, 'Minimize size during script execution' ) )
    main_object.language_manager.add_translatable_widget( ( tt, 'Downsize the window during script execution, trying not to be in its way. This setting can be ignored in ScriptInfo-block with \'DisableMinimizeOnRunning\'.' , False ) )

    val_chb_include_ss_in_error_mail = BooleanVar( value = settings.get( 'include_ss_in_error_mail' ) )
    chbIncludeSsInErrorMail = ttk.Checkbutton( master = tab,
                                                    text = _( 'Include screenshot in mail when reporting error' ),
                                                    variable = val_chb_include_ss_in_error_mail,
                                                    command = lambda: main_object.set_include_ss_in_error_mail( val_chb_include_ss_in_error_mail.get() ) )
    tt = AlwaysOnTopToolTip( widget = chbIncludeSsInErrorMail, msg = _( 'Should the mail sent to script developer when reporting that an error occured, have a screenshot of main window attached?' ) )
    chbIncludeSsInErrorMail.grid( column = 0 , row = 2, sticky = ( N, W ) )
    main_object.language_manager.add_translatable_widget( ( chbIncludeSsInErrorMail, 'Include screenshot in mail when reporting error' ) )
    main_object.language_manager.add_translatable_widget( ( tt, 'Should the mail sent to script developer when reporting that an error occured, have a screenshot of main window attached?' , False ) )

    language_frame = ttk.Frame( tab )
    language_frame.grid( column = 0 , row = 3, sticky = ( N, W ) )
    language_frame.columnconfigure( index = 0, weight = 0 )
    language_frame.columnconfigure( index = 1, weight = 0 )

    lblCurrentLanguageTitle = ttk.Label( language_frame, text = _( 'Application language' ), padding = ( 5, 10 ) )
    lblCurrentLanguageTitle.grid( column = 0, row = 0, sticky = ( N, W ) )
    main_object.language_manager.add_translatable_widget( ( lblCurrentLanguageTitle, 'Application language' ) )

    val_cmb_current_language = StringVar( value = settings.get( 'current_language' ) )
    cmbCurrentLanguage = ttk.Combobox( master = language_frame,
                                       values = get_available_languages(),
                                       textvariable = val_cmb_current_language.get )
    cmbCurrentLanguage.bind( '<<ComboboxSelected>>', main_object.set_current_language )
    cmbCurrentLanguage.grid( column = 1, row = 0, pady = 5, sticky = ( N, W ) )
    cmbCurrentLanguage.current( cmbCurrentLanguage[ 'values' ].index( val_cmb_current_language.get() ) )
    tt = AlwaysOnTopToolTip( widget = cmbCurrentLanguage, msg = _( 'Language to use in the application' ) )
    main_object.language_manager.add_translatable_widget( ( tt, 'Language to use in the application' , False ) )

# In settings_tab.py - when combobox changes
def on_language_selection( event ):
    new_language = event.widget.get()
    language_manager.change_language( new_language )

    """
    self.val_chb_display_dev = BooleanVar( value = False )
    self.chb_display_dev = ttk.Checkbutton( self.tabSettings, text = 'Visa skript i dev', variable = self.val_chb_display_dev, command = self.set_display_dev )
    self.chb_display_dev.grid( column = 0 , row = 1, sticky = ( N, S, E, W ) )
    """

