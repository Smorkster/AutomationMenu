"""
Test cases for sriptinfo

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

import json
from pathlib import Path
from typing import Callable

import pytest

from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.scriptmetadata import ScriptMetadata
from automation_menu.models.user import User


class TestPath:
    def test_to_dict_serializes_fullpath_as_string( self, tmp_path: Path ) -> None:
        """ Test that to_dict, serializes the scripts full path
        to a string.

        Args:
            tmp_path (Path): Temporary folder path
        """

        script_path: Path = tmp_path / 'script.py'
        smd: ScriptMetadata = ScriptMetadata ( synopsis = 'Test synopsis',
                                              author = 'Test author' )
        script_info: ScriptInfo = ScriptInfo( filename = script_path.name,
                                             fullpath = script_path,
                                             scriptmeta = smd )

        script_dict: dict = script_info.to_dict()
        script_dict_path = script_dict[ 'fullpath' ]

        assert isinstance( script_dict_path, str )
        assert script_dict_path == str( script_path )


    def test_from_dict_restores_fullpath_as_path( self, tmp_path: Path ) -> None:
        """ Test that path in a dict is transformed to Path

        Args:
            tmp_path (Path): Temporary folder path
        """

        script_info_dict: dict = { 'filename': 'Test_script.py',
                                  'fullpath': tmp_path / 'Test_script.py',
                                  'scriptmeta': { 'synopsis': 'Test script',
                                                 'author': 'Test author' } }

        script_info: ScriptInfo = ScriptInfo.from_dict( value = script_info_dict )

        assert isinstance( script_info.fullpath, Path )


class TestCreation:
    def test_cache_round_trip_preserves_values( self, tmp_path: Path ) -> None:
        """ Test creation/decrypting/recreation

        Args:
            tmp_path (Path): Temporary folder path
        """

        # Arrange
        filename: str = 'Test_script.py'
        fullpath: Path = tmp_path / 'Test_script.py'
        synopsis: str = 'Test script'
        author: str = 'Test author'

        script_info_dict: dict = { 'filename': filename,
                                  'fullpath': str( fullpath ),
                                  'using_breakpoint': True,
                                  'scriptmeta': { 'synopsis': synopsis,
                                                 'author': author } }

        # Act
        script_info: ScriptInfo = ScriptInfo.from_dict( value = script_info_dict )
        script_dict: dict = script_info.to_dict()
        stringed_dict: str = json.dumps( script_dict )
        dict_from_stringed_dict: dict = json.loads( stringed_dict )
        new_si_from_dict: ScriptInfo = ScriptInfo.from_dict( value = dict_from_stringed_dict )
        dict_again: dict = new_si_from_dict.to_dict()

        # Assert
        assert dict_again[ 'filename' ] == filename
        assert dict_again[ 'fullpath' ] == str( fullpath )
        assert dict_again[ 'using_breakpoint' ] == True
        assert dict_again[ 'scriptmeta' ][ 'synopsis' ] == synopsis
        assert dict_again[ 'scriptmeta' ][ 'author' ] == author

        assert isinstance( new_si_from_dict.fullpath, Path )
        assert new_si_from_dict.fullpath == fullpath


    def test_repr_returns_path( self, tmp_path: Path ) -> None:
        """ Is fullpath returned from __repr__

        Args:
            tmp_path (Path): Temporary folder path
        """

        filename: str = 'Test_script.py'
        fullpath: Path = tmp_path / 'Test_script.py'
        synopsis: str = 'Test script'
        author: str = 'Test author'

        script_info_dict: ScriptInfo = ScriptInfo.from_dict( { 'filename': filename,
                                                              'fullpath': str( fullpath ),
                                                              'using_breakpoint': True,
                                                              'scriptmeta': { 'synopsis': synopsis,
                                                                             'author': author } } )

        assert script_info_dict.__repr__() == str( fullpath )


class TestAttributes:

    def test_is_attribute_added( self, tmp_path: Path ) -> None:
        """ Is a new attribute added, and is value preserved.

        Args:
            tmp_path (Path): Temporary folder path
        """

        filename: str = 'Test_script.py'
        fullpath: Path = tmp_path / 'Test_script.py'
        synopsis: str = 'Test script'
        author: str = 'Test author'

        si: ScriptInfo = ScriptInfo.from_dict( { 'filename': filename,
                                                'fullpath': str( fullpath ),
                                                'using_breakpoint': True,
                                                'scriptmeta': { 'synopsis': synopsis,
                                                               'author': author } } )

        si.add_attr( attr_name = 'Testattr', attr_val = 'Test' )

        assert hasattr( si, 'Testattr' )
        assert si.Testattr == 'Test' # type: ignore


    def test_retrieval_of_attr( self, tmp_path: Path ) -> None:
        """ Is attribute and correct value retrieved.

        Args:
            tmp_path (Path): Temporary folder path
        """

        filename: str = 'Test_script.py'
        fullpath: Path = tmp_path / 'Test_script.py'
        synopsis: str = 'Test script'
        author: str = 'Test author'

        si: ScriptInfo = ScriptInfo.from_dict( { 'filename': filename,
                                                'fullpath': str( fullpath ),
                                                'using_breakpoint': True,
                                                'scriptmeta': { 'synopsis': synopsis,
                                                               'author': author } } )

        retrieved_path: Path = si.get_attr( attr_name = 'fullpath' )

        assert retrieved_path == fullpath


    def test_retrieval_of_metadata_attr( self, tmp_path: Path ) -> None:
        """ Is metadata attribute and correct value retrieved.

        Args:
            tmp_path (Path): Temporary folder path
        """

        filename: str = 'Test_script.py'
        fullpath: Path = tmp_path / 'Test_script.py'
        synopsis: str = 'Test script'
        author: str = 'Test author'

        si: ScriptInfo = ScriptInfo.from_dict( { 'filename': filename,
                                                'fullpath': str( fullpath ),
                                                'using_breakpoint': True,
                                                'scriptmeta': { 'synopsis': synopsis,
                                                               'author': author } } )

        retrieved_author: str = si.get_attr( attr_name = 'author' )

        assert retrieved_author == author


    def test_retrieval_of_added_attr( self, tmp_path: Path ) -> None:
        """ Is metadata attribute and correct value retrieved.

        Args:
            tmp_path (Path): Temporary folder path
        """

        filename: str = 'Test_script.py'
        fullpath: Path = tmp_path / 'Test_script.py'
        synopsis: str = 'Test script'
        author: str = 'Test author'

        si: ScriptInfo = ScriptInfo.from_dict( { 'filename': filename,
                                                'fullpath': str( fullpath ),
                                                'using_breakpoint': True,
                                                'scriptmeta': { 'synopsis': synopsis,
                                                               'author': author } } )

        si.add_attr( attr_name = 'Test', attr_val = 'Testing' )

        retrieved_value: str | None = si.get_attr( 'Test' )

        assert retrieved_value is not None
        assert retrieved_value == 'Testing'


    def test_retrieval_of_not_available_attribute_is_None( self, tmp_path: Path ) -> None:
        """ Is metadata attribute and correct value retrieved.

        Args:
            tmp_path (Path): Temporary folder path
        """

        filename: str = 'Test_script.py'
        fullpath: Path = tmp_path / 'Test_script.py'
        synopsis: str = 'Test script'
        author: str = 'Test author'

        si: ScriptInfo = ScriptInfo.from_dict( { 'filename': filename,
                                                'fullpath': str( fullpath ),
                                                'using_breakpoint': True,
                                                'scriptmeta': { 'synopsis': synopsis,
                                                               'author': author } } )

        retrieved_value: str | None = si.get_attr( 'Test' )

        assert retrieved_value is None


    @pytest.mark.parametrize( ( 'attr_name', 'attr_val', 'append', 'expected' ),
                             [ pytest.param( 'test', 'Test author', False, 'Test author', id = 'add_new_attr' ),
                               pytest.param( 'author', 'Test author', False, 'Test author', id = 'replace_attr_val' ),
                               pytest.param( 'filename', 'Testauthor', True, '', id = 'append_attr_val' ),
                               pytest.param( 'filename', 'another_file_name.py', False, 'another_file_name.py', id = 'append_attr_val' ), ] )
    def test_set_attr( self, tmp_path: Path, attr_name: str, attr_val: str, append: bool, expected: str ) -> None:
        """ Is attributes set or add/set

        Args:
            tmp_path (Path): Temporary folder path
            attr_name (str): Name of attribute to set
            attr_val (str): Value of attribute to set
            append (bool): True if value should be appended
            expected (str): What the attribute value is expected to be
        """

        filename: str = 'Test_script.py'
        fullpath: Path = tmp_path / 'Test_script.py'
        synopsis: str = 'Test script'
        author: str = 'Test author'

        si: ScriptInfo = ScriptInfo.from_dict( { 'filename': filename,
                                                'fullpath': str( fullpath ),
                                                'using_breakpoint': True,
                                                'scriptmeta': { 'synopsis': synopsis,
                                                               'author': author } } )

        if append:
            expected = si.get_attr( attr_name = attr_name ) + attr_val

        si.set_attr( attr_name = attr_name, attr_val = attr_val, append = append )

        assert si.get_attr( attr_name ) == expected


    @pytest.mark.parametrize( ( 'author', 'ad_name', 'expected' ),
                             [ pytest.param( 'Test author', 'Test author', True, id = 'matching' ),
                               pytest.param( 'Test author', 'Some other user', False, id = 'user_other_than_author' ) ] )
    def test_is_author( self, tmp_path: Path, mock_user: Callable[ [ str ], User ], author: str, ad_name: str, expected: bool ) -> None:
        """ Is metadata attribute and correct value retrieved.

        Args:
            tmp_path (Path): Temporary folder path
            mock_user (Callable[[str], User]): Mock factory of User object
            author (str): 'Mocked' script author
            ad_name (str): 'Mocked' user name
            expected (bool): Function result expected for parameters
        """

        filename: str = 'Test_script.py'
        fullpath: Path = tmp_path / 'Test_script.py'
        synopsis: str = 'Test script'

        si: ScriptInfo = ScriptInfo.from_dict( { 'filename': filename,
                                                'fullpath': str( fullpath ),
                                                'using_breakpoint': True,
                                                'scriptmeta': { 'synopsis': synopsis,
                                                               'author': author } } )

        mocked_user = mock_user( ad_name )
        is_author_result: bool = si.is_author( user = mocked_user )

        assert is_author_result == expected
