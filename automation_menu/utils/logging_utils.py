"""
Logging handler to write application errors and exceptions to file

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-12-12
"""

import json

from pathlib import Path
from datetime import datetime
from logging import ERROR, Handler, LogRecord


class JsonFileHandler( Handler ):
    def __init__( self, project_root: Path ) -> None:
        """ A logging handler to document errors occuring in application

        Args:
            project_root (Path): Root directory for project
        """

        super().__init__( level = ERROR )

        now = datetime.now()
        log_dir = (
            project_root
            / 'Log'
            / str( now.year )
            / str( now.month )
        )
        log_dir.mkdir( parents = True, exist_ok = True )

        self.log_file = log_dir / 'AppErrorLog.json'


    def emit(self, record: LogRecord ) -> None:
        """ Do the logging to file documentation

        Args:
            record (LogRecord): Log record to file
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
