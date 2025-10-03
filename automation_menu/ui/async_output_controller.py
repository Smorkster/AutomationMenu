"""
Output queue controller

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import asyncio
from email import message
import logging
import queue
import threading
import tkinter as tk

from tkinter.ttk import Button
from typing import Optional

class AsyncOutputController:
    """ Controller for output queue
     
    Args:
        output_queue (queue.Queue): Queue to handle
        text_widget (tk.Text): Tk Text widget to recieve output text
       """

    def __init__( self, output_queue: queue.Queue, text_widget: tk.Text, breakpoint_button: Button ):
        self.output_queue = output_queue
        self.text_widget = text_widget
        self.breakpoint_button = breakpoint_button

        self.loop: Optional[ asyncio.AbstractEventLoop ] = None

        self._running = False
        self._executor = None

    def start( self ):
        """  """
        if not self._running:
            self._running = True
            threading.Thread( target = self._run_async_loop, daemon = True ).start()

    def _run_async_loop( self ):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop( self.loop )

        try:
            self.loop.run_until_complete( self._async_processor() )

        except:
            pass

        finally:
            self.loop.close()

    async def _async_processor( self ):
        while self._running:
            try:
                message = await self.loop.run_in_executor(
                    None,
                    self._get_queue_item
                )

                if message is None:
                    break

                if message != 'ProcessTerminated':
                    processed = await self._async_process_message( message )

                    self._schedule_ui_update( processed )

            except Exception as e:
                logging.error( f'Error in async processor: { e }' )

    def _get_queue_item( self ):
        try:
            return self.output_queue.get( timeout = 1.5 )

        except queue.Empty:
            return 'timeout'

    async def _async_process_message( self, message ):
        if message == 'timeout':
            return None

        await asyncio.sleep( 0 )

        return self._process_message_sync( message )

    def _schedule_ui_update( self, processed_message ):
        if processed_message:
            self.text_widget.after( 0, lambda: self._handle_ui_update( processed_message ) )

    def _handle_ui_update( self, queue_item ):
        self.text_widget.config( state = 'normal' )
        self.text_widget.insert( 'end', queue_item[ 'line' ] + '\n', queue_item[ 'tag' ] )
        self.text_widget.config( state = 'disabled' )
        self.text_widget.see( 'end' )

        if hasattr( queue_item, 'breakpoint') and queue_item[ 'breakpoint' ]:
            self.breakpoint_button.config( state = 'normal' )

    def _process_message_sync( self, message: str | dict ):
        """
        TODO
        match_py = re.search( r'^.*\((.*)\)<module>\(\)', output[ 'line' ].lower() )
        match_ps = re.search( r'^entering debug mode', output[ 'line' ].lower() )
        """

        if isinstance( message, str ):
            return {
                'line': message.rstrip(),
                'tag': 'suite_info'
            }

        else:
            return message
