"""
Handle output and different types of messages

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import queue

class OutputMessageManager:
    def __init__ ( self, queue: queue.Queue ):
        """ Configure output message depending on type of data
        
        Args:
            queue (queue.Queue): Queue to put the mesages to
        """

        self.output_queue = queue

    def error ( self, message: str , finished = False ):
        """ Place error-message in output queue """

        self.output_queue.put( { 'line': message , 'tag' : 'suite_error', 'finished': finished } )

    def finished ( self, message: str ):
        """ Place finished-message in output queue """

        self.output_queue.put( { 'line': message , 'tag': 'suite_success', 'finished': True } )

    def sysinfo ( self, message: str ):
        """ Place a system info message in output queue """

        self.output_queue.put( { 'line': message , 'tag': 'suite_sysinfo' } )

    def info ( self, message: str ):
        """ Place info-message in output queue """

        self.output_queue.put( { 'line': message , 'tag': 'suite_info' } )

    def success ( self, message: str ):
        """ Place success-message in output queue """

        self.output_queue.put( { 'line': message , 'tag': 'suite_success' } )

    def warning ( self, message: str ):
        """ Place warning-message in output queue """

        self.output_queue.put( { 'line' : message , 'tag' : 'suite_warning' } )
