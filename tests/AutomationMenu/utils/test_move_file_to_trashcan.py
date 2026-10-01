"""
Test cases for settings tab

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


import ctypes
from typing import Any
import pytest

from ctypes import POINTER, addressof, c_void_p, cast, wstring_at
from pathlib import Path
from unittest.mock import patch

from automation_menu.utils.move_file_to_trashcan import SHFILEOPSTRUCTW, recycle


@pytest.fixture
def module() -> str:
    """ Module import path

    Returns:
        (str): Returns module import path
    """

    return 'automation_menu.utils.move_file_to_trashcan'

@pytest.fixture
def shell_module() -> str:
    """ Shell module import path

    Returns:
        (str): Returns shell module import path
    """

    return 'automation_menu.utils.move_file_to_trashcan.shell32.SHFileOperationW'


class TestRecycle:

    def test_passes_absolute_normalized_path_to_shell( self, shell_module: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch ) -> None:
        """ Convert the supplied path to an absolute normalized path.

        Args:
            shell_module (str): Fixture for shell module import path
            tmp_path (Path): Temporary directory
            monkeypatch (pytest.MonkeyPatch): Monkey patch mechanism
        """

        monkeypatch.chdir( tmp_path )
        expected_path: str = str( tmp_path / 'test.txt' )

        def inspect_operation( pointer: Any ) -> int:
            """ Verify the source path passed to the mocked Windows shell operation.

            Args:
                pointer (Any): ctypes byref argument pointing to an SHFILEOPSTRUCTW.

            Returns:
                int: Zero, simulating a successful shell operation.

            Raises:
                AssertionError: If the source path differs from expected_path.
            """

            operation = cast( pointer, POINTER( SHFILEOPSTRUCTW ) ).contents
            assert operation.pFrom == expected_path

            return 0

        with patch( shell_module, side_effect = inspect_operation ) as shell:
            recycle( 'subfolder/../test.txt' )

        shell.assert_called_once()


    def test_source_path_is_double_null_terminated( self, shell_module: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch ) -> None:
        """ Provide the double-null-terminated source path required by Windows.

        Args:
            shell_module (str): Fixture for shell module import path
            tmp_path (Path): Temporary directory
            monkeypatch (pytest.MonkeyPatch): Monkey patch mechanism
        """

        monkeypatch.chdir( tmp_path )
        expected_path: str = str( tmp_path / 'test.txt' )

        def inspect_operation( pointer: Any ) -> int:
            """ Inspect the source buffer and simulate a successful operation.

            Args:
                pointer (Any): ctypes byref argument pointing to an SHFILEOPSTRUCTW.

            Returns:
                int: Zero, simulating a successful shell operation.

            Raises:
                AssertionError: If the source path differs from expected_path.
            """

            operation = cast( pointer, POINTER( SHFILEOPSTRUCTW ) ).contents

            field_address = addressof( operation ) + SHFILEOPSTRUCTW.pFrom.offset
            source_address = c_void_p.from_address( field_address ).value
            assert source_address is not None

            source = wstring_at( source_address, len( expected_path ) + 2 )

            assert source == expected_path + '\0\0'

            return 0

        with patch( shell_module, side_effect = inspect_operation ) as shell:
            recycle( 'test.txt' )

        shell.assert_called_once()


    def test_requests_delete_with_recycle_bin_and_no_ui_flags( self, shell_module: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch ) -> None:
        """ Set FO_DELETE and the flags enabling recycling without UI prompts.

        Args:
            shell_module (str): Fixture for shell module import path
            tmp_path (Path): Temporary directory
            monkeypatch (pytest.MonkeyPatch): Monkey patch mechanism
        """

        monkeypatch.chdir( tmp_path )
        expected_path: str = str( tmp_path / 'test.txt' )

        def inspect_operation( pointer: Any ) -> int:
            """ Verify the source path passed to the mocked Windows shell operation.

            Args:
                pointer (Any): ctypes byref argument pointing to an SHFILEOPSTRUCTW.

            Returns:
                int: Zero, simulating a successful shell operation.

            Raises:
                AssertionError: If the source path differs from expected_path.
            """

            operation = cast( pointer, POINTER( SHFILEOPSTRUCTW ) ).contents
            assert operation.wFunc == 3
            assert operation.fFlags == 1620

            return 0

        with patch( shell_module, side_effect = inspect_operation ) as shell:
            recycle( 'subfolder/../test.txt' )

        shell.assert_called_once()


    def test_calls_shell_operation_once_with_operation_structure( self, shell_module: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch ) -> None:
        """ Pass a pointer to the configured SHFILEOPSTRUCTW to the shell.

        Args:
            shell_module (str): Fixture for shell module import path
            tmp_path (Path): Temporary directory
            monkeypatch (pytest.MonkeyPatch): Monkey patch mechanism
        """

        with patch( shell_module, return_value = 0 ) as shell:
            recycle( str( tmp_path / 'test.txt' ) )

        shell.assert_called_once()

        args = shell.call_args.args
        kwargs = shell.call_args.kwargs

        assert len( args ) == 1
        assert kwargs == {}

        pointer = args[ 0 ]

        assert isinstance( pointer._obj, SHFILEOPSTRUCTW )


    @pytest.mark.parametrize( ( 'result_code', 'expected_result' ),
                             [ pytest.param( 0, True, id = 'success' ),
                              pytest.param( 1, False, id = 'failure' ),
                              pytest.param( 5, False, id = 'another-failure' ), ], )
    def test_returns_whether_shell_operation_succeeded( self, shell_module: str, tmp_path: Path, result_code: int, expected_result: bool ) -> None:
        """ Return True only when SHFileOperationW returns zero.

        Args:
            shell_module (str): Fixture for shell module import path
            tmp_path (Path): Temporary directory
            result_code (int): Simulated operation result
            expected_result (bool): Result expected based on result_code
        """

        with patch( shell_module, return_value = result_code ) as shell:
            result = recycle( str( tmp_path ) )

        assert result is expected_result
