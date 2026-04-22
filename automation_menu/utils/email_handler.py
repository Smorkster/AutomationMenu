"""
Compose and send an email for error reporting
to script author

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from pathlib import Path
import re

from datetime import datetime
from email.headerregistry import Address
from email.message import EmailMessage
from re import Match
from smtplib import SMTP

from ldap3 import Connection, Entry

from automation_menu.core.auth import get_user_adobject
from automation_menu.models import ScriptInfo
from automation_menu.models.application_state import ApplicationState


def _compose( script_info: ScriptInfo | None, error_msg: str, screenshot: Path | None, app_state: ApplicationState, ldap_connection: Connection ) -> EmailMessage:
    """ Compose the mail body

    Args:
        script_info (ScriptInfo | None): Info about the script currently running
        error_msg (str): Message to for the mail
        screenshot (Path | None): Path to screenshot to include in the mail
        app_state (ApplicationState): User running the application
        ldap_connection (Connection): Connection used for obtaining developer of script

    Returns:
        msg (EmailMessage): The composed email
    """

    from automation_menu.utils.localization import _

    disp_name: str = ''
    disp_match: Match[str] | None = re.search( r'(.*)\(\w{4}\)$', app_state.current_user.AdObject.cn.value, re.DOTALL, )

    if disp_match is not None:
        disp_name = disp_match.group( 1 ).strip()

    msg = EmailMessage()
    msg[ 'Subject' ] = _( 'Error occured in your automation script' )
    msg[ 'From' ] = Address(
        display_name = disp_name,
        username = app_state.current_user.AdObject.mail.value.split( '@' )[ 0 ],
        domain = app_state.current_user.AdObject.mail.value.split( '@' )[ 1 ],
    )

    to_list: list[ str ] = [ str( app_state.secrets.get( 'main_error_mail' ) ) ]

    if script_info is not None:
        author = script_info.get_attr( 'Author' )

        if isinstance( author, str ):
            get_dev_id: Match[ str ] | None = re.search( r'.*\((\w{4})\)$', author, re.DOTALL, )

            if get_dev_id is not None:
                dev: Entry = get_user_adobject(
                    id = get_dev_id.group( 1 ),
                    ldap_search_base = str( app_state.secrets.get( 'ldap_search_base' ) ),
                    ldap_connection = ldap_connection,
                )

                if hasattr( dev, 'mail' ) and dev.mail.value != '':
                    to_list.append( dev.mail.value )

    msg[ 'To' ] = ', '.join( to_list )

    img_included = (
        _( 'See attached picture of main window' )
        if screenshot is not None
        else '&nbsp;'
    )

    script_name = script_info.get_attr( 'filename' ) if script_info is not None else _( 'Unknown script' )

    header = _( 'Script error' )
    text1 = _( "Error occured when your script '<strong>{script_name}</strong>' was running" ).format( script_name = script_name )
    text2 = _( 'The error occured at: {time}' ).format( time = datetime.now().strftime( '%Y-%m-%d %H:%M:%S' ) )
    error_title = _( '<strong>Error message</strong>' )
    sign = _( 'This is an automatic message sent from AutomationMenu' )

    mail_content = f"""\
    <html><head></head><body>
        <h3>{header}</h3>
        <p>{text1}</p>
        <p>{text2}</p>
        <p>{img_included}</p>
        <p>{error_title}</p>
        <p>{error_msg}</p>
        <p>&nbsp;</p>
        <p><em>{sign}</em></p>
    </body></html>
    """

    msg.add_alternative( mail_content, subtype='html' )

    if screenshot is not None:
        with open( screenshot, 'rb' ) as f:
            png_data = f.read()

        msg.add_attachment(
            png_data,
            maintype = 'image',
            subtype = 'png',
            filename = screenshot.name,
        )

    return msg


def send_error_mail( app_state: ApplicationState, error_msg: str, script_info: ScriptInfo , screenshot: Path , ldap_connection: Connection ) -> bool:
    """ Send the composed mail to script author

    Args:
        app_state (ApplicationState): App state to take info from
        error_msg (str): Message to send to script author
        script_info (ScriptInfo): Info about script currently running
        screenshot (Path): Path to screenshot to include
        ldap_connection (Connection): Connection to LDAP server

    Returns:
        (bool): True if the mail was sent successfully
    """

    try:
        msg = _compose(
            script_info = script_info,
            error_msg = error_msg,
            screenshot = screenshot,
            app_state = app_state,
            ldap_connection = ldap_connection
        )

        server = SMTP( str( app_state.secrets.get( 'smtprelay' ) ) )
        server.send_message( msg )
        server.quit()

        return True

    except Exception as e:
        raise e
