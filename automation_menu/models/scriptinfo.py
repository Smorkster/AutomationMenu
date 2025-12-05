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

from automation_menu.models.scriptmetadata import ScriptMetadata


@dataclass
class ScriptInfo:
    """ Class to hold information about a script """
    filename: str
    fullpath: Path
    scriptmeta: ScriptMetadata = None


    def add_attr( self, attr_name: str, attr_val: any ) -> None:
        """ Add an attribute to the ScriptInfo object

        Args:
            attr_name (str): Name of attribute to add
            attr_val (any): Value to add
        """

        setattr( self, attr_name, attr_val )


    def get_attr( self, attr_name: str ) -> any:
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


    def set_attr( self, attr_name: str, attr_val:any, append: bool = False ) -> None:
        """ Append a value to an existing attribute or create it if it doesn't exist

        Args:
            attr_name (str): Name of attribute
            attr_val (any): Value of attribute to set
            append (bool): Should the value be appended to existing value
        """

        if ( not hasattr( self, attr_name ) ):
            self.add_attr( attr_name, attr_val )

        elif append:
            setattr( self, attr_name, getattr( self, attr_name ) + attr_val )

        else:
            setattr( self, attr_name, attr_val )
