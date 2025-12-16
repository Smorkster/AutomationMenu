"""
File handler to write execution history to file

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-31
"""

import json
from logging import Logger
import os

from datetime import datetime
from pathlib import Path, WindowsPath


def write_exec_history( exec_items: list[ dict ], root_dir: WindowsPath, logger: Logger ) -> None:
    """ Write settings to JSON file
    
    Args:
        exec_items (list[ dict ]): String representation of execution history
        root_dir (WindowsPath): Path to file to write
        logger (Logger): General purpose logging object

    Raises:
        FileNotFoundError when the path is not valid
    """

    from automation_menu.utils.localization import _

    folder_path: Path = Path.joinpath( root_dir, 'Log', str( datetime.now().year ) , str( datetime.now().month ) )

    if not folder_path.exists():
        folder_path.mkdir( parents = True, exist_ok = True )

    file_path: Path = Path.joinpath( folder_path, 'ExecHistory.jsonl' )

    if not file_path.exists():
        with open( file_path, 'w' ) as f:
            pass

    try:
        with open( file_path, mode = 'a', encoding = 'utf-8' ) as f:
            for item in exec_items:
                log_entry: dict[ str, str | dict ] = {
                    'timestamp': datetime.now().isoformat(),
                    'user': os.getenv( key = 'USERNAME', default = 'DefaultUser' ),
                    'execution': item
                }

                try:
                    f.write( json.dumps( log_entry ) )

                except:
                    logger.warning( _( 'Failed to serialize history item {h} ' ).format( h = item ) )

                f.write( '\n')

    except FileNotFoundError as e:
        raise FileNotFoundError( _( 'Writing execution history error; file not found: {file_path}' ).format( file_path = file_path ) ) from e

    except Exception as e:
        raise e
