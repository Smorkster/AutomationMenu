"""
Output queue controller

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import asyncio
from datetime import datetime
import logging
import queue
import threading
import tkinter as tk

from tkinter.ttk import Button
from typing import Optional

from automation_menu.models import SysInstructions
from automation_menu.ui.history_manager import HistoryManager


class AsyncOutputController:
    def __init__( self, output_queue: queue.Queue, text_widget: tk.Text, breakpoint_button: Button, history_manager: HistoryManager ):
        """ Controller for output queue
        
        Args:
            output_queue (queue.Queue): Queue to handle
            text_widget (tk.Text): Tk Text widget to recieve output text
            breakpoint_button (Button): The button to return execution after breakpoint in script
       """

        self.history_manager = history_manager
        self.output_queue = output_queue
        self.text_widget = text_widget
        self.breakpoint_button = breakpoint_button

        self.loop: Optional[ asyncio.AbstractEventLoop ] = None

        self._running = False
        self._executor = None


    def start( self ) -> None:
        """ Start thread to parse queue """

        if not self._running:
            self._running = True
            threading.Thread( target = self._run_async_loop, daemon = True ).start()


    def _run_async_loop( self ) -> None:
        """"  """

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop( self.loop )

        try:
            self.loop.run_until_complete( self._async_processor() )

        except:
            pass

        finally:
            self.loop.close()


    async def _async_processor( self ) -> None:
        """ Loop to handle queue inserted """

        while self._running:
            try:
                queue_item = await self.loop.run_in_executor(
                    None,
                    self._get_queue_item
                )

                if queue_item is None:
                    break

                if queue_item != SysInstructions.PROCESSTERMINATED:
                    processed = await self._async_process_queue_item( queue_item )

                    self._schedule_ui_update( processed )

            except Exception as e:
                logging.error( f'Error in async processor: { e }' )


    def _get_queue_item( self ) -> dict | str:
        """ Get the last queue item inserted

        Returns:
            (dict | str): Queue item
        """

        try:
            return self.output_queue.get( timeout = 1.5 )

        except queue.Empty:
            return 'timeout'


    async def _async_process_queue_item( self, queue_item ) -> str | dict:
        """ Process gathered queue item

        Args:
            message (Any): Queue item to process

        Returns:
            (dict): Message normalized to a dict
        """

        if queue_item == 'timeout':
            return None

        elif queue_item == SysInstructions.CLEAROUTPUT:
            self._handle_ui_update( queue_item = queue_item )

        await asyncio.sleep( 0 )

        return self._normalize_queue_item( queue_item )


    def _schedule_ui_update( self, processed_queue_item ) -> None:
        """ Schedule UI update with the processed message

        Args:
            processed_message (Any): Message to update output with
        """

        if processed_queue_item:
            self.text_widget.after( 0, lambda: self._handle_ui_update( processed_queue_item ) )


    def _handle_ui_update( self, queue_item: dict | str ) -> None:
        """ Do the actual UI update

        Args:
            queue_item (dict | str)
        """

        if queue_item == SysInstructions.CLEAROUTPUT:
            self.text_widget.config( state = 'normal' )
            self.text_widget.delete( '1.0', tk.END )
            self.text_widget.config( state = 'disabled' )

        else:
            self.text_widget.config( state = 'normal' )
            self.text_widget.insert( 'end', queue_item[ 'line' ] + '\n', queue_item[ 'tag' ] )
            self.text_widget.config( state = 'disabled' )
            self.text_widget.see( 'end' )

            if queue_item[ 'tag' ] != 'suite_sysinfo':
                queue_item[ 'exec_item' ].append_output( {
                    'datetime': datetime.now(),
                    'output': queue_item[ 'line' ]
                } )

            if queue_item.get( 'breakpoint' ):
                self.breakpoint_button.config( state = 'normal' )

            elif queue_item.get( 'finished' ):
                queue_item[ 'exec_item' ].end = datetime.now()
                self.history_manager.add_history_item( queue_item[ 'exec_item' ] )


    def _normalize_queue_item( self, queue_item: str | dict ) -> dict:
        """ Normalize message to a dict

        Args:
            message (dict | str): Message from queue to normalize

        Returns:
            (dict): A normalized message dict
        """

        """
        TODO
        match_py = re.search( r'^.*((.*))<module>()', output[ 'line' ].lower() )
        match_ps = re.search( r'^entering debug mode', output[ 'line' ].lower() )
        """

        if isinstance( queue_item, str ):
            return {
                'line': queue_item.rstrip(),
                'tag': 'suite_info'
            }

        else:
            return queue_item
