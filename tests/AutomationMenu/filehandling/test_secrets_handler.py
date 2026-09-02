

import json
import pytest

from pathlib import Path

from automation_menu.filehandling.secrets_handler import read_secrets_file


SECRETS_CONTENT = '''{
    "domain_name": "domain",
    "error_ss_prefix": "AutoError",
    "ldap_search_base": "dc=your,dc=domain,dc=com",
    "ldap_server": "ldap://your-ldap-server.com",
    "main_error_mail": "admin@your-domain.com",
    "mainwindowtitle": "Your Title Name Here",
    "settings_file_name": "AutomationMenu_Settings_File_Name.json",
    "smtprelay": "your-smtp-server.com"
}'''

MALFORMED_JSON = r'''{
    'a': 'b',
    'c' = '1',
    'f': 1
}'''

def _create_temp_secrets_file( dir_path: Path, content: str ) -> Path:
    """ Create a temporary secrets JSON file.

    Args:
        dir_path (Path): Folder to create file in.
        content (str): What to write to the file.
    """

    ( dir_path / 's' ).mkdir()
    file_path = dir_path / 'secrets.json'
    file_path.write_text( content )

    return file_path


def _create_temp_secrets_file_with_utf_8_BOM( dir_path: Path, content: str ) -> Path:
    """ Create a temporary UTF-8 BOM-prefixed secrets JSON file.

    Args:
        dir_path (Path): Folder to create file in.
        content (str): What to write to the file.
    """

    ( dir_path / 's' ).mkdir()
    file_path = dir_path / 'secrets.json'
    full_content = b'\xef\xbb\xbf' + content.encode( 'utf-8' )
    file_path.write_bytes( full_content )

    return file_path


def test_read_secrets_file_can_read( tmp_path: Path ) -> None:
    """ Reads valid secrets JSON into a dictionary.

    Args:
        tmp_path (Path): Fixture for temp folder
    """

    file_path = _create_temp_secrets_file( tmp_path, SECRETS_CONTENT )
    secrets = read_secrets_file( str( file_path ) )

    assert isinstance( secrets , dict )


def test_read_secrets_file_valid_content( tmp_path: Path ) -> None:
    """ Preserves the expected values from a valid secrets JSON file.

    Args:
        tmp_path (Path): Fixture for temp folder
    """

    file_path = _create_temp_secrets_file( tmp_path, SECRETS_CONTENT )
    secrets = read_secrets_file( str( file_path ) )

    assert isinstance( secrets , dict )
    assert 'domain_name' in secrets.keys()
    assert secrets[ 'domain_name' ] == 'domain'

    assert 'error_ss_prefix' in secrets.keys()
    assert secrets[ 'error_ss_prefix' ] == 'AutoError'

    assert 'ldap_search_base' in secrets.keys()
    assert secrets[ 'ldap_search_base' ] == 'dc=your,dc=domain,dc=com'

    assert 'ldap_server' in secrets.keys()
    assert secrets[ 'ldap_server' ] == 'ldap://your-ldap-server.com'

    assert 'main_error_mail' in secrets.keys()
    assert secrets[ 'main_error_mail' ] == 'admin@your-domain.com'

    assert 'mainwindowtitle' in secrets.keys()
    assert secrets[ 'mainwindowtitle' ] == 'Your Title Name Here'

    assert 'settings_file_name' in secrets.keys()
    assert secrets[ 'settings_file_name' ] == 'AutomationMenu_Settings_File_Name.json'

    assert 'smtprelay' in secrets.keys()
    assert secrets[ 'smtprelay' ] == 'your-smtp-server.com'


def test_read_secrets_file_invalid_path() -> None:
    """ Raises FileNotFoundError when the secrets file does not exist. """

    with pytest.raises( FileNotFoundError ):
        read_secrets_file( '' )


def test_read_secrets_file_malformed_json( tmp_path: Path ) -> None:
    """ Raises JSONDecodeError for malformed JSON.

    Args:
        tmp_path (Path): Fixture for temp folder
    """

    file_path = _create_temp_secrets_file( tmp_path, MALFORMED_JSON )

    with pytest.raises( json.JSONDecodeError ):
        read_secrets_file( str( file_path ) )


def test_read_secrets_file_with_BOM( tmp_path: Path ) -> None:
    """ Reads a UTF-8 BOM-prefixed secrets JSON file.

    Args:
        tmp_path (Path): Fixture for temp folder
    """

    file_path = _create_temp_secrets_file_with_utf_8_BOM( tmp_path, SECRETS_CONTENT )

    read_content = read_secrets_file( str( file_path ) )

    assert isinstance( read_content, dict )
