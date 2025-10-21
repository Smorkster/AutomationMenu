"""
Model for various meta data, specifying script permissions,
definition and more.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-17
"""

from dataclasses import dataclass, field

from automation_menu.models.enums import ScriptState
from automation_menu.models.scriptinputparameter import ScriptInputParameter


@dataclass
class ScriptMetadata:
    """ Complete metadata for a script """

    # Required fields (no defaults)
    synopsis: str
    author: str

    # Optional fields with sensible defaults
    description: str = ''
    state: ScriptState = ScriptState.DEV
    version: str = '1.0'

    # Access control
    required_ad_groups: list[ str ] = field( default_factory = list )
    allowed_users: list[ str ] = field( default_factory = list )

    # Parameters
    script_input_parameters: list[ ScriptInputParameter ] = field( default_factory = list )

    # UI behavior flags
    disable_minimize_on_running: bool = False


    def __post_init__( self ):
        """ Validate after initialization """

        if not self.synopsis:
            raise ValueError( 'Synopsis is required' )

        if not self.author:
            raise ValueError( 'Author is required' )


    def has_input_parameters( self ) -> bool:
        """ Check if script accepts parameters """

        return len( self.script_input_parameters ) > 0


    def requires_permission_check(self) -> bool:
        """ Check if access control is needed """

        return bool( self.required_ad_groups or self.allowed_users )
