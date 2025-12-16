"""
Output queue controller

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import asyncio
import json
import logging
import queue
from re import Match
import threading
import tkinter as tk

from datetime import datetime
from logging import Logger
from tkinter.ttk import Button
from typing import Callable

from automation_menu.models import SysInstructions
from automation_menu.models.enums import OutputStyleTags
from automation_menu.ui.history_manager import HistoryManager


class AsyncOutputController:
    def __init__( self,
                output_queue: queue.Queue,
                text_widget: tk.Text,
                breakpoint_button: Button,
                history_manager: HistoryManager,
                api_callbacks: dict[ str, Callable ],
                logger: Logger
                ) -> None:
        """ Controller for output queue

        Args:
            output_queue (queue.Queue): Queue to handle
            text_widget (tk.Text): Tk Text widget to recieve output text
            breakpoint_button (Button): The button to return execution after breakpoint in script
            history_manager (HistoryManager): History manager to access history list
            api_callbacks (dict[ str, Callable ]): Dictionary with API callbacks
            logger (Logger): General purpose logging object used through out application
       """

        self.history_manager: HistoryManager = history_manager
        self.output_queue: queue.Queue = output_queue
        self.text_widget: tk.Text = text_widget
        self.breakpoint_button: Button = breakpoint_button
        self.api_callbacks: dict[ str, Callable ] = api_callbacks
        self._logger: Logger = logger

        self.loop: asyncio.AbstractEventLoop | None = None

        self._running: bool = False
        self._executor: bool = None


    def _api_handler( self, handler: str, data: dict ) -> None:
        """ Run API-callback

        Args:
            handler (str): Name of API handler callback
            data (dict): API data, this will be sent, unedited, to specified callback
        """

        self.api_callbacks[ handler ]( data )


    async def _async_processor( self ) -> None:
        """ Loop to handle queue insertions """

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


    async def _async_process_queue_item( self, queue_item: str | SysInstructions | dict ) -> None | dict:
        """ Process gathered queue item

        Args:
            queue_item (str | SysInstructions | dict): Queue item to process

        Returns:
            (dict): Message normalized to a dict
        """

        if queue_item == 'timeout':

            return None

        elif queue_item == SysInstructions.CLEAROUTPUT:
            self._handle_ui_update( queue_item = queue_item )

        await asyncio.sleep( 0 )

        return self._normalize_queue_item( queue_item )


    def _get_queue_item( self ) -> dict | str:
        """ Get the last queue item inserted

        Returns:
            (dict | str): Queue item
        """

        try:

            return self.output_queue.get( timeout = 1.5 )

        except queue.Empty:

            return 'timeout'


    def _handle_ui_update( self, queue_item: dict | str ) -> None:
        """ Do the actual UI update

        Args:
            queue_item (dict | str): Queued item to update UI from
        """

        from automation_menu.utils.localization import _

        if queue_item == SysInstructions.CLEAROUTPUT:
            self.text_widget.config( state = 'normal' )
            self.text_widget.delete( '1.0', tk.END )
            self.text_widget.config( state = 'disabled' )

        elif isinstance( queue_item, dict ):

            if queue_item.get( 'type' ) == 'api':
                handler: str = queue_item.get( 'handler' )
                data: dict[ str, str ] = queue_item.get( 'data', {} )

                if handler in self.api_callbacks:
                    self._api_handler( handler = queue_item[ 'handler' ] , data = queue_item[ 'data' ] )

                else:
                    self._logger.warning( _( 'Unknown API handler {h}' ).format( h = handler ) )

            else:
                line: str = queue_item.get( 'line' )
                tag: OutputStyleTags = queue_item.get( 'tag', OutputStyleTags.SYSINFO )

                if line is None:
                    self._logger.warning( _( 'Queue item missing \'line\': {q}' ).format( q = queue_item ) )

                    return

                else:
                    self.text_widget.config( state = 'normal' )
                    self.text_widget.insert( 'end', queue_item[ 'line' ] + '\n', tag.value )
                    self.text_widget.config( state = 'disabled' )
                    self.text_widget.see( 'end' )

                    # Log queue output in exec history
                    if not queue_item[ 'tag' ].name.startswith( 'SYS' ):
                        queue_item[ 'exec_item' ].append_output( {
                            'out_time': datetime.now(),
                            'output': queue_item[ 'line' ]
                        } )

                    if queue_item.get( 'breakpoint' ):
                        self.breakpoint_button.config( state = 'normal' )

                    elif queue_item.get( 'finished' ):
                        queue_item[ 'exec_item' ].end = datetime.now()
                        self.history_manager.add_history_item( queue_item[ 'exec_item' ] )


    def _normalize_queue_item( self, queue_item: str | dict ) -> dict[ str, dict | OutputStyleTags | str ]:
        """ Normalize message to a dict

        Args:
            queue_item (dict | str): Queued item to normalize

        Returns:
            (dict): A normalized message dict
        """

        if isinstance( queue_item, str ):

            return {
                'line': queue_item.rstrip(),
                'tag': OutputStyleTags.INFO
            }

        elif isinstance( queue_item, dict ):
            if '__API_START__' in queue_item[ 'line' ]:
                return self._parse_api_message( queue_item )

            else:

                return queue_item

        else:

            return queue_item


    def _parse_api_message( self, queue_item: dict ) -> dict[ str, dict | str ]:
        """ Parse API call from queue item

        Args:
            queue_item (dict): Queue item to parse

        Returns:
            (dict): Dictionary with name of API handler and recieved data
        """

        import re

        match: Match = re.search( r'__API_START__(.+?)__API_END__', string = queue_item[ 'line' ] )

        if match:
            try:
                api_msg = json.loads( match.group( 1 ) )

                if api_msg[ 'type' ] == 'progress':
                    data = api_msg.get( 'data' ).get( 'set', api_msg.get( 'data' ).get( 'percent' ) )
                    handler = 'update'

                    if isinstance( data, str ):
                        handler = data

                    return { 'type': 'api', 'handler': f'{ handler }_progress', 'data': api_msg[ 'data' ] }

                elif api_msg[ 'type' ] == 'status':
                    call_type = api_msg.get( 'data' ).get( 'set' )

                    if call_type not in ( 'clear', 'get' ):
                        call_type = 'set'

                    return { 'type': 'api', 'handler': f'{ call_type }_status', 'data': api_msg[ 'data' ] }

                elif api_msg[ 'type' ] == 'setting':

                    return { 'type': 'api', 'handler': 'setting', 'data': api_msg.get( 'data' ) }


            except json.JSONDecodeError as e:
                from automation_menu.utils.localization import _

                self._logger.error( _( 'Couldn\'t decode API JSON:\n{e}' ).format( e = e ) )
 
                pass


    def _run_async_loop( self ) -> None:
        """" Startup the async loop """

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop( self.loop )

        try:
            self.loop.run_until_complete( self._async_processor() )

        except Exception as e:
            from automation_menu.utils.localization import _

            logging.exception( _( 'Error in async loop: %s' ).format( e = e ) )

        finally:
            self.loop.close()


    def _schedule_ui_update( self, processed_queue_item: dict ) -> None:
        """ Schedule UI update with the processed message

        Args:
            processed_queue_item (dict): Queued item to schedule update for
        """

        if processed_queue_item:
            self.text_widget.after( 0, lambda: self._handle_ui_update( processed_queue_item ) )


    async def _shutdown( self ) -> None:
        """ Gather and cancel all tasks and stop the async loop """

        tasks: list[ asyncio.Task ] = [ t for t in asyncio.all_tasks( self.loop ) if t is not asyncio.current_task() ]

        for task in tasks:
            task.cancel()

        await asyncio.gather( *tasks, return_exceptions = True )
        self.loop.stop()


    def closedown( self ) -> None:
        """ Close asyncio """

        self._running = False

        if self.loop and self.loop.is_running():
            self._loop_thread.join( timeout = 3 )

            try:
                self.loop.call_soon_threadsafe( self.loop.stop )

            except:
                raise


    def start( self ) -> None:
        """ Start thread to parse queue """

        if not self._running:
            self._running = True
            self._loop_thread = threading.Thread( target = self._run_async_loop, daemon = True )
            self._loop_thread.start()
