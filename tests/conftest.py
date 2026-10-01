"""
Shared pytest fixtures for application dependencies and temporary test data.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from pathlib import Path
from queue import Queue
from typing import Callable, cast
from unittest.mock import Mock, patch

import pytest

from automation_menu.core.app_context import ApplicationContext
from automation_menu.models.application_state import ApplicationState
from automation_menu.models.enums import ApplicationRunState
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.scriptmetadata import ScriptMetadata
from automation_menu.models.user import User
from automation_menu.services.script_manager import ScriptManager
from automation_menu.services.settings_manager import SettingsManager


@pytest.fixture
def script_manager( tmp_path: Path, mock_user: Callable[ [ str ], User], ) -> ScriptManager:
    """ Create a script manager using a temporary directory and mocked user.

    Args:
        tmp_path (Path): Temporary directory supplied by pytest.
        mock_user (Callable[[str], User]): Factory for mocked users.

    Returns:
        ScriptManager: Manager configured to search the temporary directory.
    """

    return ScriptManager( script_dir_path = [ tmp_path ],
                         current_user = mock_user( 'test-user'), )


@pytest.fixture
def settings_manager( app_context: Mock, tmp_path: Path ) -> SettingsManager:
    """ Create a settings manager without loading saved settings.

    Args:
        app_context (Mock): Mocked application dependencies.
        tmp_path (Path): Temporary directory supplied by pytest.

    Returns:
        SettingsManager: Manager using a settings path in the temporary directory.
    """

    p: Path = tmp_path / 'settings.json'

    with patch.object( SettingsManager, 'read_saved_settings' ):
        m: SettingsManager = SettingsManager( app_context = cast( ApplicationContext, app_context ),
                                             settings_file_path = str( p ) )

    m._settings_file_path = p

    return m


@pytest.fixture
def output_queue() -> Queue[ object ]:
    """ Create an empty queue for test output.

    Returns:
        Queue[object]: A new queue for each test requesting the fixture.
    """

    return Queue()


@pytest.fixture
def app_context() -> Mock:
    """ Create a mock application context with common dependencies.

    Returns:
        Mock: Context exposing mocked logger, language manager, main window,
            output queue, and script manager dependencies.
    """

    context = Mock()

    context.debug_logger = Mock()
    context.LanguageManager = Mock()
    context.main_window = Mock()
    context.OutputQueue = Mock()
    context.ScriptManager = Mock()

    return context


@pytest.fixture
def app_state() -> ApplicationState:
    """ Create a mock using the ApplicationState specification.

    Returns:
        ApplicationState: Mock cast to ApplicationState for use in tests.
    """

    return cast( ApplicationState, Mock( spec = ApplicationState ) )


@pytest.fixture
def app_run_state() -> ApplicationRunState:
    """ Provide the application run state used by tests.

    Returns:
        ApplicationRunState: The TEST enumeration member.
    """

    return ApplicationRunState.TEST


@pytest.fixture
def script_info( tmp_path: Path ) -> ScriptInfo:
    """ Create script information referencing a temporary path.

    Args:
        tmp_path (Path): Temporary directory supplied by pytest.

    Returns:
        ScriptInfo: Information for script.py with sample metadata.
            The script file itself is not created.
    """

    return ScriptInfo( filename = 'script.py',
                      fullpath = tmp_path / 'script.py',
                      scriptmeta = ScriptMetadata( synopsis = 'Syn',
                                                  author = 'Auth' ) )


@pytest.fixture
def menu_cache_path( tmp_path: Path ) -> Path:
    """ Provide a menu-cache path inside a temporary directory.

    Args:
        tmp_path (Path): Temporary directory supplied by pytest.

    Returns:
        Path: Path to menu_cache.json. The cache file itself is not created.
    """

    return tmp_path / 'menu_cache.json'


@pytest.fixture
def mock_user() -> Callable[ [ str ], User ]:
    """ Provide a factory for mocked users with configurable AD names.

    Returns:
        Callable[[str], User]: Factory accepting an AD name and returning
            a user mock.
    """

    def create_user( ad_name: str ) -> User:
        """ Create a user mock with the requested Active Directory name.

        Args:
            ad_name (str): Value exposed through AdObject.name.value.

        Returns:
            User: Mock using the User specification and cast to User.
        """
        u = Mock( spec = User )

        u.AdObject = Mock()
        u.AdObject.name = Mock()
        u.AdObject.name.value = ad_name

        return cast( User, u )

    return create_user
