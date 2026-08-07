"""
Model for holding execution history from one execution

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

import json

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.models import ScriptInfo

from automation_menu.models.script_output import ScriptOutput


class ExecHistory:
    def __init__( self, script_info: ScriptInfo ) -> None:
        """ Class to hold script execution history

        Args:
            script_info (ScriptInfo): Script info for associated execution
        """

        self.script_info: ScriptInfo = script_info
        self.output: list[ ScriptOutput ] = []
        self.start: datetime = datetime.now()
        self.end: datetime
        self.exit_code: int
        self.was_terminated: bool = False
        self.list_id: str = ''


    def __getitem__( self ) -> ExecHistory:
        """ Return this object

        Returns:
            (ExecHistory): Current object
        """

        return self


    def __repr__( self ) -> str:
        """ Custom representation

        Returns:
            (str): A custom string representation of this
                object
        """

        repr_str = {
            'script': {
                    'script': self.script_info.filename,
                    'author': self.script_info.scriptmeta.author
                },
            'execution': {
                'start': str( self.start ),
                'end': str( self.end ),
                'return_code': self.exit_code,
                'was_terminated': self.was_terminated
            },
            'script_output': ';'.join( [ repr( o ) for o in self.output ] )
            }

        return json.dumps( repr_str )


    def add_end( self, time: datetime ) -> None:
        """ Set datetime when execution ended

        Args:
            time (datetime): Execution finished
        """

        self.end = time


    def append_output( self, item: ScriptOutput ) -> None:
        """ Add new item to output

        Args:
            item (ScriptOutput): Output item from script output
        """

        self.output.append( item )


    def set_exit_code( self, exit_code: int ) -> None:
        """ Set return code from finished script execution

        Args:
            exit_code (int): Return code from script execution
        """

        self.exit_code = exit_code


    def set_terminated( self ) -> None:
        """ Set flag that execution was manually terminated """

        self.was_terminated = True


    def to_dict( self ) -> dict:
        """ Convert object to dict

        Returns:
            (dict): Parses this object to a dictionary
        """

        return {
            'script': {
                'filename': self.script_info.filename,
                'author': self.script_info.scriptmeta.author
            },
            'execution': {
                'start': self.start.isoformat(),
                'end': self.end.isoformat() if self.end else None,
                'exit_code': self.exit_code
            },
            'output': [
                {
                    'time': o.out_time.isoformat(),
                    'message': o.output
                }
                for o in self.output
            ]
        }
