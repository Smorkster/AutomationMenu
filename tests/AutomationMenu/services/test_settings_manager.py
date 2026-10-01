"""
Test cases for settings manager

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


import json
import pytest

from collections import Counter
from pathlib import Path
from tkinter.ttk import Frame, Notebook
from unittest.mock import Mock, call, patch

from automation_menu.core.app_context import ApplicationContext
from automation_menu.models.enums import OutputStyleTags
from automation_menu.models.settings import Settings
from automation_menu.services.settings_manager import SettingsManager
from automation_menu.types.rawsettings import RawSettings
from automation_menu.ui.types.settings_ui import SettingsUi


class TestCreate:

    def test_creation_loads_settings_from_given_path( self, app_context: ApplicationContext, tmp_path: Path ) -> None:
        """ Store app context and call read_saved_settings with the path.
        
        Args:
            app_context (ApplicationContext): Fixture for an ApplicationContext instance
            tmp_path (Path): A temporary directory
        """

        p: str = str( tmp_path / 'settings.json' )

        with patch.object( SettingsManager, 'read_saved_settings' ) as read:
            m: SettingsManager = SettingsManager( app_context = app_context, settings_file_path = p )

            read.assert_called_once_with( settings_file_path = p )

        assert m._app_context is app_context


class TestReadSettings:

    def test_read_settings_uses_path_and_debug_logger( self, settings_manager: SettingsManager, tmp_path: Path ) -> None:
        """ Pass the requested path and app context logger to the reader.

        Args:
            settings_manager (SettingsManager): Fixture of an SettingsManager instance
            tmp_path (Path): Temporary directory
        """

        p: Path = tmp_path / 'tmp_settings.json'

        with ( patch( 'automation_menu.services.settings_manager.read_settingsfile', return_value = { 'a': 1 } ) as read,
              patch( 'automation_menu.services.settings_manager.Settings' ) as settings,
              patch.object( settings_manager, 'save_settings' ) as save_callback ):

            settings.return_value.get_setting_errors.return_value = []
            settings_manager.read_saved_settings( settings_file_path = str( p ) )

            read.assert_called_once_with( settings_file_path = str( p ),
                                         debug_logger = settings_manager._app_context.debug_logger )
            settings.assert_called_once_with( settings_dict = read.return_value,
                                             save_callback = save_callback )
            settings.return_value.get_setting_errors.assert_called_once()

        assert settings_manager._settings_file_path == p


    def test_read_settings_creates_stores_and_returns_settings( self, settings_manager: SettingsManager, tmp_path: Path ) -> None:
        """ Wrap the loaded data in Settings and return the stored instance.
        
        Args:
            settings_manager (SettingsManager): Fixture of an SettingsManager instance
            tmp_path (Path): Temporary directory
        """

        module: str = 'automation_menu.services.settings_manager'
        p: Path = tmp_path / 'settings.json'
        rs_string: str = '{"current_language": "sv_SE","force_focus_post_execution": false, "include_ss_in_error_mail": false, "minimize_on_running": false, "on_top": false, "send_mail_on_error": false, "keepass_shortcut": {"ctrl": true, "alt": false, "shift": false, "key": "A"}}'
        rs: RawSettings = RawSettings( **json.loads( rs_string ) )

        with patch( f'{ module }.read_settingsfile', return_value = rs ) as read:
            s: Settings = settings_manager.read_saved_settings( settings_file_path = str( p ) )

            assert isinstance( s, Settings )
            assert settings_manager.settings.current_language == s.current_language == 'sv_SE'
            assert settings_manager.settings is s


    def test_read_settings_registers_save_callback( self, settings_manager: SettingsManager, tmp_path: Path ) -> None:
        """ Supply the manager's save_settings method to Settings.

        Args:
            settings_manager (SettingsManager): Fixture of an SettingsManager instance
            tmp_path (Path): Temporary directory
        """

        p: Path = tmp_path / 'settings.json'

        with ( patch.object( settings_manager, 'save_settings' ),
              patch( 'automation_menu.services.settings_manager.read_settingsfile' ) ):
            s: Settings = settings_manager.read_saved_settings( settings_file_path = str( p ) )

            assert s._save_callback == settings_manager.save_settings


    def test_read_settings_stores_file_path( self, settings_manager: SettingsManager, tmp_path: Path ) -> None:
        """ Store the supplied settings-file path as a Path.

        Args:
            settings_manager (SettingsManager): Fixture of an SettingsManager instance
            tmp_path (Path): Temporary directory
        """

        p: Path = tmp_path / 'new_settings.json'

        with patch( 'automation_menu.services.settings_manager.read_settingsfile' ):
            settings_manager.read_saved_settings( str( p ) )

            assert settings_manager._settings_file_path == p


    @pytest.mark.parametrize( 'errors', [ pytest.param( [], id = 'no-errors' ),
                                         pytest.param( [ 'Invalid setting' ], id = 'one-error' ),
                                         pytest.param( [ 'First error', 'Second error'], id = 'multiple-errors' ) ] )
    def test_read_settings_reports_validation_errors( self, settings_manager: SettingsManager, errors: list[ str ], app_context: Mock, tmp_path: Path ) -> None:
        """ Queue each error with SYSERROR; queue nothing when none exist.

        Args:
            settings_manager (SettingsManager): Fixture of an SettingsManager instance
            errors (list[ str ]): Errors defined for invalid settings
            app_context (Mock): Fixture of an ApplicationContext instance
            tmp_path (Path): Temporary path
        """

        p: Path = tmp_path / 'settings.json'

        module: str = 'automation_menu.services.settings_manager'

        with ( patch( f'{ module }.read_settingsfile', return_value = {} ),
              patch( f'{ module }.Settings' ) as settings ):
            settings.return_value.get_setting_errors.return_value = errors
            settings_manager.read_saved_settings( settings_file_path = str( p ) )

            if errors:
                app_context.OutputQueue.put.assert_called()

                expected_calls = [ call( { 'line': error, 'tag': OutputStyleTags.SYSERROR } )
                                  for error in errors ]

                assert app_context.OutputQueue.put.call_args_list == expected_calls

            else:
                app_context.OutputQueue.put.assert_not_called()


class TestUi:

    def test_collect_callbacks_uses_app_context_methods( self, settings_manager: SettingsManager ) -> None:
        """ Collect menu rebuild, script discovery, and script-list callbacks.

        Args:
            settings_manager (SettingsManager): Fixture of an SettingsManager instance
        """

        rebuild = Mock()
        gather = Mock()
        get = Mock()

        settings_manager._app_context.main_window.menu_buttons.script_menu.rebuild_menu = rebuild
        settings_manager._app_context.ScriptManager.gather_scripts = gather
        settings_manager._app_context.ScriptManager.get_script_list = get

        settings_manager._collect_op_callbacks()

        assert settings_manager._op_callbacks.clear_script_menu == rebuild
        assert settings_manager._op_callbacks.gather_script_info == gather
        assert settings_manager._op_callbacks.get_script_list == get


    def test_create_tab_stores_and_returns_created_frame( self, settings_manager: SettingsManager ) -> None:
        """ Pass notebook and translation callback to create_settings_tab.

        Args:
            settings_manager (SettingsManager): Fixture of an SettingsManager instance
        """

        m_tab: Notebook = Mock( spec = Notebook )
        m_callback: Mock = Mock()

        with patch( 'automation_menu.services.settings_manager.create_settings_tab', return_value = Mock( spec = Frame ) ) as create:
            settings_manager._app_context.LanguageManager.add_translatable_widget = m_callback
            t: Frame = settings_manager.create_tab( parent_notebook = m_tab )

            create.assert_called_once_with( tab_control = m_tab,
                                           translate_store_callback = m_callback )

        assert t is create.return_value
        assert settings_manager._tab is create.return_value


    def test_build_tab_content_creates_controller_with_dependencies( self, settings_manager: SettingsManager ) -> None:
        """ Supply settings, root window, language callback, and operations.

        Args:
            settings_manager (SettingsManager): Fixture of an SettingsManager instance
        """

        module: str = 'automation_menu.services.settings_manager'

        with ( patch( f'{ module }.SettingsUiController' ) as controller,
              patch( f'{ module }.build_settings' ),
              patch.object( settings_manager, '_collect_op_callbacks' ) ):

            settings_manager.settings = Mock()
            settings_manager._op_callbacks = Mock()
            settings_manager._tab = Mock( spec = Frame )
            settings_manager.build_tab_content()

            controller.assert_called_once_with( settings = settings_manager.settings,
                                               root_window = settings_manager._app_context.main_window.root,
                                               change_app_language = settings_manager._app_context.LanguageManager.change_app_language,
                                               op_callbacks = settings_manager._op_callbacks )

            assert settings_manager.settings_ui_controller is controller.return_value


    def test_build_tab_content_builds_stores_and_returns_ui( self, settings_manager: SettingsManager ) -> None:
        """ Pass dependencies to build_settings and return its result.

        Args:
            settings_manager (SettingsManager): Fixture of an SettingsManager instance
        """

        module: str = 'automation_menu.services.settings_manager'

        with ( patch( f'{ module }.build_settings', return_value = Mock( spec = SettingsUi ), ) as build,
              patch( f'{ module }.SettingsUiController' ) ):

            settings_manager.settings = Mock()
            settings_manager._tab = Mock()
            returned_ui = settings_manager.build_tab_content()

            build.assert_called_once_with( tab = settings_manager._tab,
                                          settings = settings_manager.settings,
                                          settings_ui_controller = settings_manager.settings_ui_controller,
                                          add_translatable = settings_manager._app_context.LanguageManager.add_translatable_widget )

            assert returned_ui is build.return_value
            assert settings_manager.settings_ui is build.return_value


    def test_build_tab_content_binds_ui_to_controller( self, settings_manager: SettingsManager ) -> None:
        """ Bind the newly created UI to the settings controller.

        Args:
            settings_manager (SettingsManager): Fixture of an SettingsManager instance
        """

        module: str = 'automation_menu.services.settings_manager'

        with ( patch( f'{ module }.build_settings', return_value = Mock( spec = SettingsUi ) ) as build,
              patch( f'{ module }.SettingsUiController' ) as controller,
              patch( f'{ module }.SettingsUiCallbacks' ) ):
            settings_manager.settings = Mock()
            settings_manager._tab = Mock()
            settings_manager.build_tab_content()

            controller.return_value.bind_ui.assert_called_once_with( settings_ui = build.return_value )


class TestSaveSettings:

    def test_save_settings_writes_given_object_to_stored_path( self, settings_manager: SettingsManager, tmp_path: Path ) -> None:
        """ Pass the supplied Settings object and string path to the writer.

        Args:
            settings_manager (SettingsManager): Fixture of an SettingsManager instance
            tmp_path (Path): Temporary directory
        """

        m_settings: Settings = Mock( spec = Settings )
        p: Path = tmp_path / 'settings.json'

        settings_manager._settings_file_path = p

        with patch( 'automation_menu.services.settings_manager.write_settingsfile' ) as write:
            settings_manager.save_settings( m_settings )

            write.assert_called_once_with( settings = m_settings,
                                          settings_file_path = str( p ) )


class TestScriptFolders:

    @pytest.mark.parametrize( 'already_present',
                             [ pytest.param( False, id = 'adds-missing-folder' ),
                              pytest.param( True, id = 'does-not-duplicate-folder' ) ] )
    def test_main_script_folder_is_present_once( self, settings_manager: SettingsManager, already_present: bool, tmp_path: Path ) -> None:
        """ Ensure the requested folder is stored as a Path exactly once.

        Args:
            settings_manager (SettingsManager): Fixture of an SettingsManager instance
            already_present (bool): Is folder present in script folder list
            tmp_path (Path): Temporary directory
        """

        settings_manager.settings = Mock( spec = Settings )
        settings_manager.settings.script_folders = [ Path( 'C:\\Folder1' ), Path( 'C:\\Folder2' ) ]

        if already_present:
            settings_manager.settings.script_folders.append( tmp_path )

        settings_manager.test_add_main_script_folder( main_script_folder = str( tmp_path ) )

        assert tmp_path in settings_manager.settings.script_folders

        counted = Counter( settings_manager.settings.script_folders )[ tmp_path ]
        assert counted == 1


    def test_adding_main_script_folder_preserves_other_folders( self, settings_manager: SettingsManager, tmp_path: Path ) -> None:
        """ Keep existing folder entries when adding the main script folder.

        Args:
            settings_manager (SettingsManager): Fixture of an SettingsManager instance
            tmp_path (Path): Temporary directory
        """

        f1: Path = Path( 'C:\\Folder1' )
        f2: Path = Path( 'C:\\Folder2' )
        settings_manager.settings = Mock( spec = Settings )
        settings_manager.settings.script_folders = [ f1, f2 ]

        settings_manager.test_add_main_script_folder( str( tmp_path ) )

        assert f1 in settings_manager.settings.script_folders
        assert f2 in settings_manager.settings.script_folders
        assert settings_manager.settings.script_folders == [ f1, f2, tmp_path ]
