"""
Logging handler to write application errors and exceptions to file

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

import json

from pathlib import Path
from datetime import datetime
from logging import ERROR, Handler, LogRecord


class JsonFileHandler( Handler ):
    """ Write application error log records to a JSON lines file."""

    def __init__( self, project_root: Path ) -> None:
        """ Initialize the JSON file logging handler.

        Args:
            project_root (Path): Root directory of the project.
        """

        super().__init__( level = ERROR )

        now: datetime = datetime.now()
        log_dir: Path = (
            project_root
            / 'Log'
            / str( now.year )
            / str( now.month )
        )
        log_dir.mkdir( parents = True, exist_ok = True )

        self.log_file = log_dir / 'AppErrorLog.json'


    def emit( self, record: LogRecord ) -> None:
        """ Write a log record to the JSON log file.

        Args:
            record (LogRecord): Log record to write.
        """

        try:
            log_entry = {
                'timestamp': datetime.fromtimestamp( record.created ).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
                'message': record.getMessage(),
            }

            with self.log_file.open( 'a', encoding = 'utf-8' ) as f:
                f.write( json.dumps( log_entry, ensure_ascii = False ) + '\n' )

        except Exception:

            pass
