
from datetime import datetime
import os
from pathlib import Path


def write_exec_history( exec_items: str, root_dir: str ):
    """ Write settings to JSON file
    
    Args:
        exec_items (str): String representation of execution history
        root_dir (str): Path to file to write

    Raises:
        FileNotFoundError when the path is not valid
    """

    from automation_menu.utils.localization import _

    folder_path = Path.joinpath( root_dir, 'Log', str( datetime.now().year ) , str( datetime.now().month ) )

    if not folder_path.exists():
        folder_path.mkdir( parents = True, exist_ok = True )

    file_path = Path.joinpath( folder_path, 'ExecHistory.json' )

    if not file_path.exists():
        with open( file_path, 'w' ) as f:
            pass

    try:
        with open( file_path, mode = 'a', encoding = 'utf-8' ) as f:
            output_history_item = {
                'user': os.getenv( key = 'USERNAME', default = 'DefaultUser' ),
                'exec_output': exec_items.replace( '\\', '' )
            }

            f.write( '\n' )
            f.write( str( output_history_item ) )

    except FileNotFoundError as e:
        raise FileNotFoundError( _( 'Writing execution history error; file not found: {file_path}' ).format( file_path = file_path ) ) from e

    except Exception as e:
        raise e
