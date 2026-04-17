"""
Model for script output data

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
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


