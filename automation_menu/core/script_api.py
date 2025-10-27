import json


MESSAGE_START = "__API_START__"
MESSAGE_END = "__API_END__"


def _send( msg_type: str, data: dict ):
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


def execute_script( name: str, args: dict = None ) -> None:
    """ API-entry for executing another script available in the Script-folder

    Args:
        name (str): Name of the script to execute, spelling must be correct
    """

    data = {
        'name': name,
        'args': args
    }

    _send( msg_type = 'exec', data = data )


def set_progress( percent: float ) -> None:
    """ API entry to update progressbar in main window

    Args:
        percent (float): Percent to update progressbar to
    """

    data = {
        'percent': percent
    }

    _send( msg_type = 'progress', data = data )
