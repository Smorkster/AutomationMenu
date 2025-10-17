from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union


class ScriptState( Enum ):
    """ Valid script states """
    DEV = 'Dev'
    TEST = 'Test'
    PROD = 'Prod'


@dataclass
class ScriptInputParameter:
    """ Represents a single input parameter """

    name: str
    type: Union[ str , int, bool ]
    required: bool = True
    default: Optional[ str ] = None
    description: str = ''


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
    parameters: list[ ScriptInputParameter ] = field( default_factory = list )

    # UI behavior flags
    disable_minimize_on_running: bool = False

    # Internal, not settable in ScriptInfo
    filename: str = field( default = '', init = False )
    fullpath: str = field( default = '', init = False )


    def __post_init__( self ):
        """ Validate after initialization """

        if not self.synopsis:
            raise ValueError( 'Synopsis is required' )

        if not self.author:
            raise ValueError( 'Author is required' )


    def has_parameters( self ) -> bool:
        """ Check if script accepts parameters """

        return len( self.parameters ) > 0


    def requires_permission_check(self) -> bool:
        """ Check if access control is needed """

        return bool( self.required_ad_groups or self.allowed_users )
