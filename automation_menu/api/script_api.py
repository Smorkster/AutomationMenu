"""
API definition for script to AutomationMenu communication

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-31
"""

import json
import sys

MESSAGE_START = '__API_START__'
MESSAGE_END = '__API_END__'


def _get_api_response() -> None:
    """ Send API call and wait for response """

    response: list[ str ] = []
    in_message: bool = False
    buffer: str = ""

    for line in sys.stdin:
        buffer += line

        if not in_message and MESSAGE_START in buffer:
            # Start of message found
            in_message = True
            _, buffer = buffer.split( MESSAGE_START, 1 )

        if in_message:
            if MESSAGE_END in buffer:
                # End of message found
                line, _ = buffer.split( MESSAGE_END, 1 )
                response.append( line )
                break

            else:
                response.append( buffer )
                buffer = ""

        else:
            # MESSAGE_END was never found
            if in_message:
                response.append( buffer )

    return ''.join( response )


def _send( msg_type: str, data: dict ) -> None:
    """ Send API call for json parsing

    Args:
        msg_type (str): API message type
        data (dict): API data
    """

    msg: dict[ str, dict ] = {
        'type': msg_type,
        'data': data
    }

    print( f'{ MESSAGE_START }{ json.dumps( msg ) }{ MESSAGE_END }', flush = True )


# region Progressbar
def determinate_progress() -> None:
    """ API entry to set progressbar as determinate """

    data: dict[ str ] = {
        'set': 'determinate'
    }

    _send( msg_type = 'progress', data = data )


def hide_progress() -> None:
    """ API entry to hide progressbar """

    data: dict[ str ] = {
        'set': 'hide'
    }

    _send( msg_type = 'progress', data = data )


def indeterminate_progress() -> None:
    """ API entry to set progressbar as indeterminate """

    data: dict[ str ] = {
        'set': 'indeterminate'
    }

    _send( msg_type = 'progress', data = data )


def set_progress( percent: float ) -> None:
    """ API entry to update progressbar in main window

    Args:
        percent (float): Precalculated value to set in the progressbar
    """

    data: dict[ int ] = {
        'percent': percent
    }

    _send( msg_type = 'progress', data = data )


def show_progress() -> None:
    """ API entry to show progressbar """

    data: dict[ str ] = {
        'set': 'show'
    }

    _send( msg_type = 'progress', data = data )
# endregion Progressbar


# region Settings
def get_keepass_shortcut() -> dict:
    """ Get KeePass global auto-type shortcut
    This setting should be set by AutomationMenu user and should match
    setting set in KeePass application

    Returns:
        (dict): A dictionary with keys to use for KeePass global auto type
            Set dict will be formated like:
            { "ctrl": bool, "alt": bool, "shift": bool, "key": str }
    """

    _send( msg_type = 'setting', data = { 'key': 'keepass_shortcut' } )

    return _get_api_response()
# endregion Settings


# region Textstatus
def clear_status() -> None:
    """ Remove current status """

    data: dict[ str ] = {
        'set': 'clear'
    }

    _send( msg_type = 'status', data = data )


def get_status() -> str:
    """ Get what is currently set as status

    Returns:
        str: The currently displayed statustext
    """

    data: dict[ str ] = {
        'set': 'get'
    }

    _send( msg_type = 'status', data = data )

    return _get_api_response()


def set_status( text: str, append: bool = False ) -> None:
    """ Set a textstatus
    Text will be stripped of all new line characters

    Args:
        text (str): Text to set as status
        append (bool): Should status text be appended to current status
    """

    data: dict[ str, bool ] = {
        'set': text,
        'append': append
    }

    _send( msg_type = 'status', data = data )
# endregion Textstatus
