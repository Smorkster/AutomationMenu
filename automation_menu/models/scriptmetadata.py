"""
Model for various meta data, specifying script permissions,
definition and more.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from dataclasses import dataclass, field

from automation_menu.models.enums import ScriptState
from automation_menu.models.scriptinputparameter import ScriptInputParameter


@dataclass
class ScriptMetadata:
    """ Stores metadata that defines script behavior and access control."""

    # Required fields
    synopsis: str
    author: str

    # Optional fields
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


    def __post_init__( self ) -> None:
        """ Validate required metadata after initialization.

        Raises:
            ValueError: If `synopsis` or `author` is empty.
        """

        if not self.synopsis:

            raise ValueError( 'Synopsis is required' )

        if not self.author:

            raise ValueError( 'Author is required' )


    def has_input_parameters( self ) -> bool:
        """ Check whether the script accepts input parameters.

        Returns:
            True if one or more input parameters are defined, otherwise False.
        """

        return len( self.script_input_parameters ) > 0


    def requires_permission_check(self) -> bool:
        """ Check whether script access control needs to be evaluated.

        Returns:
            True if required AD groups or allowed users are configured,
            otherwise False.
        """

        return bool( self.required_ad_groups or self.allowed_users )
