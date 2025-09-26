"""
Authentication towards AD
And collecting AD functions

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import os
import sys
from dynamicinputbox import dynamic_inputbox as inputbox
from ldap3 import ALL, Connection, Server
from ldap3.core.exceptions import LDAPSocketOpenError
from automation_menu.core.state import ApplicationState
from automation_menu.models import Secrets

def connect_to_AD( app_state: ApplicationState ) -> None :
    """ Connect to Active Directory and return the connection object
    
    Returns:
        conn (ldap3.core.connection.Connection) - The connection setup after connecting
    """
    from automation_menu.utils.localization import _

    AD_loginattempts = 0
    main_input_text = _( 'Enter password for AD-domain\nP.S.\nThe password will not be stored' )

    while ( AD_loginattempts < 3 ):
        try:
            if AD_loginattempts == 0:
                inputbox_label_text = main_input_text
            else:
                inputbox_label_text = _( 'Wrong password. Try again\n{main_label_text}' ).format( main_label_text = main_input_text )

            password = inputbox( message = inputbox_label_text, input = True, input_show = '*', buttons = [ 'Ok', 'Avbryt' ] ).get( dictionary = True )
            if password.get( 'button' ) == 'Avbryt' or password.get( 'button' ) == 'Cancel':
                inputbox( title = 'Avbryter', message = _( 'No password was entered. Exiting.' ) )
                AD_loginattempts = 3
                sys.exit()
            server = Server( host = app_state.secrets.get( 'ldap_server' ), get_info = ALL )
            app_state.ldap_connection = Connection( server,
                               user = f'{ app_state.secrets.get( 'domain_name' ) }\\{ os.getenv( key = 'USERNAME', default = 'DefaultUser' ) }',
                               password = password.get('inputs')['Input'].get().decode(),
                               auto_bind = True
                             )
            break

        except SystemExit:
            raise SystemExit()

        except LDAPSocketOpenError as e:
            inputbox( title = _( 'Error' ), message =_( 'Could not connect to AD\n{error}\nExiting' ).format( error = str( e ) ) )
            AD_loginattempts = 3
            sys.exit()

        except Exception as e:
            AD_loginattempts = AD_loginattempts + 1

def get_user_adobject( id = None, app_state: ApplicationState = None ):
    """ Get the full AD-object of the current user """
    from automation_menu.utils.localization import _

    if id == None:
        user = os.getenv( key = 'USERNAME', default = 'DefaultUser' )
    else:
        user = id

    if not app_state.is_ldap_connected():
        raise ConnectionError( _( 'Not connected to LDAP' ) )

    app_state.ldap_connection.search(
        search_base = Secrets.get( 'ldap_search_base' ),
        search_filter = f'(sAMAccountName={ user })',
        attributes = [ '*' ]
    )

    return app_state.ldap_connection.entries[ 0 ]
