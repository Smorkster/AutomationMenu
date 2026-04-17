"""
Definition of ScriptInfo

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-31
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from automation_menu.models.scriptmetadata import ScriptMetadata
from automation_menu.models.user import User


@dataclass
class ScriptInfo:
    """ Class to hold information about a script """

    # File info
    filename: str
    fullpath: Path

    # Parsed info
    scriptmeta: ScriptMetadata

    # Operational settings
    using_breakpoint: bool = False


    def __repr__( self ) -> str:
        """ Custom representation string """

        return str( self.fullpath )


    def add_attr( self, attr_name: str, attr_val: Any ) -> None:
        """ Add an attribute to the ScriptInfo object

        Args:
            attr_name (str): Name of attribute to add
            attr_val (Any): Value to add
        """

        setattr( self, attr_name, attr_val )


    def get_attr( self, attr_name: str ) -> Any:
        """ Get the value of an attribute if it exists, otherwise return None

        Args:
            attr_name (str): Name of attribute to retrieve
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

        return (
            bool( author_name )
            and user.AdObject.name.value == author_name.replace( ' (', '(' )
        )



    def set_attr( self, attr_name: str, attr_val: Any, append: bool = False ) -> None:
        """ Append a value to an existing attribute or create it if it doesn't exist

        Args:
            attr_name (str): Name of attribute
            attr_val (Any): Value of attribute to set
            append (bool): Should the value be appended to existing value
        """

        if ( not hasattr( self, attr_name ) ):
            self.add_attr( attr_name, attr_val )

        elif append:
            setattr( self, attr_name, getattr( self, attr_name ) + attr_val )

        else:
            setattr( self, attr_name, attr_val )
