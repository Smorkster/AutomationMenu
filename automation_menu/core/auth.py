"""
Authentication towards AD
And collecting AD functions

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.models.application_state import ApplicationState

import os
import sys

from dynamicinputbox import dynamic_inputbox as inputbox
from ldap3 import ALL, Connection, Entry, Server
from ldap3.core.exceptions import LDAPSocketOpenError

def connect_to_AD( app_state: ApplicationState, app_context: ApplicationContext ) -> Connection:
    """ Connect to Active Directory and return the connection object
    
    Returns:
        conn (ldap3.core.connection.Connection) - The connection setup after connecting
    """

    from automation_menu.utils.localization import _

    AD_loginattempts: int = 0
    main_input_text: str = _( 'Enter password for AD-domain\nP.S.\nThe password will not be stored' )

    while ( AD_loginattempts < 3 ):
        try:
            if AD_loginattempts == 0:
                inputbox_label_text: str = main_input_text

            else:
                inputbox_label_text: str = _( 'Wrong password. Try again\n{main_label_text}' ).format( main_label_text = main_input_text )

            abort_string: str = _( 'Abort' )
            ok_string: str = _( 'Ok' )
            password: dict = inputbox( message = inputbox_label_text, title = _( 'AD password' ), input = True, input_show = '*', buttons = [ ok_string, abort_string ] ).get( dictionary = True )

            if password.get( 'button' ) == abort_string or password.get( 'button' ) == 'Cancel':
                inputbox( message = _( 'No password was entered. Exiting.' ) )
                AD_loginattempts = 3
                sys.exit()

            server: Server = Server( host = app_state.secrets.get( 'ldap_server' ), get_info = ALL )
            con: Connection = Connection( server,
                               user = f'{ app_state.secrets.get( 'domain_name' ) }\\{ os.getenv( key = 'USERNAME', default = 'DefaultUser' ) }',
                               password = password.get('inputs')['Input'].get().decode(),
                               auto_bind = True
                             )

            if con:

                return con

        except SystemExit:
            raise SystemExit()

        except LDAPSocketOpenError as e:
            inputbox( title = _( 'Error' ), message = _( 'Could not connect to AD\n{error}\nExiting' ).format( error = str( e ) ) )
            AD_loginattempts = 3
            sys.exit()

        except Exception as e:
            AD_loginattempts = AD_loginattempts + 1


def get_user_adobject( id: str = None, app_state: ApplicationState = None, app_context: ApplicationContext = None ) -> Entry:
    """ Get the full AD-object of the current user

    Args:
        id (str): AD object for current user
        app_state (ApplicationState): Applicate state vault
        app_context (ApplicationContext): Collection of context managers
    """

    from automation_menu.utils.localization import _

    if id == None:
        user: str = os.getenv( key = 'USERNAME', default = 'DefaultUser' )

    else:
        user: str = id

    if not app_context.is_ldap_connected():
        raise ConnectionError( _( 'Not connected to LDAP' ) )

    app_context.ldap_connection.search(
        search_base = app_state.secrets.get( 'ldap_search_base' ),
        search_filter = f'(sAMAccountName={ user })',
        attributes = [ '*' ]
    )

    return app_context.ldap_connection.entries[ 0 ]
