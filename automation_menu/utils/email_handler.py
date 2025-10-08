"""
Compose and send an email for error reporting
to script author

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import re
import smtplib

from datetime import datetime
from email.headerregistry import Address
from email.message import EmailMessage

from automation_menu.core.auth import get_user_adobject
from automation_menu.core.state import ApplicationState
from automation_menu.models import ScriptInfo, Secrets


def _compose( script_info: ScriptInfo, error_msg: str, screenshot: str, app_state: ApplicationState ) -> EmailMessage:
    """ Compose the mail body
    
    Args:
        script_info (ScriptInfo): Info about the script currently running
        error_msg (str): Message to for the mail
        screenshot (str): Path to screenshot to include in the mail
        current_user (User): User running the application

    Returns:
        msg (EmailMessage): The composed email
    """

    from automation_menu.utils.localization import _

    msg = EmailMessage()
    msg[ 'Subject' ] = _( 'Error occured in your automation script' )
    msg[ 'From' ] = Address( display_name = f'{ ( re.search( r'(.*)\(\w{4}\)$', app_state.current_user.AdObject.cn.value , re.DOTALL ) ).group( 1 ) }' ,
                            username = f'{ app_state.current_user.AdObject.mail.value.split( '@' )[0] }' ,
                            domain = f'{ app_state.current_user.AdObject.mail.value.split( '@' )[1] }' )
    to_list = [ Secrets.get( 'main_error_mail' ) ]

    if script_info.Author != None:
        get_dev_id = re.search( r'.*\((\w{4})\)$', script_info.Author, re.DOTALL )
        dev = get_user_adobject( id = get_dev_id.group( 1 ), app_state = app_state )
        if dev.mail.value != '':
            to_list.append( dev.mail.value )

    msg[ 'To' ] = ', '.join( to_list )

    if screenshot:
        img_included = _( 'See attached picture of main window' )

    else:
        img_included = '&nbsp;'

    header = _( 'Script error' )
    text1 = _( 'Error occured when your script ''<strong>{script_name}</strong>'' was running' ).format( script_name = script_info.filename )
    text2 = _( 'The error occured at: {time}' ).format( time = datetime.now().strftime( '%Y-%m-%d %H:%M:%S' ) )
    error_title = _( '<strong>Error message</strong>' )
    sign = _( 'This is an automatic message sent from AutomationMenu' )
    mail_content = f"""\
    <html><head></head><body>
        <h3>{ header }</h3>
        <p>{ text1 }</strong></p>
        <p>{ text2 }</p>
        <p>{ img_included }</p>
        <p>{ error_title }</p>
        <p>{ error_msg }</p>
        <p>&nbsp;</p>
        <p><em>{ sign }</em></p>
    </body></html>
    """
    msg.add_alternative( mail_content , subtype = 'html' )

    if screenshot:
        with open( screenshot , 'rb' ) as f:
            png_data = f.read()

        msg.add_attachment( png_data, maintype = 'image', subtype = 'png' )

    return msg


def report_script_error( app_state: ApplicationState, error_msg: str , script_info = None, screenshot:str = None ) -> bool:
    """ Send the composed mail to script author

    Args:
        app_state (ApplicationState): App state to take info from
        error_msg (str): Message to send to script author
        script_info (ScriptInfo): Info about script currently running
        screenshot (str): Path to screenshot to include

    Returns:
        (bool): True if the mail was sent successfully
    """

    try:
        msg = _compose( script_info = script_info, error_msg = error_msg, screenshot = screenshot, app_state = app_state )
        server = smtplib.SMTP( Secrets.get( 'smtprelay' ) )
        server.send_message( msg )
        server.quit()

        return True

    except Exception as e:
        raise