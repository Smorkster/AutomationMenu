"""
Test cases for settings ui controller

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from pathlib import Path
from tkinter import Tk
from tkinter.ttk import Button, Combobox
from typing import Callable
from unittest.mock import Mock, patch

import pytest

from automation_menu.models.settings import Settings
from automation_menu.types.settings_ui_callbacks import SettingsUiCallbacks
from automation_menu.ui.controllers.settings_ui_controller import SettingsUiController


@pytest.fixture()
def module() -> str:
    """ Fixture for module path.
    
    Returns:
        (str): Module import path
    """

    return 'automation_menu.ui.controllers.settings_ui_controller'


@pytest.fixture
def settings_ui_controller() -> SettingsUiController:
    """ Test fixture to provide an SettingsUiControllerobject. """

    s: SettingsUiController = SettingsUiController.__new__( SettingsUiController )

    s.settings = Mock()
    s.settings_ui = Mock()
    s.root_window = Mock()
    s.change_app_language = Mock()
    s._settings_op_callbacks = Mock()

    return s


class TestCreation:

    def test_creation_stores_dependencies( self ) -> None:
        """ Store settings, root window, language callback, and operation callbacks. """

        s = Mock( spec = Settings )
        r = Mock( spec = Tk )
        c = Mock( spec = Callable )
        o = Mock( spec = SettingsUiCallbacks )

        suc = SettingsUiController( settings = s,
                                   root_window = r,
                                   change_app_language = c,
                                   op_callbacks = o )

        assert suc.settings is s
        assert suc.root_window is r
        assert suc.change_app_language is c
        assert suc._settings_op_callbacks is o


    def test_bind_ui_stores_widget_collection( self ) -> None:
        """ Store the exact SettingsUi instance supplied. """

        b = Mock()
        s = SettingsUiController.__new__( SettingsUiController )

        s.bind_ui( b )

        assert s.settings_ui is b


class TestScriptFolders:

    @pytest.mark.parametrize( 'has_tree', [ False, True ] )
    def test_add_new_folder_updates_settings_and_available_tree( self, settings_ui_controller: SettingsUiController, has_tree: bool ) -> None:
        """ Append the selected Path and insert a tree row when a tree exists.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
            has_tree (bool): True if testing with an available tree widget
        """

        tree = Mock()
        settings_ui_controller.settings_ui.script_folders_list = tree if has_tree else None
        settings_ui_controller.settings.script_folders = []

        with patch( 'automation_menu.ui.controllers.settings_ui_controller.filedialog' ) as fd:
            fd.askdirectory.return_value = 'C:\\'
            settings_ui_controller.add_script_folder()

            if has_tree:
                tree.insert.assert_called_once_with( parent = '',
                                                    index = 'end',
                                                    text = fd.askdirectory.return_value,
                                                    tags = 'exists' )

            else:
                tree.insert.assert_not_called()

            assert Path( fd.askdirectory.return_value ) in settings_ui_controller.settings.script_folders


    def test_add_existing_folder_does_not_duplicate_it( self, settings_ui_controller: SettingsUiController, module: str ) -> None:
        """ Leave settings and tree unchanged when the selected folder exists.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
            module (str): Fixture for module import path
        """

        settings_ui_controller.settings.script_folders = [ Path( 'C:\\' ) ]

        with ( patch( f'{ module }.filedialog' ) as fd,
              patch.object( settings_ui_controller.settings, 'script_folders' ) as list,
              patch.object( settings_ui_controller.settings_ui, 'script_folders_list' ) as list_w ):
            fd.askdirectory.return_value = 'C:\\'
            settings_ui_controller.add_script_folder()

            list.append.assert_not_called()
            list_w.insert.assert_not_called()


    @pytest.mark.parametrize( 'invalid_path', [ '', 'C:\\NonExising' ] )
    def test_cancel_folder_dialog_or_non_exising_path_leaves_settings_and_tree_unchanged( self, settings_ui_controller: SettingsUiController, module: str, invalid_path: str ) -> None:
        """ Do nothing when the folder dialog returns an empty string or non existing path.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
            module (str): Fixture for module import path
            invalid_path (str): Invalid path to test
        """

        settings_ui_controller.settings._script_folders = [ Path( 'C:\\' ) ]

        with ( patch( f'{ module }.filedialog' ) as fd,
              patch.object( settings_ui_controller.settings, 'script_folders' ) as list,
              patch.object( settings_ui_controller.settings_ui, 'script_folders_list' ) as list_w ):
            fd.askdirectory.return_value = invalid_path
            settings_ui_controller.add_script_folder()

            list.append.assert_not_called()
            list_w.insert.assert_not_called()
            assert len( settings_ui_controller.settings._script_folders ) == 1


    def test_remove_folder_removes_focused_row_and_matching_path( self, settings_ui_controller : SettingsUiController ) -> None:
        """ Delete the focused tree row and remove its Path from settings.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
        """

        tree = Mock()
        tree_focus_item = 'r-1'

        settings_ui_controller.settings_ui.script_folders_list = tree
        settings_ui_controller.settings.script_folders = [ Path( 'C:\\' ) ]

        tree.item.return_value = { 'text': 'C:\\' }
        tree.focus.return_value = tree_focus_item

        settings_ui_controller.remove_script_folder()

        tree.focus.assert_called_once_with()
        tree.item.assert_called_once_with( tree.focus.return_value )
        tree.delete.assert_called_once_with( tree_focus_item )
        assert settings_ui_controller.settings.script_folders == []


    def test_remove_folder_preserves_other_folders( self, settings_ui_controller: SettingsUiController ) -> None:
        """ Remove only the selected folder.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
        """

        tree = Mock()
        settings_ui_controller.settings._script_folders = [ Path( 'C:\\' ), Path( 'C:\\F1' ) ]
        settings_ui_controller.settings_ui.script_folders_list = tree
        tree_focus_item = 'r-1'

        with ( patch.object( tree, 'delete' ) as tree_del,
              patch.object( tree, 'item', return_value = { 'text': 'C:\\' } ) as tree_item,
              patch.object( tree, 'focus', return_value = tree_focus_item ) as tree_focus,
               patch.object( settings_ui_controller.settings, 'script_folders' ) as folder_list ):
            settings_ui_controller.remove_script_folder()

            tree_item.assert_called_once_with( tree_focus.return_value )
            tree_del.assert_called_once_with( tree_focus_item )
            folder_list.remove.assert_called_once_with( Path( tree_item.return_value[ 'text' ] ) )
            assert Path( 'C:\\F1' ) in settings_ui_controller.settings._script_folders


    def test_remove_folder_does_nothing_without_tree( self, settings_ui_controller: SettingsUiController ) -> None:
        """ Leave settings unchanged when script_folders_list is None.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
        """

        script_list = [ Path( 'C:\\' ), Path( 'C:\\F1' ) ]
        settings_ui_controller.settings.script_folders = script_list

        with patch.object( settings_ui_controller.settings_ui, 'script_folders_list' ) as list_w:
            settings_ui_controller.settings_ui.script_folders_list = None
            settings_ui_controller.remove_script_folder()

            list_w.focus.assert_not_called()
            list_w.item.assert_not_called()
            list_w.delete.assert_not_called()

        assert settings_ui_controller.settings.script_folders is script_list


class TestRebuildMenu:

    def test_rebuild_menu_clears_cache_and_gathers_scripts( self, settings_ui_controller: SettingsUiController ) -> None:
        """ Call gather_script_info once with clear_cache=True.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
        """

        with patch.object( settings_ui_controller._settings_op_callbacks, 'gather_script_info' ) as gather:
            settings_ui_controller.rebuild_menu()

            gather.assert_called_once_with( clear_cache = True )


    def test_rebuild_menu_uses_updated_script_list( self, settings_ui_controller: SettingsUiController ) -> None:
        """ Gather first, then retrieve scripts and pass them to clear_script_menu.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
        """

        script_list = []

        with ( patch.object( settings_ui_controller._settings_op_callbacks, 'get_script_list', return_value = script_list ) as get,
              patch.object( settings_ui_controller._settings_op_callbacks, 'clear_script_menu' ) as clear ):
            settings_ui_controller.rebuild_menu()

            get.assert_called_once_with()
            clear.assert_called_once_with( exec_list = get.return_value )


class TestLanguage:

    def test_selected_language_is_stored_and_applied( self, settings_ui_controller: SettingsUiController ) -> None:
        """ Read the Combobox value, store it, and invoke the language callback.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
        """

        event = Mock()
        event.widget = Mock( spec = Combobox )
        event.widget.get.return_value = 'sv'

        with patch.object( settings_ui_controller, 'change_app_language' ) as change:
            settings_ui_controller.set_current_language( event )

            change.assert_called_once_with( new_language = event.widget.get.return_value )
            assert settings_ui_controller.settings.current_language is event.widget.get.return_value


    @pytest.mark.parametrize( 'event_kind', [ 'none', 'other-widget' ] )
    def test_invalid_language_event_is_ignored( self, settings_ui_controller: SettingsUiController, event_kind: str ) -> None:
        """ Leave the language unchanged and do not invoke its callback.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
            event_kind (str): Event widget to test with
        """

        if event_kind == 'none':
            event = None

        else:
            event = Mock()
            event.widget = Mock( spec = Button ) if event_kind == 'other-widget' else Mock( spec = Combobox )

        with patch.object( settings_ui_controller.settings, 'change_app_language' ) as change:
            settings_ui_controller.settings.current_language = 'sv'
            settings_ui_controller.set_current_language( event )

            change.assert_not_called()
            assert settings_ui_controller.settings.current_language == 'sv'


class TestBooleanSettings:

    @pytest.mark.parametrize( ( 'method_name', 'setting_name' ),
                             [ ( 'set_include_ss_in_error_mail', 'include_ss_in_error_mail' ),
                                ('set_minimize_on_running', 'minimize_on_running' ), ], )
    @pytest.mark.parametrize( 'new_value', [ False, True ] )
    def test_boolean_setting_is_updated( self, settings_ui_controller: SettingsUiController, method_name: str, setting_name: str, new_value: bool ) -> None:
        """ Replace the existing setting with the supplied boolean.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
            method_name (str): Method to test
            setting_name (str): Settings to test
            new_value (bool): Value to set
        """

        setattr( settings_ui_controller.settings, setting_name, not new_value )

        getattr( settings_ui_controller, method_name )( new_value )

        assert getattr( settings_ui_controller.settings, setting_name ) is new_value


    @pytest.mark.parametrize( 'new_value', [ False, True ] )
    @pytest.mark.parametrize( 'has_checkbox', [ False, True ] )
    def test_force_focus_updates_setting_and_checkbox( self, settings_ui_controller: SettingsUiController, new_value: bool, has_checkbox: bool ) -> None:
        """ Store the value; configure an available checkbox as normal/disabled.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
            new_value (bool): Value to set
            has_checkbox (bool): Define if checkbox is available
        """

        chb = Mock()
        settings_ui_controller.settings.force_focus_post_execution = not new_value
        settings_ui_controller.settings_ui.chb_force_focus_post_execution = chb if has_checkbox else None

        settings_ui_controller.set_force_focus_post_execution( new_value = new_value )

        assert settings_ui_controller.settings.force_focus_post_execution is new_value

        if has_checkbox:

            if new_value:
                chb.config.assert_called_once_with( state = 'normal' )

            else:
                chb.config.assert_called_once_with( state = 'disabled' )

        else:
            chb.assert_not_called()


    @pytest.mark.parametrize( 'new_value', [ False, True ] )
    @pytest.mark.parametrize( 'has_checkbox', [ False, True ] )
    def test_send_mail_updates_setting_and_screenshot_checkbox( self, settings_ui_controller: SettingsUiController, new_value: bool, has_checkbox: bool ) -> None:
        """Store the value; enable/disable the available screenshot checkbox.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
            new_value (bool): Value to set
            has_checkbox (bool): Define if checkbox is available
        """

        chb = Mock()
        settings_ui_controller.settings.send_mail_on_error = not new_value
        settings_ui_controller.settings_ui.chb_include_ss_in_error_mail = chb if has_checkbox else None

        settings_ui_controller.set_send_mail_on_error( new_value = new_value )

        assert settings_ui_controller.settings.send_mail_on_error is new_value

        if has_checkbox:

            if new_value:
                chb.config.assert_called_once_with( state = 'normal' )

            else:
                chb.config.assert_called_once_with( state = 'disabled' )

        else:
            chb.assert_not_called()


    @pytest.mark.parametrize( 'new_value', [ False, True ] )
    def test_on_top_updates_setting_and_window( self, settings_ui_controller: SettingsUiController, module: str, new_value: bool ) -> None:
        """ Store the value, force window focus, and set its -topmost attribute.

        Args:
            settings_ui_controller (SettingsUiController): Fixture for an SettingsUiController instance
            module (str): Fixture of module import path
            new_value (bool): Value to set
        """

        settings_ui_controller.settings.on_top = not new_value

        with patch.object( settings_ui_controller, 'root_window' ) as rw:
            settings_ui_controller.set_on_top( new_value )

            rw.focus_force.assert_called_once_with()
            rw.attributes.assert_called_once_with( '-topmost', new_value )

        assert settings_ui_controller.settings.on_top is new_value
