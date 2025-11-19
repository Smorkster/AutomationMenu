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

    response = []
    in_message = False
    buffer = ""

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

    msg = {
        'type': msg_type,
        'data': data
    }

    print( f'{ MESSAGE_START }{ json.dumps( msg ) }{ MESSAGE_END }', flush = True )


# region Progressbar
def set_progress( percent: float ) -> None:
    """ API entry to update progressbar in main window

    Args:
        percent (float): Precalculated value to set in the progressbar
    """

    data = {
        'percent': percent
    }

    _send( msg_type = 'progress', data = data )


def show_progress() -> None:
    """ API entry to show progressbar """

    data = {
        'set': 'show'
    }

    _send( msg_type = 'progress', data = data )


def hide_progress() -> None:
    """ API entry to hide progressbar """

    data = {
        'set': 'hide'
    }

    _send( msg_type = 'progress', data = data )


def determinate_progress() -> None:
    """ API entry to set progressbar as determinate """

    data = {
        'set': 'determinate'
    }

    _send( msg_type = 'progress', data = data )


def indeterminate_progress() -> None:
    """ API entry to set progressbar as indeterminate """

    data = {
        'set': 'indeterminate'
    }

    _send( msg_type = 'progress', data = data )
# endregion


# region Textstatus
def clear_status() -> None:
    """ Remove current status """

    data = {
        'set': 'clear'
    }

    _send( msg_type = 'status', data = data )


def get_status() -> str:
    """ Get what is currently set as status

    Returns:
        str: The currently displayed statustext
    """

    data = {
        'set': 'get'
    }

    _send( msg_type = 'status', data = data )
    return _get_api_response()


def set_status( text: str, append: bool = False ) -> None:
    """ Set a textstatus
    Text will be stripped of all new line characters

    Args:
        text (str): Text to set as status
    """

    data = {
        'set': text,
        'append': append
    }

    _send( msg_type = 'status', data = data )
# endregion
