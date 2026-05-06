"""
Authenticate against Active Directory and provide LDAP helper functions.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations
from typing import Callable

import os

from dynamicinputbox import ResultDict, ResultTuple, dynamic_inputbox as inputbox
from ldap3 import ALL, Connection, Entry, Server
from ldap3.core.exceptions import LDAPSocketOpenError


def connect_to_AD( ldap_server: str, domain_name: str ) -> Connection:
    """ Connect to Active Directory and return an authenticated connection.

    Args:
        ldap_server (str): Hostname of the LDAP server.
        domain_name (str): Domain name used when building the login username.

    Returns:
        Connection: An authenticated LDAP connection.

    Raises:
        ConnectionError: If a connection could not be established after the allowed attempts.
        SystemExit: If the input dialog exits the application.
    """

    from automation_menu.utils.localization import _

    AD_loginattempts: int = 0
    con: Connection
    main_input_text: str = _( 'Enter password for AD-domain\nP.S.\nThe password will not be stored' )

    while ( AD_loginattempts < 3 ):
        try:
            if AD_loginattempts == 0:
                inputbox_label_text: str = main_input_text

            else:
                inputbox_label_text: str = _( 'Wrong password. Try again\n{main_label_text}' ).format( main_label_text = main_input_text )

            abort_string: str = _( 'Abort' )
            ok_string: str = _( 'Ok' )
            ipb = inputbox( message = inputbox_label_text, title = _( 'AD password' ), input = True, input_show = '*', buttons = [ ok_string, abort_string ] ).show()
            password: ResultDict | ResultTuple = ipb.get( dictionary = True )

            if isinstance( password, dict ):
                if password.get( 'button' ) == abort_string or password.get( 'button' ) == 'Cancel':
                    inputbox( message = _( 'No password was entered. Exiting.' ) ).show()

                    break

                inputs: dict = password.get( 'inputs', {} )
                pwd = ''

                if inputs is not None:
                    pwd = inputs.get( 'Input', b'' ).decode()

                if pwd == '':

                    break

                server: Server = Server( host = ldap_server, get_info = ALL )
                con = Connection( server,
                                user = f'{ domain_name }\\{ os.getenv( key = 'USERNAME', default = 'DefaultUser' ) }',
                                password = pwd,
                                auto_bind = True
                                )

                return con

        except SystemExit:
            raise

        except LDAPSocketOpenError as e:
            inputbox( title = _( 'Error' ), message = _( 'Could not connect to AD\n{error}\nExiting' ).format( error = str( e ) ) ).show()
            break

        except Exception:
            AD_loginattempts = AD_loginattempts + 1

    raise ConnectionError( _( 'Could not connect to AD after {n} attempts' ).format( n = AD_loginattempts ) )


def get_user_adobject( ldap_search_base: str, ldap_connection: Connection, id: str | None = None, connected: Callable | None = None ) -> Entry:
    """ Get the Active Directory entry for a user.

    Args:
        ldap_search_base (str): LDAP search base used for the user lookup.
        ldap_connection (Connection): Active LDAP connection used for the search.
        id (str | None): Account name to look up. If omitted, the current username is used.
        connected (Callable | None): Optional callback that returns whether LDAP is connected.

    Returns:
        Entry: The first matching LDAP entry for the user.

    Raises:
        ConnectionError: If a connection check callback is provided and reports no LDAP connection.
    """

    from automation_menu.utils.localization import _

    if id == None:
        user: str = os.getenv( key = 'USERNAME', default = 'DefaultUser' )

    else:
        user: str = id

    if connected and not connected():
        raise ConnectionError( _( 'Not connected to LDAP' ) )

    ldap_connection.search(
        search_base = ldap_search_base,
        search_filter = f'(sAMAccountName={ user })',
        attributes = [ '*' ]
    )

    return ldap_connection.entries[ 0 ]
