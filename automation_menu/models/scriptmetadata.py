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
    persistent_gui: bool = False
    persistent_gui_multiple: bool = False


    def __post_init__( self ) -> None:
        """ Validate required metadata after initialization.

        Raises:
            ValueError: If `synopsis` or `author` is empty,
                or both `persistent_gui` and `persistent_gui_multiple`
                are set.
        """

        if not self.synopsis:

            raise ValueError( 'Synopsis is required' )

        if not self.author:

            raise ValueError( 'Author is required' )

        if self.persistent_gui and self.persistent_gui_multiple:

            raise ValueError( 'persistent_gui and persistent_gui_multiple can''t be used at the same time' )


    @classmethod
    def from_dict( cls: type[ ScriptMetadata ], value: dict ) -> ScriptMetadata:
        """ Create an instance from a dict

        Args:
            cls (type[ScriptMetadata]): Current preset parameter class.
            value (dict): Dictionary containing the script meta data values.
        """

        try:
            state: ScriptState = ScriptState( value[ 'state' ] )

        except:
            state = ScriptState( 'Prod' )

        smd: ScriptMetadata = cls( synopsis = value[ 'synopsis' ],
                                  author = value[ 'author' ],
                                  description = value.get( 'description', '' ),
                                  state = state,
                                  version = value.get( 'version', '1.0' ),
                                  required_ad_groups = value.get( 'required_ad_groups', [] ),
                                  allowed_users = value.get( 'allowed_users', [] ),
                                  script_input_parameters = [ ScriptInputParameter.from_dict( d ) for d in value.get( 'script_input_parameters', [] ) ],
                                  disable_minimize_on_running = value.get( 'disable_minimize_on_running', False ),
                                  persistent_gui = value.get( 'persistent_gui', False ),
                                  persistent_gui_multiple = value.get( 'persistent_gui_multiple', False ) )

        return smd


    def has_input_parameters( self ) -> bool:
        """ Check whether the script accepts input parameters.

        Returns:
            True if one or more input parameters are defined, otherwise False.
        """

        return len( self.script_input_parameters ) > 0


    def requires_permission_check( self ) -> bool:
        """ Check whether script access control needs to be evaluated.

        Returns:
            True if required AD groups or allowed users are configured,
            otherwise False.
        """

        return bool( self.required_ad_groups or self.allowed_users )


    def to_dict( self ) -> dict:
        """ Transform into a dictionary

        Returns:
            (dict): Metadata as a dictionary
        """

        return { 'synopsis': self.synopsis,
                'author': self.author,
                'description': self.description,
                'state': self.state.value,
                'version': self.version,
                'required_ad_groups': self.required_ad_groups,
                'allowed_users': self.allowed_users,
                'script_input_parameters': [ i.to_dict() for i in self.script_input_parameters ],
                'disable_minimize_on_running': self.disable_minimize_on_running,
                'persistent_gui': self.persistent_gui,
                'persistent_gui_multiple': self.persistent_gui_multiple }
