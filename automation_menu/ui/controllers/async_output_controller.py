"""
Output queue controller

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

import asyncio
import json
import logging
import queue
import threading
import tkinter as tk

from datetime import datetime
from logging import Logger
from re import Match
from tkinter.ttk import Button
from typing import Callable

from automation_menu.models import SysInstructions
from automation_menu.models.enums import OutputStyleTags
from automation_menu.models.exechistory import ExecHistory, Output
from automation_menu.services.history_manager import HistoryManager


class AsyncOutputController:
    """ Control asynchronous processing of output queue messages and UI updates."""

    def __init__( self, output_queue: queue.Queue, text_widget: tk.Text, breakpoint_button: Button, history_manager: HistoryManager, api_callbacks: dict[ str, Callable ], logger: Logger ) -> None:
        """ Initialize the async output controller.

        Args:
            output_queue (queue.Queue): Queue to process.
            text_widget (tk.Text): Tkinter text widget that receives output text.
            breakpoint_button (Button): Button used to continue execution after a breakpoint.
            history_manager (HistoryManager): History manager used to store completed execution items.
            api_callbacks (dict[str, Callable]): Dictionary containing API callback functions.
            logger (Logger): General-purpose logger used throughout the application.
       """

        self.history_manager: HistoryManager = history_manager
        self.output_queue: queue.Queue = output_queue
        self.text_widget: tk.Text = text_widget
        self.breakpoint_button: Button = breakpoint_button
        self.api_callbacks: dict[ str, Callable ] = api_callbacks
        self._logger: Logger = logger

        self.loop: asyncio.AbstractEventLoop

        self._running: bool = False


    def _api_handler( self, handler: str, data: dict ) -> None:
        """ Run a registered API callback.

        Args:
            handler (str): Name of the API handler callback to run.
            data (dict): API data passed unmodified to the callback.
        """

        self.api_callbacks[ handler ]( data )


    async def _async_processor( self ) -> None:
        """ Run the asynchronous loop that processes output queue items."""

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

                    if processed is not None:
                        self._schedule_ui_update( processed_queue_item = processed )

            except Exception as e:
                logging.error( f'Error in async processor: { e }' )


    async def _async_process_queue_item( self, queue_item: str | SysInstructions | dict[ str, object ] ) -> dict[ str, object ] | SysInstructions | None:
        """ Process a queue item before scheduling a UI update.

        Args:
            queue_item (str | SysInstructions | dict[str, object]): Queue item to process.

        Returns:
            (dict[str, object] | SysInstructions | None): Normalized queue item, or None if no UI update should be scheduled.
        """

        if queue_item == 'timeout':

            return None

        elif queue_item == SysInstructions.CLEAROUTPUT:
            self._handle_ui_update( queue_item = queue_item )

        await asyncio.sleep( 0 )

        return self._normalize_queue_item( queue_item )


    def _get_queue_item(self) -> str | dict[ str, object ] | SysInstructions:
        """ Get the next queue item.

        Returns:
            (str | dict[str, object] | SysInstructions): Next queue item, or the string `'timeout'` if the queue is empty.
        """

        try:

            return self.output_queue.get( timeout = 1.5 )

        except queue.Empty:

            return 'timeout'


    def _handle_ui_update( self, queue_item: dict[ str, object ] | str | SysInstructions ) -> None:
        """ Apply a processed queue item to the UI.

        Args:
            queue_item (dict[str, object] | str | SysInstructions): Queue item used to update the UI.
        """

        from automation_menu.utils.localization import _

        if queue_item == SysInstructions.CLEAROUTPUT:
            self.text_widget.config( state = 'normal' )
            self.text_widget.delete( '1.0', tk.END )
            self.text_widget.config( state = 'disabled' )

            return

        if not isinstance( queue_item, dict ):

            return

        if queue_item.get('type') == 'api':
            handler_obj = queue_item.get( 'handler', '' )
            data_obj = queue_item.get( 'data', {} )

            if isinstance( handler_obj, str ) and isinstance( data_obj, dict ):
                if handler_obj in self.api_callbacks:
                    self._api_handler( handler = handler_obj, data = data_obj )

                else:
                    self._logger.warning( _( 'Unknown API handler {h}' ).format( h = handler_obj ) )

            else:
                self._logger.warning( _( 'Unknown API handler {h}' ).format( h = handler_obj ) )

            return

        line_obj = queue_item.get( 'line', '' )
        tag_obj = queue_item.get( 'tag', OutputStyleTags.SYSINFO )
        exec_item_obj = queue_item.get( 'exec_item' )

        if not isinstance( line_obj, str ):
            self._logger.warning( _( 'Queue item missing \'line\': {q}' ).format( q = queue_item ) )

            return

        if not isinstance( tag_obj, OutputStyleTags ):
            tag_obj = OutputStyleTags.SYSINFO

        self.text_widget.config( state = 'normal' )
        self.text_widget.insert( 'end', line_obj + '\n', tag_obj.value )
        self.text_widget.config( state = 'disabled' )
        self.text_widget.see( 'end' )

        if not tag_obj.name.startswith( 'SYS' ):
            if isinstance( exec_item_obj, ExecHistory ):
                o = Output( out_time = datetime.now(), output = line_obj )
                exec_item_obj.append_output( o )

        if queue_item.get( 'breakpoint'):
            self.breakpoint_button.config( state = 'normal' )

        elif queue_item.get( 'finished' ):
            if isinstance( exec_item_obj, ExecHistory ):
                exec_item_obj.end = datetime.now()
                self.history_manager.add_history_item( exec_item_obj )


    def _normalize_queue_item( self, queue_item: dict[ str, object ] | str | SysInstructions ) -> dict[ str, object ] | SysInstructions:
        """ Normalize a queue item into a UI-ready format.

        Args:
            queue_item (dict[str, object] | str | SysInstructions): Item read from the output queue.

        Returns:
            (dict[str, object] | SysInstructions): Normalized object for UI handling.
        """

        if isinstance( queue_item, str ):
            return {
                'line': queue_item.rstrip(),
                'tag': OutputStyleTags.INFO,
            }

        if isinstance( queue_item, SysInstructions ):

            return queue_item

        if isinstance( queue_item, dict ):
            line_obj = queue_item.get( 'line' )

            if isinstance( line_obj, str ) and '__API_START__' in line_obj:
                parsed = self._parse_api_message( api_message = line_obj )

                if isinstance( parsed, str ):
                    return {
                        'line': parsed.rstrip(),
                        'tag': OutputStyleTags.INFO,
                    }

                return parsed

            return queue_item

        return {
            'line': str( queue_item ),
            'tag': OutputStyleTags.INFO,
        }


    def _parse_api_message( self, api_message: str ) -> dict[ str, object ] | str:
        """ Parse an embedded API message from queue output.

        Args:
            api_message (str): Queue message to parse.

        Returns:
            api_msg_dict (dict[str, object]) | api_message (str): Parsed API message data, or the original message if no API payload was found.
        """

        import re

        api_msg_dict: dict[ str, object ] = { 'type': '', 'handler': '', 'data': {} }
        match: Match[ str ] | None = re.search( r'__API_START__(.+?)__API_END__', string = api_message )

        if match is None:

            return api_message

        try:
            api_msg = json.loads( match.group( 1 ) )
            api_msg_dict[ 'type' ] = 'api'
            api_msg_dict[ 'data' ] = api_msg[ 'data' ]

            if api_msg[ 'type' ] == 'progress':
                data = api_msg.get( 'data' ).get( 'set', api_msg.get( 'data' ).get( 'percent' ) )
                handler = 'update'

                if isinstance( data, str ):
                    handler = data

                api_msg_dict[ 'handler' ] = f'{ handler }_progress'

            elif api_msg[ 'type' ] == 'status':
                call_type = api_msg.get( 'data' ).get( 'set' )

                if call_type not in ( 'clear', 'get' ):
                    call_type = 'set'

                api_msg_dict[ 'handler' ] = f'{ call_type }_status'

            elif api_msg[ 'type' ] == 'setting':

                api_msg_dict[ 'handler' ] = 'setting'


        except json.JSONDecodeError as e:
            from automation_menu.utils.localization import _

            self._logger.error( _( 'Couldn\'t decode API JSON:\n{e}' ).format( e = e ) )

        return api_msg_dict


    def _run_async_loop( self ) -> None:
        """ Start and run the asynchronous event loop."""

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop( self.loop )

        try:
            self.loop.run_until_complete( self._async_processor() )

        except Exception as e:
            from automation_menu.utils.localization import _

            logging.exception( _( 'Error in async loop: %s' ).format( e = e ) )

        finally:
            self.loop.close()


    def _schedule_ui_update( self, processed_queue_item: dict | SysInstructions ) -> None:
        """ Schedule a processed queue item for UI handling.

        Args:
            processed_queue_item (dict | SysInstructions): Queue item to schedule for UI update.
        """

        if processed_queue_item:
            self.text_widget.after( 0, lambda: self._handle_ui_update( processed_queue_item ) )


    async def _shutdown( self ) -> None:
        """ Cancel running async tasks and stop the event loop."""

        tasks: list[ asyncio.Task ] = [ t for t in asyncio.all_tasks( self.loop ) if t is not asyncio.current_task() ]

        for task in tasks:
            task.cancel()

        await asyncio.gather( *tasks, return_exceptions = True )
        self.loop.stop()


    def closedown( self ) -> None:
        """ Stop queue processing and shut down the async loop thread."""

        self._running = False

        if self.loop and self.loop.is_running():
            self._loop_thread.join( timeout = 3 )

            try:
                if not self.loop.is_closed():
                    self.loop.call_soon_threadsafe( self.loop.stop )

            except:
                raise


    def start( self ) -> None:
        """ Start the background thread that processes output queue items."""

        if not self._running:
            self._running = True
            self._loop_thread = threading.Thread( target = self._run_async_loop, daemon = True )
            self._loop_thread.start()
