"""
Definition of a predefined, automatic, run sequence

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

import uuid

from dataclasses import dataclass, field

from automation_menu.models.sequencestep import SequenceStep


@dataclass
class Sequence:
    """ Represents a predefined automatic run sequence."""

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

        Returns:
            A new sequence instance.

        Raises:
            TypeError: If `data` is not a dictionary.

        """

        from automation_menu.utils.localization import _

        if not isinstance( data, dict ):

            raise TypeError( _( f'Data was not of type \'dict\', got {t}' ).format( t = type( data ) ) )

        return cls(
            description = data.get( 'description', _( '<Description not set>' ) ),
            id = data.get( 'id', str( uuid.uuid4() ) ),
            name = data.get( 'name', _( 'Unnamed sequence' ) ),
            steps = [
                SequenceStep.from_dict( step )
                for step in data.get( 'steps', [] )
            ],
            stop_on_error = data.get( 'stop_on_error', False )
        )


    @classmethod
    def from_sequence( cls: type[ Sequence ], seq: Sequence ) -> Sequence:
        """ Create a copy of an existing sequence.

        Args:
            cls (type[ Sequence ]): Current sequence
            seq(Sequence): Sequence instance to copy.

        Returns:
            A new sequence instance with copied step data.
        """

        return cls( description = seq.description,
                   id = seq.id,
                   name = seq.name,
                   steps = [
                       SequenceStep.from_step( step = step )
                       for step in seq.steps
                       ],
                   stop_on_error = seq.stop_on_error )


    def to_dict( self ) -> dict:
        """ Convert the sequence to a dictionary

        Returns:
            (dict): Dictionary representation of the sequence.
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