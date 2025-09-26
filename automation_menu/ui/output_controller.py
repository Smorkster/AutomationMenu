"""
Output queue controller

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import queue
import tkinter as tk

from tkinter.ttk import Button
from typing import Optional

from automation_menu.core.state import ApplicationState

class OutputController:
    """ Controller for output queue
     
    Args:
        output_queue (queue.Queue): Queue to handle
        text_widget (tk.Text): Tk Text widget to recieve output text
       """

    def __init__( self, output_queue: queue.Queue, text_widget: tk.Text, state: ApplicationState, breakpoint_button: Button ):
        self.output_queue = output_queue
        self.text_widget = text_widget
        self._polling = False
        self._app_state = state
        self._breakpoint_button = breakpoint_button

    def start_polling( self ):
        """  """
        if not self._polling:
            self._polling = True
            self._poll_queue()

    def _poll_queue( self ):
        """  """
        if not self._polling:
            return
        else:
            try:
                while True:
                    queue_item = self.output_queue.get_nowait()
                    if type( queue_item ) is str:
                        self._handle_queue_item( queue_item )

                    else:
                        self._handle_queue_item( queue_item )

            except queue.Empty:
                pass

            except Exception as e:
                self._handle_finished_message( str( e ) )
            self.text_widget.after( 100, self._poll_queue )

    def _enable_breakpoint_button( self ):
        self._breakpoint_button.state( [ '!disabled' ] )

    def _handle_queue_item( self, queue_item ):
        """  """
        if isinstance( queue_item, str ):
            self._append_text( queue_item )
        elif isinstance( queue_item, dict ):
            text = queue_item.get( 'line', '' )
            tag = queue_item.get( 'tag', 'suite_info' )

            self._append_text( text, tag )

            if queue_item.get( 'finished', False ):
                self._app_state.running_automation.process = None

    def stop_polling( self ):
        """Stop polling (for cleanup)"""
        self._polling = False

    def _append_text( self, text: str, tag: Optional[ str ] = None ):
        """ Append text to the widget with optional styling """
        self.text_widget.config( state = 'normal' )
        if tag:
            self.text_widget.insert( 'end', text.strip() + '\n', tag )
        else:
            self.text_widget.insert( 'end', text.strip() + '\n' )
        self.text_widget.see( 'end' )
        self.text_widget.config( state = 'disabled' )

    def _handle_finished_message( self, queue_item ):
        """ Handle special 'finished' messages """
        self._app_state.running_automation.process = None
