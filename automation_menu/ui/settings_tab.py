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
from typing import TYPE_CHECKING, Callable, cast

from automation_menu.models.settings_ui_dict import SettingsUiDict


if TYPE_CHECKING:
    from automation_menu.ui.main_window import AutomationMenuWindow

from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
from tkinter import BooleanVar, Canvas, Event, StringVar
from tkinter.ttk import Button, Checkbutton, Combobox, Entry, Frame, Label, LabelFrame, Notebook, Scrollbar, Treeview

from automation_menu.models import Settings
from automation_menu.models.widget_for_translation import WidgetForTranslation


def build_settings( tab: Frame, settings: Settings, main_self: AutomationMenuWindow ) -> SettingsUiDict:
    """ Create widgets for application settings

    Args:
        tab (Frame): Frame to place settings widgets in
        settings (Settings): Collection of settings data
        main_self (AutomationMenuWindow): Main object
    """

    from automation_menu.utils.localization import _, get_available_languages


    def _refresh_scrollregion() -> None:
        """ Refresh the canvas scrollregion after geometry updates settle. """

        bbox: tuple[ int, int, int, int ] | None = container_canvas.bbox( 'all' )

        if bbox is not None:
            container_canvas.configure( scrollregion = bbox )


    def _on_canvas_config( event: Event ) -> None:
        """ Update canvas width when canvas window changes

        Args:
            event (Event): Event triggering this handler
        """

        container_canvas.itemconfig( window_id, width = event.width )
        container_canvas.after_idle( _refresh_scrollregion )


    def _on_frame_config( event: Event ) -> None:
        """ Update scrollregion when frame region changes

        Args:
            event (Event): Event triggering this handler
        """

        container_canvas.after_idle( _refresh_scrollregion )


    def _on_mousewheel( event: Event ) -> None:
        """ Bind mouse wheel scrolling

        Args:
            event (Event): Event triggering this handler
        """

        delta: int = getattr( event, 'delta', 0 )

        if delta == 0:
            return

        step_count: int = max( 1, abs( delta ) // 120 )
        direction: int = -1 if delta > 0 else 1
        container_canvas.yview_scroll( direction * step_count, 'units' )


    def _on_tree_select( event: Event ) -> None:
        """ Enable or disable the script-folder remove button based on selection.

        Args:
            event (Event): Treeview selection event.
        """

        w: Treeview = cast( Treeview, event.widget )
        if len( w.selection() ) > 0:
            script_folder_btn_remove.config( state = '!disabled' )

        else:
            script_folder_btn_remove.config( state = 'disabled' )


    settings_ui: dict = {}
    frame_root: Frame = Frame( master = tab )
    frame_root.grid( column = 0, columnspan=2, row = 0, sticky = 'nswe' )
    frame_root.columnconfigure( index = 0, weight = 1 )
    frame_root.columnconfigure( index = 1, weight = 0 )
    frame_root.rowconfigure( index = 0, weight = 1 )

    container_canvas: Canvas = Canvas( master = frame_root, highlightthickness = 0 )
    container_canvas.grid( sticky = 'nswe' )
    container_canvas.grid_columnconfigure( index = 0, weight = 1 )

    container_scrollbar: Scrollbar = Scrollbar( master = frame_root, orient = 'vertical', command = container_canvas.yview )
    container_scrollbar.grid( column = 1, row = 0, sticky = 'ns' )

    container_canvas.configure( yscrollcommand = container_scrollbar.set )

    settings_widget_container: Frame = Frame( master = container_canvas )
    settings_widget_container.columnconfigure( index = 0, weight = 1 )
    window_id: int = container_canvas.create_window( ( 0, 0 ), window = settings_widget_container, anchor = 'nw' )

    settings_widget_container.bind( '<Configure>', _on_frame_config )
    container_canvas.bind( '<Configure>', _on_canvas_config )
    container_canvas.bind_all( '<MouseWheel>', _on_mousewheel )

    ######################
    # Application settings
    tab_frame_row: int = 0

    app_settings_group_title: Label = Label( text=_( 'Application settings' ), style = 'LabelFrameTitle.TLabel' )
    app_settings_group: LabelFrame = LabelFrame( master = settings_widget_container, labelwidget = app_settings_group_title )
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
    cmb_current_language.grid( column = 1, columnspan = 2, row = row, padx = 5, pady = 5, sticky = 'we' )

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
    keepass_shortcut_key.grid( column = 3, row = 0, padx = 5, pady = 5, sticky = 'w' )
    settings_ui[ 'keepass_shortcut_key' ] = keepass_shortcut_key
    settings_ui[ 'keepass_shortcut_key_val' ] = val_keepass_shortcut_key

    tt: AlwaysOnTopToolTip = AlwaysOnTopToolTip( widget = keepass_shortcut_key, msg = _( 'Shortcut used to activate KeePass for auto typing' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = tt, default_text = 'Shortcut used to activate KeePass for auto typing' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    row += 1

    app_settings_group.rowconfigure( index = row, weight = 0 )
    script_folders_title: Label = Label( master = app_settings_group, text = _( 'Script folders' ), padding = ( 5, 10 ) )
    script_folders_title.grid( column = 0, row = row, sticky = 'nw' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = script_folders_title, default_text = 'Script folders' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    script_folders_list: Treeview = Treeview( master = app_settings_group,
                                             columns = ( 'name', 'path' ),
                                             displaycolumns = 'name',
                                             show = '',
                                             selectmode = 'browse',
                                             height = 5
                                             )
    for f in settings.script_folders:
        folder_id: str = script_folders_list.insert( parent = '',
                                                    index = 'end',
                                                    text = str( f ),
                                                    values = [ f ] )
    script_folders_list.column( 'name', anchor = 'w' )
    script_folders_list.grid( column = 1, row = row, rowspan = 2, sticky = 'we' )
    script_folders_list.bind( '<<TreeviewSelect>>', _on_tree_select )
    settings_ui[ 'script_folders_list' ] = script_folders_list

    script_folder_btn_add: Button = Button( master = app_settings_group, text = _( 'Add' ) )
    script_folder_btn_add.grid( column = 2, row = row, sticky = 'nw' )

    row += 1

    script_folder_btn_remove: Button = Button( master = app_settings_group, text = _( 'Remove' ) )
    script_folder_btn_remove.grid( column = 2, row = row, sticky = 'nw' )
    script_folder_btn_remove.config( default = 'disabled' )
    tt: AlwaysOnTopToolTip = AlwaysOnTopToolTip( widget = keepass_shortcut_key, msg = _( 'Shortcut used to activate KeePass for auto typing' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = tt, default_text = 'Shortcut used to activate KeePass for auto typing' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )



    ###############
    # Errorhandling
    tab_frame_row += 1

    error_group_title: Label = Label( text = _( 'Errorhandling' ), style = 'LabelFrameTitle.TLabel' )
    error_group: LabelFrame = LabelFrame( settings_widget_container, labelwidget = error_group_title )
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
        'chbIncludeSsInErrorMail': chb_include_screenshot_in_errormail,
        'script_folders_list': script_folders_list,
        'script_folder_btn_add': script_folder_btn_add,
        'script_folder_btn_remove': script_folder_btn_remove,
    }


def get_settings_tab( tabcontrol: Notebook, translate_store_callback: Callable ) -> Frame:
    """ Create a frame used as a tab to collect settings

    Args:
        tabcontrol (Notebook): Tabcontrol (Notebook) to place the frame in
        translate_store_callback (Callable): Function callback to store widget for translation
    """

    from automation_menu.utils.localization import _

    tabSettings: Frame = Frame( tabcontrol , padding = ( 5, 5, 5, 5 ), name = 'settings' )
    tabSettings.grid( sticky = 'nswe' )
    tabSettings.columnconfigure( index = 0, weight = 1 )
    tabSettings.rowconfigure( index = 0, weight = 1 )

    tabcontrol.add( child = tabSettings, text = _( 'Settings' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = tabSettings, default_text = 'Settings' )
    translate_store_callback( wft )

    return tabSettings
