"""
Model for holding execution history from one execution

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-17
"""

from dataclasses import dataclass
from datetime import datetime
import json

#from automation_menu.models import scriptinfo

@dataclass
class Output:
    out_time: datetime
    output: str

    def __repr__( self ) -> str:
        """ Custom representation """

        return str( { 'time': str( self.out_time ), 'output': self.output } )


    def __str__( self ) -> str:
        """ Custom string conversion """

        return f'{ self.out_time.strftime( '%H:%M:%S' ) }: { self.output }'


class ExecHistory:
    #def __init__( self, script_info: scriptinfo.ScriptInfo = None ):
    def __init__( self, script_info = None ):
        """ Class to hold script execution history """

        self.script_info = script_info
        self.output = []
        self.start = datetime.now()
        self.end = None
        self.exit_code = None
        self.was_terminated = False


    def __repr__( self ) -> str:
        """ Custom representation """

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
            time (datetime.datetime): Execution finished
        """

        self.end = time


    def append_output( self, item: dict[ datetime, str ] ) -> None:
        """ Add new item to output

        Args:
            item (dict[ datetime.datetime, str ]): Dict item with datetime and string from output
        """

        self.output.append( Output( **item ) )


    def set_exit_code( self, exit_code: int ) -> None:
        """ Set return code from finished script execution

        Args:
            return_code (int): Return code from script execution
        """

        self.exit_code = exit_code


    def set_terminated( self ) -> None:
        """ Set flag that execution was manually terminated """

        self.was_terminated = True
