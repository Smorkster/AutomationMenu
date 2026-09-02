

from pathlib import Path

from ldap3 import Connection

from automation_menu.core.auth import connect_to_AD
from automation_menu.filehandling.secrets_handler import read_secrets_file
from automation_menu.models.secrets import Secrets


def test_connect_to_AD() -> None:
    """ Returns an LDAP connection for the configured server. """

    secrets_file: Path = Path( __file__ ).parent.parent.parent.parent / 'secrets.json'

    secrets_dict: dict = read_secrets_file( file_path = str( secrets_file ) )
    secrets: Secrets = Secrets( new_dict = secrets_dict )

    connection = connect_to_AD( ldap_server = secrets[ 'ldap_server' ], domain_name = '' )

    assert isinstance( connection, Connection )
