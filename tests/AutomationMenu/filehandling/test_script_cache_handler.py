"""
Test cases for cache file handler

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


import json
import os
import pytest

from pathlib import Path

from automation_menu.filehandling.script_cache_handler import get_menu_cache_path, read_menu_cache, write_menu_cache_file


class Test_GetMenuCache:
    """Tests for resolving the menu cache file path."""

    def test_get_menu_cache_path__returns_expected_location( self ) -> None:
        """ Verify that the cache path points to the current user's local app data directory. """

        returned_path = get_menu_cache_path()
        expected_path = f'C:\\Users\\{ os.getlogin() }\\AppData\\Local\\AutomationMenu\\menu_cache.json'

        assert isinstance( returned_path, Path )
        assert str( returned_path ) == expected_path


class Test_ReadMenuCache:
    """ Tests for reading and decoding menu cache files. """

    def test_read_menu_cache__returns_decoded_content( self, tmp_path: Path ) -> None:
        """ Verify that valid JSON cache content is decoded and returned.

        Args:
            tmp_path (Path): Temporary folder path
        """

        temp_cache_content = '{ "test_script": { "filename": "test_script.py" } }'
        cache_path = tmp_path / 'menu_cache.json'
        cache_path.write_text( temp_cache_content )

        read_cache = read_menu_cache( cache_file = cache_path )

        assert read_cache == json.loads( temp_cache_content )


    def test_read_menu_cache__raises_for_invalid_json( self, tmp_path: Path ) -> None:
        """ Verify that invalid cache content raises JSONDecodeError.

        Args:
            tmp_path (Path): Temporary folder path
        """


        temp_cache_invalid_content = '{ "Test script" = ( "File name" = "Test file.py" ) }'
        cache_path = tmp_path / 'menu_cache.json'
        cache_path.write_text( temp_cache_invalid_content )

        with pytest.raises( json.JSONDecodeError ):
            c = read_menu_cache( cache_file = cache_path )


    def test_read_menu_cache__raises_on_file_not_found( self, tmp_path: Path ) -> None:
        """ Verify that a missing cache file raises FileNotFoundError.

        Args:
            tmp_path (Path): Temporary folder path
        """


        cache_path = tmp_path / 'menu_cache.json'

        with pytest.raises( FileNotFoundError ):
            read_menu_cache( cache_file = cache_path )


class Test_WriteMenuCache:
    """ Tests for writing menu cache files. """

    def test_write_menu_cache_file__creates_parent_directory( self, tmp_path: Path ) -> None:
        """ Verify that missing parent directories are created before writing.

        Args:
            tmp_path (Path): Temporary folder path
        """


        temp_cache_content = '{ "test_script": { "filename": "test_script.py" } }'
        cache_path = tmp_path / 'AppData' / 'menu_cache.json'

        write_menu_cache_file( cache_file_path = cache_path, cache_content = temp_cache_content )

        assert cache_path.parent.exists()


    def test_write_menu_cache_file__persists_content( self, tmp_path: Path ) -> None:
        """ Verify that cache content is written without modification.

        Args:
            tmp_path (Path): Temporary folder path
        """


        temp_cache_content = '{ "test_script": { "filename": "test_script.py" } }'
        cache_path = tmp_path / 'menu_cache.json'

        write_menu_cache_file( cache_file_path = cache_path, cache_content = temp_cache_content )

        with open( cache_path, mode = 'r' ) as f:
            file_content = f.read()

        assert file_content == temp_cache_content


    def test_write_menu_cache_file__raises_on_file_not_found( self, tmp_path: Path ) -> None:
        """ Verify that writing to a directory path raises PermissionError.

        Args:
            tmp_path (Path): Temporary folder path
        """


        temp_cache_content: str = '{ "test_script": { "filename": "test_script.py" } }'
        temp_cache_path: Path = tmp_path

        with pytest.raises( PermissionError ):
            write_menu_cache_file( cache_file_path = temp_cache_path, cache_content = temp_cache_content )
