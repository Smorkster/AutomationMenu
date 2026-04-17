"""
Definition of a predefined, automatic, run sequence

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0.0
Created: 2025-11-20
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Self
import uuid

from automation_menu.models.sequencestep import SequenceStep


@dataclass
class Sequence:
    """ Define an automatic run sequence """

    description: str = ''
    id: str = ''
    name: str = ''
    steps: list[ SequenceStep ] = field( default_factory = list[ SequenceStep ] )
    stop_on_error: bool = False


    @classmethod
    def from_dict( cls: type[ Sequence ], data: dict ) -> Sequence:
        """ Turn a dict into a Sequence

        Args:
            cls (type[Sequence]): Current sequence
            data (dict): Dictionary to turn into a Sequence
        """

        from automation_menu.utils.localization import _

        if not isinstance( data, dict ):

            raise TypeError( _( f'Data was not type as dict; got {t}' ).format( t = type( data ) ) )

        return cls(
            description = data[ 'description' ] or _( '<Description not set>' ),
            id = data[ 'id' ] or str( uuid.uuid4() ),
            name = data[ 'name' ],
            steps = [
                SequenceStep.from_dict( step )
                for step in data.get( 'steps', [] )
            ],
            stop_on_error = data[ 'stop_on_error' ] or False
        )


    def to_dict( self ) -> dict:
        """ Transform sequence to a dict

        Returns:
            (dict): Sequence as a dict
        """

        steps: list[ dict ] = []
        for step in self.steps:
            steps.append( step.to_dict() )

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stop_on_error': self.stop_on_error,
            'steps': steps
        }