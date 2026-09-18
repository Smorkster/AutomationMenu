"""
Definition of ScriptInfo

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from automation_menu.models.scriptmetadata import ScriptMetadata
from automation_menu.models.user import User


@dataclass
class ScriptInfo:
    """ Stores file, metadata, and runtime information for a script. """

    # File info
    filename: str
    fullpath: Path

    # Parsed info
    scriptmeta: ScriptMetadata

    # Operational settings
    using_breakpoint: bool = False


    def __repr__( self ) -> str:
        """ Return the script path as the object representation.

        Returns:
            String representation of the script's full path.
        """

        return str( self.fullpath )


    def add_attr( self, attr_name: str, attr_val: Any ) -> None:
        """ Add an attribute to the ScriptInfo object

        Args:
            attr_name (str): Name of attribute to add
            attr_val (Any): Value to add
        """

        setattr( self, attr_name, attr_val )


    @classmethod
    def from_dict( cls: type[ ScriptInfo ], value: dict ) -> ScriptInfo:
        """ Create an instance from a dict
        
        Args:
            cls (type[ScriptInfo]): Current preset parameter class.
            value (dict): Dictionary containing the script info values.
        """

        m: ScriptMetadata = ScriptMetadata.from_dict( value.get( 'scriptmeta', {} ) )
        s: ScriptInfo = cls( filename = value[ 'filename' ],
                            fullpath = Path( value[ 'fullpath' ] ),
                            scriptmeta = m,
                            using_breakpoint = value.get( 'using_breakpoint', False ) )

        return s


    def get_attr( self, attr_name: str ) -> Any:
        """ Get an attribute value from the instance or its script metadata.

        Args:
            attr_name (str): Name of the attribute to retrieve.

        Returns:
            Any: Attribute value if found on this instance or `scriptmeta`, otherwise None.
        """

        if hasattr( self, attr_name ):

            return getattr( self, attr_name )

        else:
            if hasattr( self.scriptmeta, attr_name ):

                return getattr( self.scriptmeta, attr_name )

            else:

                return None


    def is_author( self, user: User ) -> bool:
        """ Verify if the user is author of this script

        Args:
            user (User): Current user running the application

        Returns:
            (bool): True if the current user is assigned as author
        """

        author_name: str = self.get_attr( 'author' )

        return ( bool( author_name )
                and user.AdObject.name.value == author_name.replace( ' (', '(' ) )



    def set_attr( self, attr_name: str, attr_val: Any, append: bool = False ) -> None:
        """ Set an attribute value, optionally appending to an existing value.

        Args:
            attr_name (str): Name of the attribute to set.
            attr_val (Any): Value to assign or append.
            append (bool): If True, append to the existing attribute value instead of replacing it.
        """

        if ( not hasattr( self, attr_name ) ):
            self.add_attr( attr_name, attr_val )

        elif append:
            setattr( self, attr_name, getattr( self, attr_name ) + attr_val )

        else:
            setattr( self, attr_name, attr_val )


    def to_dict( self ) -> dict:
        """ Transform into a dictionary """

        return { 'filename': self.filename,
                'fullpath': str( self.fullpath ),
                'using_breakpoint': self.using_breakpoint,
                'scriptmeta': self.scriptmeta.to_dict() }
