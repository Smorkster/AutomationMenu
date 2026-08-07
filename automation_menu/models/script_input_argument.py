"""
Model for an input argument for when running script

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InputArgument:
    """ Represents an input argument for calling a script """

    name: str = ''
    value: str = ''


    @classmethod
    def from_dict( cls: type[ InputArgument ], value: dict[ str, str ] ) -> InputArgument:
        """ Create an input argument from a dictionary.

        Args:
            cls (type[InputArgument]): Current input argument class.
            value (dict[str, str]): Dictionary containing the input argument values.

        Returns:
            InputArgument: New input argument instance.
        """

        return cls( name = value[ 'name' ],
                   value = value[ 'value' ] )


    @classmethod
    def from_ia( cls: type[ InputArgument ], value: InputArgument ) -> InputArgument:
        """ Create a copy of an existing input argument.

        Args:
            cls (type[InputArgument]): Current input argument class.
            value (InputArgument): InputArgument instance to copy.

        Returns:
            InputArgument: New input argument instance with the same values.
        """

        return cls( name = value.name,
                   value = value.value )


    def to_dict( self ) -> dict[ str, str ]:
        """ Convert the input argument to a dictionary.

        Returns:
            Dictionary representation of the input argument.
        """

        return { 'name': self.name,
                'value': self.value }
