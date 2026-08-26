"""
API definitions for communication between scripts and AutomationMenu.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


import json
import sys

MESSAGE_START = '__API_START__'
MESSAGE_END = '__API_END__'


def _get_api_response() -> str:
    """ Read a framed API response from standard input.

    Returns:
        str: The response payload between the API message markers.
    """

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
    """ Serialize and send a framed API message.

    Args:
        msg_type (str): API message type
        data (dict): API data
    """

    msg: dict[ str, dict | str ] = {
        'type': msg_type,
        'data': data
    }

    print( f'{ MESSAGE_START }{ json.dumps( msg ) }{ MESSAGE_END }', flush = True )


# region One time run
# region Progressbar
def determinate_progress() -> None:
    """ API entry to set progressbar to determinate mode """

    data: dict[ str, str ] = {
        'set': 'determinate'
    }

    _send( msg_type = 'progress', data = data )


def hide_progress() -> None:
    """ API entry to hide progressbar """

    data: dict[ str, str ] = {
        'set': 'hide'
    }

    _send( msg_type = 'progress', data = data )


def indeterminate_progress() -> None:
    """ API entry to set progressbar to indeterminate mode """

    data: dict[ str, str ] = {
        'set': 'indeterminate'
    }

    _send( msg_type = 'progress', data = data )


def set_progress( percent: float ) -> None:
    """ API entry to update progressbar value

    Args:
        percent (float): Precalculated value to set in the progressbar
    """

    data: dict[ str, float ] = {
        'percent': percent
    }

    _send( msg_type = 'progress', data = data )


def show_progress() -> None:
    """ API entry to show progressbar """

    data: dict[ str, str ] = {
        'set': 'show'
    }

    _send( msg_type = 'progress', data = data )
# endregion Progressbar


# region Settings
def get_keepass_shortcut() -> str:
    """ Get the configured KeePass global auto-type shortcut.

    This setting should be configured by the AutomationMenu user and match
    the shortcut configured in the KeePass application.

    Returns:
        str: The API response containing the KeePass shortcut configuration
            The shortcut will be a returned as a dict, json.dumped to a string
            The dict will be formated like:
            { "ctrl": bool, "alt": bool, "shift": bool, "key": str }
    """

    _send( msg_type = 'setting', data = { 'key': 'keepass_shortcut' } )

    return _get_api_response()
# endregion Settings


# region Textstatus
def clear_status() -> None:
    """ Clear the current status text """

    data: dict[ str, str ] = {
        'set': 'clear'
    }

    _send( msg_type = 'status', data = data )


def get_status() -> str:
    """ Get the currently displayed status text.

    Returns:
        str: The currently displayed status text.
    """

    data: dict[ str, str ] = {
        'set': 'get'
    }

    _send( msg_type = 'status', data = data )

    return _get_api_response()


def set_status( text: str, append: bool = False ) -> None:
    """ Set the status text.

    Newline characters are stripped from the text before it is sent.

    Args:
        text (str): Text to display as the status.
        append (bool): Whether to append the text to the current status.
    """

    data: dict[ str, bool | str ] = {
        'set': text,
        'append': append
    }

    _send( msg_type = 'status', data = data )
# endregion Textstatus
# endregion One time run


# region Persistent script
# region Progress
def set_persistent_progress( percent: float ) -> None:
    """ API entry to update progressbar value

    Args:
        percent (float): Precalculated value to set in the progressbar
    """

    data: dict[ str, float ] = { 'percent': percent }

    _send( msg_type = 'progress', data = data )
# endregion Progress

# region State
def send_persistent_state( state: str ) -> None:
    """ Set the state text for persistent script.

    Accepted states: IDLE, RUNNING, PAUSED

    Args:
        state (str): State to display the script is in.
    """

    if state.upper() not in [ 'IDLE', 'PAUSED', 'RUNNING' ]:

        raise ValueError( 'Invalid state name. Valid names are: IDLE, PAUSED, RUNNING' )

    data: dict[ str, str ] = { 'set': state }

    _send( msg_type = 'state', data = data )
# endregion State

# region Status
def send_persistent_status( text: str ) -> None:
    """ Set the status text for persistent script.

    Newline characters are stripped from the text before it is sent.

    Args:
        text (str): Text to display as the status.
    """

    data: dict[ str, str ] = { 'set': text }

    _send( msg_type = 'status', data = data )
# endregion Status

# endregion Persistent script