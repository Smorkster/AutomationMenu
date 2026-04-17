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
from typing import TYPE_CHECKING, Callable, TypedDict


if TYPE_CHECKING:
    from automation_menu.ui.main_window import AutomationMenuWindow

from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
from tkinter import E, N, S, W, BooleanVar, StringVar
from tkinter.ttk import Checkbutton, Combobox, Entry, Frame, Label, LabelFrame, Notebook

from automation_menu.models import Settings
from automation_menu.models.widget_for_translation import WidgetForTranslation


class SettingsUiDict( TypedDict ):
    """ Defined dict for settings widgets """

    chbTopMost: Checkbutton
    chbMinimizeOnRunning: Checkbutton
    chb_force_focus_post_execution: Checkbutton
    cmbCurrentLanguage: Combobox
    keepass_shortcut_ctrl: Checkbutton
    keepass_shortcut_ctrl_val: BooleanVar
    keepass_shortcut_alt: Checkbutton
    keepass_shortcut_alt_val: BooleanVar
    keepass_shortcut_shift: Checkbutton
    keepass_shortcut_shift_val: BooleanVar
    keepass_shortcut_key: Entry
    keepass_shortcut_key_val: StringVar
    chbSendMailOnError: Checkbutton
    chbIncludeSsInErrorMail: Checkbutton


