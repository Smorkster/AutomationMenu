"""
Compose and send an email for error reporting
to script author

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

import re

from datetime import datetime
from email.headerregistry import Address
from email.message import EmailMessage
from ldap3 import Connection, Entry
from re import Match
from pathlib import Path
from smtplib import SMTP

from automation_menu.core.auth import get_user_adobject
from automation_menu.models import ScriptInfo
from automation_menu.models.application_state import ApplicationState


def _compose( script_info: ScriptInfo | None, error_msg: str, screenshot: Path | None, app_state: ApplicationState, ldap_connection: Connection ) -> EmailMessage:
    """Compose an error-report email message.

    Args:
        script_info (ScriptInfo | None): Information about the script currently running.
        error_msg (str): Error message to include in the email.
        screenshot (Path | None): Path to a screenshot to attach to the email.
        app_state (ApplicationState): Application state containing current user and configuration data.
        ldap_connection (Connection): LDAP connection used to resolve the script author.

    Returns:
        msg (EmailMessage): Composed email message.
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
    """Send an error-report email to the script author.

    Args:
        app_state (ApplicationState): Application state to take mail configuration and user info from.
        error_msg (str): Error message to send.
        script_info (ScriptInfo): Information about the script currently running.
        screenshot (Path): Path to the screenshot to include.
        ldap_connection (Connection): Connection to the LDAP server.

    Returns:
        bool: True if the email was sent successfully.
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
