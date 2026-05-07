"""
Model for a pre set parameter for sequence step

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PreSetParam:
    """ Represents a preset parameter for a sequence step """

    name: str = ''
    set: str = ''


    @classmethod
    def from_dict( cls: type[ PreSetParam ], value: dict[ str, str ] ) -> PreSetParam:
        """ Create a preset parameter from a dictionary.

        Args:
            cls (type[PreSetParam]): Current preset parameter class.
            value (dict[str, str]): Dictionary containing the preset parameter values.

        Returns:
            PreSetParam: New preset parameter instance.
        """

        return cls( name = value[ 'name' ],
                   set = value[ 'set' ]
                   )


    @classmethod
    def from_psp( cls: type[ PreSetParam ], value: PreSetParam ) -> PreSetParam:
        """ Create a copy of an existing preset parameter.

        Args:
            cls (type[PreSetParam]): Current preset parameter class.
            value (PreSetParam): Preset parameter instance to copy.

        Returns:
            PreSetParam: New preset parameter instance with the same values.
        """

        return cls( name = value.name,
                   set = value.set
                   )


    def to_dict( self ) -> dict[ str, str ]:
        """ Convert the preset parameter to a dictionary.

        Returns:
            Dictionary representation of the preset parameter.
        """

        return {
            'name': self.name,
            'set': self.set
        }
