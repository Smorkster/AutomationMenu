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
    def __init__( self, script_info = None ):
        """ Class to hold script execution history """

        self.script_info = script_info
        self.output = []
        self.start = datetime.now()
        self.end = None


    def __repr__( self ) -> str:
        """ Custom representation """

        return str( {
            'ScriptInfo': self.script_info.filename,
            'start': str( self.start ),
            'end': str( self.end ),
            'script_output': ';'.join( [ repr( o ) for o in self.output ] )
            } )


    def add_end( self, time: datetime ):
        """ Set datetime when execution ended
        Args:
            time (datetime.datetime): Execution finished
        """

        self.end = time


    def append_output( self, item: dict[ datetime, str ] ):
        """ Add new item to output

        Args:
            item (dict[ datetime.datetime, str ]): Dict item with datetime and string from output
        """

        self.output.append( Output( **item ) )

