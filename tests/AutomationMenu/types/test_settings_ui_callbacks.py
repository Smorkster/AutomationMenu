"""
Test cases for settings ui callbacks

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from unittest.mock import Mock

from automation_menu.types.settings_ui_callbacks import SettingsUiCallbacks


class TestCreate:

    def test_creation_stores_callback_references( self ) -> None:
        """ Each field holds the exact callback supplied to the constructor. """

        clear = Mock()
        gather = Mock()
        get = Mock()

        ui = SettingsUiCallbacks( clear_script_menu = clear,
                                 gather_script_info = gather,
                                 get_script_list = get )

        assert ui.clear_script_menu is clear
        assert ui.gather_script_info is gather
        assert ui.get_script_list is get


    def test_creation_does_not_invoke_callbacks( self ) -> None:
        """ Constructing the container does not execute any callback. """

        clear = Mock()
        gather = Mock()
        get = Mock()

        SettingsUiCallbacks( clear_script_menu = clear,
                            gather_script_info = gather,
                            get_script_list = get )

        clear.assert_not_called()
        gather.assert_not_called()
        get.assert_not_called()
