"""
Model for defining a parameter used as input for script execution

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from dataclasses import dataclass


@dataclass
class ScriptInputParameter:
    """ Represents a single input parameter """

    alternatives: list[ str ] | None = None
    default: str = ''
    description: str = ''
    name: str = ''
    required: bool = False
    type: str = ''


    @classmethod
    def from_dict( cls: type[ ScriptInputParameter ], value: dict ) -> ScriptInputParameter:
        """ Create instance from a dict

        Args:
            cls (type[ScriptInputParameter]): Current preset parameter class.
            value (dict): Dictionary containing the script input parameter values.
        """

        return cls( alternatives = value.get( 'alternatives' ),
                   default = value.get( 'default', '' ),
                   description = value.get( 'description', '' ),
                   name = value.get( 'name', '' ),
                   required = value.get( 'required', False ),
                   type = value.get( 'type', '' ) )


    def to_dict( self ) -> dict:
        """ Transform into a dictionary"""

        return { 'alternatives': self.alternatives,
                'default': self.default,
                'description': self.description,
                'name': self.name,
                'required': self.required,
                'type': self.type }