def build_settings( tab: Frame, settings: Settings, main_self: AutomationMenuWindow ) -> SettingsUiDict:
    """ Create widgets for application settings

    Args:
        tab (Frame): Frame to place settings widgets in
        settings (Settings): Collection of settings data
        main_self (AutomationMenuWindow): Main object
    """

    from automation_menu.utils.localization import _, get_available_languages

    settings_ui: dict = {}
    tab.columnconfigure( index = 0, weight = 1 )

    ######################
    # Application settings
    tab_frame_row: int = 0

    app_settings_group_title: Label = Label( text=_( 'Application settings' ), style = 'LabelFrameTitle.TLabel' )
    app_settings_group: LabelFrame = LabelFrame( master = tab, labelwidget = app_settings_group_title )
    app_settings_group.grid( column = 0, row = tab_frame_row, sticky = 'nwe' )
    app_settings_group.grid_columnconfigure( index = 0, weight = 0, uniform = 'titles' )
    app_settings_group.grid_columnconfigure( index = 1, weight = 1, uniform = 'values' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = app_settings_group_title, default_text = 'Application settings' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    row: int = 0

    app_settings_group.rowconfigure( index = row, weight = 0 )
    chb_on_top_title: Label = Label( master = app_settings_group, text = _( 'Set as topmost window' ), padding = ( 5, 10 ) )
    chb_on_top_title.grid( column = 0, row = row, sticky = 'we' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = chb_on_top_title, default_text = 'Set as topmost window' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    val_chb_on_top: BooleanVar = BooleanVar( value = settings.on_top )
    chb_on_top: Checkbutton = Checkbutton( master = app_settings_group,
                             variable = val_chb_on_top,
                             command = lambda: main_self.set_on_top( val_chb_on_top.get() ) )
    chb_on_top.grid( column = 1, row = row, sticky = 'nw' )
    settings_ui[ 'chbTopMost' ] = chb_on_top

    tt: AlwaysOnTopToolTip = AlwaysOnTopToolTip( widget = chb_on_top, msg = _ ( 'Shall the window be set as topmost, above all other windows' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = tt, default_text = 'Shall the window be set as topmost, above all other windows' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    row += 1

    app_settings_group.rowconfigure( index = row, weight = 0 )
    chb_minimize_on_running_title: Label = Label( master = app_settings_group, text = _( 'Minimize size during script execution' ), padding = ( 5, 10 ) )
    chb_minimize_on_running_title.grid( column = 0, row = row, sticky = 'we' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = chb_minimize_on_running_title, default_text = 'Minimize size during script execution' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    val_chb_minimize_on_running: BooleanVar = BooleanVar( value = settings.minimize_on_running )
    chb_minimize_on_running: Checkbutton = Checkbutton( master = app_settings_group,
                                          variable = val_chb_minimize_on_running,
                                          command = lambda: main_self.set_minimize_on_running( val_chb_minimize_on_running.get() ) )
    chb_minimize_on_running.grid( column = 1, row = row, sticky = 'nw' )
    settings_ui[ 'chbMinimizeOnRunning' ] = chb_minimize_on_running

    tt: AlwaysOnTopToolTip = AlwaysOnTopToolTip( widget = chb_minimize_on_running, msg = _( 'Downsize the window during script execution, trying not to be in its way. This setting can be ignored in ScriptInfo-block with \'DisableMinimizeOnRunning\'.' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = tt, default_text = 'Downsize the window during script execution, trying not to be in its way. This setting can be ignored in ScriptInfo-block with \'DisableMinimizeOnRunning\'.' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    row += 1

    app_settings_group.rowconfigure( index = row, weight = 0 )
    chb_force_focus_post_execution_title: Label = Label( master = app_settings_group, text = _( 'Main window focus post execution' ), padding = ( 5, 10 ) )
    chb_force_focus_post_execution_title.grid( column = 0, row = row, sticky = 'we' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = chb_force_focus_post_execution_title, default_text = 'Main window focus post execution' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    val_chb_force_focus_post_execution: BooleanVar = BooleanVar( value = settings.force_focus_post_execution )
    chb_force_focus_post_execution: Checkbutton = Checkbutton( master = app_settings_group,
                                          variable = val_chb_force_focus_post_execution,
                                          command = lambda: main_self.set_force_focus_post_execution( val_chb_force_focus_post_execution.get() ) )
    chb_force_focus_post_execution.grid( column = 1, row = row, sticky = 'nw' )
    settings_ui[ 'chb_force_focus_post_execution' ] = chb_force_focus_post_execution

    tt: AlwaysOnTopToolTip = AlwaysOnTopToolTip( widget = chb_force_focus_post_execution, msg = _( 'Should the main window be forced back to focus after execution of script or sequence have finished' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = tt, default_text = 'Should the main window be forced back to focus after execution of script or sequence have finished' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    row += 1

    app_settings_group.rowconfigure( index = row, weight = 0 )
    cmb_current_language_title: Label = Label( master = app_settings_group, text = _( 'Application language' ), padding = ( 5, 10 ) )
    cmb_current_language_title.grid( column = 0, row = row, sticky = 'nw' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = cmb_current_language_title, default_text = 'Application language' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    val_cmb_current_language: StringVar = StringVar()
    cmb_current_language: Combobox = Combobox( master = app_settings_group,
                                              values = get_available_languages(),
                                              textvariable = val_cmb_current_language )
    cmb_current_language.bind( '<<ComboboxSelected>>', main_self.set_current_language )
    cmb_current_language.grid( column = 1, row = row, padx = 5, pady = 5, sticky = 'we' )

    if settings.current_language in cmb_current_language[ 'values' ]:
        val_cmb_current_language.set( settings.current_language )

    else:
        val_cmb_current_language.set( cmb_current_language[ 'values' ][ 0 ] )

    settings_ui[ 'cmbCurrentLanguage' ] = cmb_current_language
    settings_ui[ 'cmbCurrentLanguage_val' ] = val_cmb_current_language

    tt: AlwaysOnTopToolTip = AlwaysOnTopToolTip( widget = cmb_current_language, msg = _( 'Language to use in the application' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = tt, default_text = 'Language to use in the application' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    row += 1

    app_settings_group.rowconfigure( index = row, weight = 0 )
    keepass_shortcut_title: Label = Label( master = app_settings_group, text = _( 'KeePass shortcut' ), padding = ( 5, 10 ) )
    keepass_shortcut_title.grid( column = 0, row = row, sticky = 'nw' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = keepass_shortcut_title, default_text = 'KeePass shortcut' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    keepass_shortcut_value_frame: Frame = Frame( master = app_settings_group )
    keepass_shortcut_value_frame.grid( column = 1, row = row, sticky = 'nwe' )

    val_keepass_shortcut_ctrl: BooleanVar = BooleanVar( value = main_self.app_state.settings.keepass_shortcut.get( 'ctrl' ) )
    keepass_shortcut_ctrl: Checkbutton = Checkbutton( master = keepass_shortcut_value_frame,
                                        text = _( 'CTRL' ),
                                        variable = val_keepass_shortcut_ctrl,
                                        command = lambda: main_self.app_state.settings.set_keepass_shortcut( shortcut_key = 'ctrl', shortcut_val = val_keepass_shortcut_ctrl.get() ) )
    keepass_shortcut_ctrl.grid( column = 0, row = 0, sticky = 'nw' )
    settings_ui[ 'keepass_shortcut_ctrl' ] = keepass_shortcut_ctrl
    settings_ui[ 'keepass_shortcut_ctrl_val' ] = val_keepass_shortcut_ctrl

    wft: WidgetForTranslation = WidgetForTranslation( widget = keepass_shortcut_ctrl, default_text = 'CTRL' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    val_keepass_shortcut_alt: BooleanVar = BooleanVar( value = main_self.app_state.settings.keepass_shortcut.get( 'alt' ) )
    keepass_shortcut_alt: Checkbutton = Checkbutton( master = keepass_shortcut_value_frame,
                                       text = _( 'ALT' ),
                                       variable = val_keepass_shortcut_alt,
                                       command = lambda : main_self.app_state.settings.set_keepass_shortcut( shortcut_key = 'alt', shortcut_val = val_keepass_shortcut_alt.get() ) )
    keepass_shortcut_alt.grid( column = 1, row = 0, sticky = 'nw' )
    settings_ui[ 'keepass_shortcut_alt' ] = keepass_shortcut_alt
    settings_ui[ 'keepass_shortcut_alt_val' ] = val_keepass_shortcut_alt

    wft: WidgetForTranslation = WidgetForTranslation( widget = keepass_shortcut_alt, default_text = 'ALT' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    val_keepass_shortcut_shift: BooleanVar = BooleanVar( value = main_self.app_state.settings.keepass_shortcut.get( 'shift' ) )
    keepass_shortcut_shift: Checkbutton = Checkbutton( master = keepass_shortcut_value_frame,
                                         text = _( 'Shift' ),
                                         variable = val_keepass_shortcut_shift,
                                         command = lambda *args: main_self.app_state.settings.set_keepass_shortcut( shortcut_key = 'shift', shortcut_val = val_keepass_shortcut_shift.get() ) )
    keepass_shortcut_shift.grid( column = 2, row = 0, sticky = 'nw' )
    settings_ui[ 'keepass_shortcut_shift' ] = keepass_shortcut_shift
    settings_ui[ 'keepass_shortcut_shift_val' ] = val_keepass_shortcut_shift

    wft: WidgetForTranslation = WidgetForTranslation( widget = keepass_shortcut_shift, default_text = 'Shift' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    val_keepass_shortcut_key: StringVar = StringVar( value = main_self.app_state.settings.keepass_shortcut.get( 'key' ) )
    keepass_shortcut_key: Entry = Entry( master = keepass_shortcut_value_frame,
                                 textvariable = val_keepass_shortcut_key )
    val_keepass_shortcut_key.trace_add( mode = 'write', callback = lambda *args: main_self.app_state.settings.set_keepass_shortcut( shortcut_key = 'key', shortcut_val = val_keepass_shortcut_key.get() ) )
    keepass_shortcut_key.grid( column = 3, row = 0, padx = 5, pady = 5, sticky = ( W ) )
    settings_ui[ 'keepass_shortcut_key' ] = keepass_shortcut_key
    settings_ui[ 'keepass_shortcut_key_val' ] = val_keepass_shortcut_key

    tt: AlwaysOnTopToolTip = AlwaysOnTopToolTip( widget = keepass_shortcut_key, msg = _( 'Shortcut used to activate KeePass for auto typing' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = tt, default_text = 'Shortcut used to activate KeePass for auto typing' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )


    ###############
    # Errorhandling
    tab_frame_row += 1

    error_group_title: Label = Label( text = _( 'Errorhandling' ), style = 'LabelFrameTitle.TLabel' )
    error_group: LabelFrame = LabelFrame( tab, labelwidget = error_group_title )
    error_group.grid_columnconfigure( index = 0, weight = 0, uniform = 'titles' )
    error_group.grid_columnconfigure( index = 1, weight = 1, uniform = 'values' )
    error_group.grid( column = 0, row = tab_frame_row, sticky = 'nwe' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = error_group_title, default_text = 'Errorhandling' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    row: int = 0

    error_group.rowconfigure( index = row, weight = 0 )
    chb_send_mail_on_error_title: Label = Label( master = error_group, text = _( 'Send mail to developer on script error' ), padding = ( 5, 10 ) )
    chb_send_mail_on_error_title.grid( column = 0, row = row, sticky = 'we' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = chb_send_mail_on_error_title, default_text = 'Send mail to developer on script error' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    val_chb_send_mail_on_error: BooleanVar = BooleanVar( value = main_self.app_state.settings.send_mail_on_error )
    chb_send_mail_on_error: Checkbutton = Checkbutton( master = error_group,
                                          variable = val_chb_send_mail_on_error,
                                          command = lambda: main_self.set_send_mail_on_error( val_chb_send_mail_on_error.get() ) )
    chb_send_mail_on_error.grid( column = 1, row = 0, sticky = 'we' )
    settings_ui[ 'chbSendMailOnError' ] = chb_send_mail_on_error

    tt: AlwaysOnTopToolTip = AlwaysOnTopToolTip( widget = chb_send_mail_on_error, msg = _( 'Should an mail be sent to its developer if an error occurs in the script?' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = tt, default_text = 'Should an mail be sent to its developer if an error occurs in the script?' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    row += 1

    error_group.rowconfigure( index = row, weight = 0 )
    chb_include_screenshot_in_errormail_title: Label = Label( master = error_group, text = _( 'Include screenshot in mail when reporting error' ), padding = ( 5, 10 ) )
    chb_include_screenshot_in_errormail_title.grid( column = 0, row = row, sticky = 'we' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = chb_include_screenshot_in_errormail_title, default_text = 'Include screenshot in mail when reporting error' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    val_chb_include_ss_in_error_mail: BooleanVar = BooleanVar( value = main_self.app_state.settings.include_ss_in_error_mail )
    chb_include_screenshot_in_errormail: Checkbutton = Checkbutton( master = error_group,
                                                      variable = val_chb_include_ss_in_error_mail,
                                                      command = lambda: main_self.set_include_ss_in_error_mail( val_chb_include_ss_in_error_mail.get() ) )
    chb_include_screenshot_in_errormail.grid( column = 1, row = row, sticky = 'we' )
    settings_ui[ 'chbIncludeSsInErrorMail' ] = chb_include_screenshot_in_errormail

    tt: AlwaysOnTopToolTip = AlwaysOnTopToolTip( widget = chb_include_screenshot_in_errormail, msg = _( 'Should the mail sent to script developer when reporting that an error occured, have a screenshot of main window attached?' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = tt, default_text = 'Should the mail sent to script developer when reporting that an error occured, have a screenshot of main window attached?' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    if not val_chb_send_mail_on_error.get():
        chb_include_screenshot_in_errormail.config( state = 'disabled' )

    return {
        'chbTopMost': chb_on_top,
        'chbMinimizeOnRunning': chb_minimize_on_running,
        'chb_force_focus_post_execution': chb_force_focus_post_execution,
        'cmbCurrentLanguage': cmb_current_language,
        'keepass_shortcut_ctrl': keepass_shortcut_ctrl,
        'keepass_shortcut_ctrl_val': val_keepass_shortcut_ctrl,
        'keepass_shortcut_alt': keepass_shortcut_alt,
        'keepass_shortcut_alt_val': val_keepass_shortcut_alt,
        'keepass_shortcut_shift': keepass_shortcut_shift,
        'keepass_shortcut_shift_val': val_keepass_shortcut_shift,
        'keepass_shortcut_key': keepass_shortcut_key,
        'keepass_shortcut_key_val': val_keepass_shortcut_key,
        'chbSendMailOnError': chb_send_mail_on_error,
        'chbIncludeSsInErrorMail': chb_include_screenshot_in_errormail
    }


def get_settings_tab( tabcontrol: Notebook, translate_store_callback: Callable ) -> Frame:
    """ Create a frame used as a tab to collect settings

    Args:
        tabcontrol (Notebook): Tabcontrol (Notebook) to place the frame in
        translate_store_callback (Callable): Function callback to store widget for translation
    """

    from automation_menu.utils.localization import _

    tabSettings: Frame = Frame( tabcontrol , padding = ( 5, 5, 5, 5 ), name = 'settings' )
    tabSettings.grid( sticky = 'nsew' )

    tabcontrol.add( child = tabSettings, text = _( 'Settings' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = tabSettings, default_text = 'Settings' )
    translate_store_callback( wft )

    return tabSettings
