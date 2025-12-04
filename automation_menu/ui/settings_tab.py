"""
Create a Frame widget for gathering application settings
For each available setting, create appropriate control widgets

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.ui.main_window import AutomationMenuWindow

from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
from tkinter import E, N, S, W, BooleanVar, StringVar
from tkinter.ttk import Checkbutton, Combobox, Entry, Frame, Label, LabelFrame, Notebook

from automation_menu.models import Settings


def get_settings_tab( tabcontrol: Notebook, settings: Settings, main_self: AutomationMenuWindow ) -> Frame:
    """ Create a frame used as a tab to collect settings

    Args:
        tabcontrol (Notebook): Tabcontrol (Notebook) to place the frame in
        settings (Settings): Collection of settings data
        main_object (AutomationMenuWindow): Main object
    """

    from automation_menu.utils.localization import _

    tabSettings = Frame( tabcontrol , padding = ( 5, 5, 5, 5 ) )
    tabSettings.grid( sticky = ( N, S, E, W ) )

    tabcontrol.add( child = tabSettings, text = _( 'Settings' ) )
    main_self.app_context.language_manager.add_translatable_widget( ( tabSettings, 'Settings' ) )

    _list_settings( tab = tabSettings, settings = settings, main_self = main_self )

    return tabSettings


def _list_settings( tab: Frame, settings: Settings, main_self: AutomationMenuWindow ) -> None:
    """ Create widgets for application settings

    Args:
        tab (Frame): Frame to place settings widgets in
        settings (Settings): Collection of settings data
        main_object (AutomationMenuWindow): Main object
    """

    from automation_menu.utils.localization import _, get_available_languages

    main_self.settings_ui = {}
    tab.columnconfigure( index = 0, weight = 1 )

    ######################
    # Application settings
    tab_frame_row = 0

    app_settings_group_title = Label( text=_( 'Application settings' ), style = 'LabelFrameTitle.TLabel' )
    app_settings_group = LabelFrame( master = tab, labelwidget = app_settings_group_title )
    app_settings_group.grid( column = 0, row = tab_frame_row, sticky = ( N, W, E ) )
    app_settings_group.grid_columnconfigure( index = 0, weight = 0, uniform = 'titles' )
    app_settings_group.grid_columnconfigure( index = 1, weight = 1, uniform = 'values' )
    main_self.app_context.language_manager.add_translatable_widget( ( app_settings_group_title, 'Application settings' ) )

    row = 0

    app_settings_group.rowconfigure( index = row, weight = 0 )
    chb_on_top_title = Label( master = app_settings_group, text = _( 'Set as topmost window' ), padding = ( 5, 10 ) )
    chb_on_top_title.grid( column = 0, row = row, sticky = ( W, E ) )
    main_self.app_context.language_manager.add_translatable_widget( ( chb_on_top_title, 'Set as topmost window' ) )

    val_chb_on_top = BooleanVar( value = settings.get( 'on_top' ) )
    chb_on_top = Checkbutton( master = app_settings_group,
                             variable = val_chb_on_top,
                             command = lambda: main_self.set_on_top( val_chb_on_top.get() ) )
    chb_on_top.grid( column = 1, row = row, sticky = ( N, W ) )
    main_self.settings_ui[ 'chbTopMost' ] = chb_on_top

    tt = AlwaysOnTopToolTip( widget = chb_on_top, msg = _ ( 'Shall the window be set as topmost, above all other windows' ) )
    main_self.app_context.language_manager.add_translatable_widget( ( tt, 'Shall the window be set as topmost, above all other windows' , False ) )

    row += 1

    app_settings_group.rowconfigure( index = row, weight = 0 )
    chb_minimize_on_running_title = Label( master = app_settings_group, text = _( 'Minimize size during script execution' ), padding = ( 5, 10 ) )
    chb_minimize_on_running_title.grid( column = 0, row = row, sticky = ( W, E ) )
    main_self.app_context.language_manager.add_translatable_widget( ( chb_minimize_on_running_title, 'Minimize size during script execution' ) )

    val_chb_minimize_on_running = BooleanVar( value = settings.get( 'minimize_on_running' ) )
    chb_minimize_on_running = Checkbutton( master = app_settings_group,
                                          variable = val_chb_minimize_on_running,
                                          command = lambda: main_self.set_minimize_on_running( val_chb_minimize_on_running.get() ) )
    chb_minimize_on_running.grid( column = 1, row = row, sticky = ( N, W ) )
    main_self.settings_ui[ 'chbMinimizeOnRunning' ] = chb_minimize_on_running

    tt = AlwaysOnTopToolTip( widget = chb_minimize_on_running, msg = _( 'Downsize the window during script execution, trying not to be in its way. This setting can be ignored in ScriptInfo-block with \'DisableMinimizeOnRunning\'.' ) )
    main_self.app_context.language_manager.add_translatable_widget( ( tt, 'Downsize the window during script execution, trying not to be in its way. This setting can be ignored in ScriptInfo-block with \'DisableMinimizeOnRunning\'.' , False ) )

    row += 1

    app_settings_group.rowconfigure( index = row, weight = 0 )
    cmb_current_language_title = Label( master = app_settings_group, text = _( 'Application language' ), padding = ( 5, 10 ) )
    cmb_current_language_title.grid( column = 0, row = row, sticky = ( N, W ) )
    main_self.app_context.language_manager.add_translatable_widget( ( cmb_current_language_title, 'Application language' ) )

    val_cmb_current_language = StringVar( value = settings.get( 'current_language' ) )
    cmb_current_language = Combobox( master = app_settings_group,
                                       values = get_available_languages(),
                                       textvariable = val_cmb_current_language.get )
    cmb_current_language.bind( '<<ComboboxSelected>>', main_self.set_current_language )
    cmb_current_language.grid( column = 1, row = row, padx = 5, pady = 5, sticky = ( W, E ) )
    cmb_current_language.current( cmb_current_language[ 'values' ].index( val_cmb_current_language.get() ) )
    main_self.settings_ui[ 'cmbCurrentLanguage' ] = cmb_current_language

    tt = AlwaysOnTopToolTip( widget = cmb_current_language, msg = _( 'Language to use in the application' ) )
    main_self.app_context.language_manager.add_translatable_widget( ( tt, 'Language to use in the application' , False ) )

    row += 1

    app_settings_group.rowconfigure( index = row, weight = 0 )
    keepass_shortcut_title = Label( master = app_settings_group, text = _( 'KeePass shortcut' ), padding = ( 5, 10 ) )
    keepass_shortcut_title.grid( column = 0, row = row, sticky = ( N, W ) )
    main_self.app_context.language_manager.add_translatable_widget( ( keepass_shortcut_title, 'KeePass shortcut' ) )

    keepass_shortcut_value_frame = Frame( master = app_settings_group )
    keepass_shortcut_value_frame.grid( column = 1, row = row, sticky = ( N, W, E ) )

    val_keepass_shortcut_ctrl = BooleanVar( value = main_self.app_state.settings.get( 'keepass_shortcut' ).get( 'ctrl' ) )
    keepass_shortcut_ctrl = Checkbutton( master = keepass_shortcut_value_frame,
                                        text = _( 'CTRL' ),
                                        variable = val_keepass_shortcut_ctrl,
                                        command = lambda: main_self.app_state.settings.set_keepass_shortcut( value_tup = ( 'ctrl', val_keepass_shortcut_ctrl.get() ) ) )
    keepass_shortcut_ctrl.grid( column = 0, row = 0, sticky = ( N, W ) )
    main_self.settings_ui[ 'keepass_shortcut_ctrl' ] = keepass_shortcut_ctrl
    main_self.settings_ui[ 'keepass_shortcut_ctrl_val' ] = val_keepass_shortcut_ctrl
    main_self.app_context.language_manager.add_translatable_widget( ( keepass_shortcut_ctrl, 'CTRL' ) )
    keepass_shortcut_ctrl.update_idletasks()

    val_keepass_shortcut_alt = BooleanVar( value = main_self.app_state.settings.get( 'keepass_shortcut' ).get( 'alt' ) )
    keepass_shortcut_alt = Checkbutton( master = keepass_shortcut_value_frame,
                                       text = _( 'ALT' ),
                                       variable = val_keepass_shortcut_alt,
                                       command = lambda : main_self.app_state.settings.set_keepass_shortcut( value_tup = ( 'alt', val_keepass_shortcut_alt.get() ) ) )
    keepass_shortcut_alt.grid( column = 1, row = 0, sticky = ( N, W ) )
    main_self.settings_ui[ 'keepass_shortcut_alt' ] = keepass_shortcut_alt
    main_self.settings_ui[ 'keepass_shortcut_alt_val' ] = val_keepass_shortcut_alt
    main_self.app_context.language_manager.add_translatable_widget( ( keepass_shortcut_alt, 'ALT' ) )
    keepass_shortcut_alt.update_idletasks()

    val_keepass_shortcut_shift = BooleanVar( value = main_self.app_state.settings.get( 'keepass_shortcut' ).get( 'shift' ) )
    keepass_shortcut_shift = Checkbutton( master = keepass_shortcut_value_frame,
                                         text = _( 'Shift' ),
                                         variable = val_keepass_shortcut_shift,
                                         command = lambda *args: main_self.app_state.settings.set_keepass_shortcut( value_tup = ( 'shift', val_keepass_shortcut_shift.get() ) ) )
    keepass_shortcut_shift.grid( column = 2, row = 0, sticky = ( N, W ) )
    main_self.settings_ui[ 'keepass_shortcut_shift' ] = keepass_shortcut_shift
    main_self.settings_ui[ 'keepass_shortcut_shift_val' ] = val_keepass_shortcut_shift
    main_self.app_context.language_manager.add_translatable_widget( ( keepass_shortcut_shift, 'Shift' ) )
    keepass_shortcut_shift.update_idletasks()

    val_keepass_shortcut_key = StringVar( value = main_self.app_state.settings.get( 'keepass_shortcut' ).get( 'key' ) )
    keepass_shortcut_key = Entry( master = keepass_shortcut_value_frame,
                                 textvariable = val_keepass_shortcut_key )
    val_keepass_shortcut_key.trace_add( mode = 'write', callback = lambda *args: main_self.app_state.settings.set_keepass_shortcut( value_tup = ( 'key', val_keepass_shortcut_key.get() ) ) )
    keepass_shortcut_key.grid( column = 3, row = 0, padx = 5, pady = 5, sticky = ( W ) )
    main_self.settings_ui[ 'keepass_shortcut_key' ] = keepass_shortcut_key
    main_self.settings_ui[ 'keepass_shortcut_key_val' ] = val_keepass_shortcut_key
    keepass_shortcut_key.update_idletasks()

    tt = AlwaysOnTopToolTip( widget = keepass_shortcut_key, msg = _( 'Shortcut used to activate KeePass for auto typing' ) )
    main_self.app_context.language_manager.add_translatable_widget( ( tt, 'Shortcut used to activate KeePass for auto typing' , False ) )

    keepass_shortcut_value_frame.update_idletasks()

    ###############
    # Errorhandling
    tab_frame_row += 1

    error_group_title = Label( text = _( 'Errorhandling' ), style = 'LabelFrameTitle.TLabel' )
    error_group = LabelFrame( tab, labelwidget = error_group_title )
    error_group.grid_columnconfigure( index = 0, weight = 0, uniform = 'titles' )
    error_group.grid_columnconfigure( index = 1, weight = 1, uniform = 'values' )
    error_group.grid( column = 0, row = tab_frame_row, sticky = ( N, W, E ) )
    main_self.app_context.language_manager.add_translatable_widget( ( error_group_title, 'Errorhandling' ) )

    row = 0

    error_group.rowconfigure( index = row, weight = 0 )
    chb_send_mail_on_error_title = Label( master = error_group, text = _( 'Send mail to developer on script error' ), padding = ( 5, 10 ) )
    chb_send_mail_on_error_title.grid( column = 0, row = row, sticky = ( W, E ) )
    main_self.app_context.language_manager.add_translatable_widget( ( chb_send_mail_on_error_title, 'Send mail to developer on script error' ) )

    val_chb_send_mail_on_error = BooleanVar( value = main_self.app_state.settings.get( 'send_mail_on_error' ) )
    chb_send_mail_on_error = Checkbutton( master = error_group,
                                          variable = val_chb_send_mail_on_error,
                                          command = lambda: main_self.set_send_mail_on_error( val_chb_send_mail_on_error.get() ) )
    chb_send_mail_on_error.grid( column = 1, row = 0, sticky = ( W, E ) )
    main_self.settings_ui[ 'chbSendMailOnError' ] = chb_send_mail_on_error

    tt = AlwaysOnTopToolTip( widget = chb_send_mail_on_error, msg = _( 'Should an mail be sent to its developer if an error occurs in the script?' ) )
    main_self.app_context.language_manager.add_translatable_widget( ( tt, 'Should an mail be sent to its developer if an error occurs in the script?' , False ) )

    row += 1

    error_group.rowconfigure( index = row, weight = 0 )
    chb_include_screenshot_in_errormail_title = Label( master = error_group, text = _( 'Include screenshot in mail when reporting error' ), padding = ( 5, 10 ) )
    chb_include_screenshot_in_errormail_title.grid( column = 0, row = row, sticky = ( W, E ) )
    main_self.app_context.language_manager.add_translatable_widget( ( chb_include_screenshot_in_errormail_title, 'Include screenshot in mail when reporting error' ) )

    val_chb_include_ss_in_error_mail = BooleanVar( value = main_self.app_state.settings.get( 'include_ss_in_error_mail' ) )
    chb_include_screenshot_in_errormail = Checkbutton( master = error_group,
                                                      variable = val_chb_include_ss_in_error_mail,
                                                      command = lambda: main_self.set_include_ss_in_error_mail( val_chb_include_ss_in_error_mail.get() ) )
    chb_include_screenshot_in_errormail.grid( column = 1, row = row, sticky = ( W, E ) )
    main_self.settings_ui[ 'chbIncludeSsInErrorMail' ] = chb_include_screenshot_in_errormail

    tt = AlwaysOnTopToolTip( widget = chb_include_screenshot_in_errormail, msg = _( 'Should the mail sent to script developer when reporting that an error occured, have a screenshot of main window attached?' ) )
    main_self.app_context.language_manager.add_translatable_widget( ( tt, 'Should the mail sent to script developer when reporting that an error occured, have a screenshot of main window attached?' , False ) )

    if not val_chb_send_mail_on_error.get():
        chb_include_screenshot_in_errormail.config( state = 'disabled' )

