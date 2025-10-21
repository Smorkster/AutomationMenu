
from dataclasses import dataclass
from pathlib import Path

from automation_menu.models.scriptmetadata import ScriptMetadata


@dataclass
class ScriptInfo:
    """ Class to hold information about a script """
    filename: str
    fullpath: Path
    scriptmeta: ScriptMetadata = None


    def __getattr__( self, name ):
        """ Assure that retreival of none existing attribute does not generate an exception """

        return None


    def add_attr( self, attr_name: str, attr_val: any ) -> None:
        """ Add an attribute to the ScriptInfo object """

        setattr( self, attr_name, attr_val )


    def set_attr( self, attr_name: str, attr_val:any, append: bool = False ) -> None:
        """ Append a value to an existing attribute or create it if it doesn't exist """

        if ( not hasattr( self, attr_name ) ):
            self.add_attr( attr_name, attr_val )

        elif append:
            setattr( self, attr_name, getattr( self, attr_name ) + attr_val )

        else:
            setattr( self, attr_name, attr_val )


    def get_attr( self, attr_name: str ) -> any:
        """ Get the value of an attribute if it exists, otherwise return None """

        if attr_name in [ 'filename', 'fullpath' ]:
            return getattr( self, attr_name )

        else:
            if hasattr( self.scriptmeta, attr_name ):
                return getattr( self.scriptmeta, attr_name )

            else:
                return None


