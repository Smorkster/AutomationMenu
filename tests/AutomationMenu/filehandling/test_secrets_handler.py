"""
Test cases for secrets handler

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from json import JSONDecodeError
from pathlib import Path

import pytest

from automation_menu.filehandling.secrets_handler import read_secrets_file


def test_read_file( tmp_path: Path ) -> None:
    """ Test read file

    Args:
        tmp_path (Path): Temporary folder path
    """

    file: Path = tmp_path / 'test_secrets.json'
    file.write_text( '{ "test": "" }' )

    ret = read_secrets_file( str( file ) )

    assert ret is not None


def test_read_empty_file( tmp_path: Path ) -> None:
    """ Assert that empty files are read

    Args:
        tmp_path (Path): Temporary folder path
    """

    tmp_path = tmp_path / 'tmp.json'
    ret = ''
    tmp_path.touch()

    with pytest.raises( JSONDecodeError ):
        read_secrets_file( str( tmp_path ) )
