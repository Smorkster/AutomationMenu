

import pytest

from automation_menu.core.auth import connect_to_AD


def test_connect_to_AD() -> None:
    """ Raises ConnectionError when the LDAP server cannot be reached. """

    with pytest.raises( ConnectionError ):
        connect_to_AD( ldap_server = 'test_server', domain_name = 'test_domain' )
