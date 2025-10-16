from datetime import datetime


class ExecHistory:
    """ Class to hold script execution history """
    def __init__( self, script_info = None ):
        self.script_info = script_info
        self.output = []
        self.start = datetime.now()
        self.end = None


    def add_end( self, time: datetime ):
        """ Set datetime when execution ended
        
        Args:
            time (datetime.datetime): Execution finished
        """
        self.end = time


    def append_output( self, item: dict[ datetime, str ] ):
        """ Add new item to output

        Args:
            item (dict[ datetime.datetime, str ]): Dict item with datetime and string from output
        """
        self.output.append( item )

