

class ScriptInfo:
    """ Class to hold information about a script """
    def __init__( self, filename: str, directory: str ):
        """ Initialize ScriptInfo with filename and directory """

        self.filename = filename
        self.fullpath = directory.joinpath( filename )
        self.scriptmeta = None


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

        if hasattr( self, attr_name ):
            return getattr( self, attr_name )

        else:
            None


