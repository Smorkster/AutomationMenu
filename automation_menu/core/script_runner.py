"""
Object representing a script
Contains script info and a runner

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""


import os
import queue
import re
import subprocess
import threading
from io import TextIOWrapper
from tkinter import Menu
from tkinter.ttk import Button, Label
from automation_menu.models import ScriptInfo
#from automation_menu.ui.main_window import AutomationMenuWindow
from automation_menu.utils.email_handler import report_script_error
from automation_menu.utils.screenshot import take_screenshot

class ScriptMenuItem:
#    def __init__ ( self, script_menu: Menu, script_info: ScriptInfo, main_object: AutomationMenuWindow ):
    def __init__ ( self, script_menu: Menu, script_info: ScriptInfo, main_object ):
        """ Object for representing a script in the menu. """

        from automation_menu.utils.localization import _

        self.script_menu = script_menu
        self.script_info = script_info
        self.script_path = script_info.fullpath
        self.master_self = main_object
        self.master_self.app_state.running_automation = self
        self.process = None
        self.label_text = ''
        self._in_debug = False
        style = 'TButton'

        if hasattr( self.script_info, 'Synopsis' ):
            self.label_text = self.script_info.Synopsis
        else:
            self.label_text = self.script_info.filename

        if hasattr( self.script_info, 'State' ) and self.script_info.State == 'Dev':
            self.label_text = self.label_text + _( ' (Dev)' )
            style = 'Dev.TLabel'
        else:
            style = 'Script.TLabel'

        self.script_button = Label( self.script_menu, text = self.label_text, style = style, borderwidth=1 )
        self.script_button.bind( '<Button-1>' , lambda e: self.run_script() )

        # Add tooltip to this button
        if hasattr( self.script_info, 'Description' ):
            from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip

            desc = self.script_info.get_attr( 'Description' )
            dev = False
            if self.script_info.get_attr( 'State' ) == 'Dev':
                desc += f'\n\n{ _( 'In development, and should only be run by its developer.' ) }'
                dev = True

            tt = AlwaysOnTopToolTip( widget = self.script_button, msg = desc )
            self.master_self.language_manager.add_widget( ( tt, self.script_info.Description, dev ) )

    def continue_breakpoint( self ):
        """ Continue execution of the script after hitting a breakpoint """

        self.process.stdin.write( 'c\n' )
        self.process.stdin.flush()
        self.master_self.btnContinueBreakpoint.after( 0, self.master_self.enable_breakpoint_button() )
        self._in_debug = False

    def set_window_minimized_on_running( self ):
        """ Set the main window to a minimized state when a script is running """

        if self.master_self.app_state.settings.get( 'minimize_on_running' ) and hasattr( self.master_self , 'old_window_geometry' ) and not self.script_info.DisableMinimizeOnRunning:
            win_width = 400
            win_height = 100
            if self.master_self.root.winfo_height() == self.master_self.old_window_geometry[ 'h' ] and self.master_self.root.winfo_width() == self.master_self.old_window_geometry[ 'w' ]:
                if self.master_self.app_state.settings.get( 'minimize_on_running' ):
                    self.master_self.root.geometry( newGeometry = f'{ win_width }x{ win_height }+{ self.master_self.root.winfo_screenwidth() - win_width  }+{ self.master_self.root.winfo_screenheight() - win_height - 100 }' )
            else:
                self.master_self.root.geometry( newGeometry = f'{ self.master_self.old_window_geometry['w'] }x{ self.master_self.old_window_geometry['h'] }+{ self.master_self.old_window_geometry['x'] }+{ self.master_self.old_window_geometry['y'] }' )

    def read_process_pipes( self, out, err ):
        """ Initiate pipe readers and populate queue with each output line """

        # Constants
        PIPE_OPENED = 1
        PIPE_OUTPUT = 2
        PIPE_CLOSED = 3
        q = queue.Queue()

        def pipe_reader( name, pipe: TextIOWrapper ):
            """ Reads a single pipe into output queue """

            try:
                for line in iter( pipe.readline, '' ):
                    if pipe.closed:
                        q.put( ( PIPE_CLOSED, name, ) )
                        #break
                    if line:
                        q.put( ( PIPE_OUTPUT, { 'n': name, 'line': line.rstrip() } , ) )

            finally:
                q.put( ( PIPE_CLOSED, name, ) )

        # Start a reader for each pipe
        threading.Thread( target = pipe_reader, args = ( 'stderr', err, ) , daemon = True ).start()
        threading.Thread( target = pipe_reader, args = ( 'stdout', out, ) , daemon = True ).start()

        # Use a counter to determine how many pipes are left open.
        # Return if all are closed
        pipe_count = 2

        # Read the queue in order, blocking if there's no data
        for data in iter( q.get, '' ):
            code = data[ 0 ]
            if code == PIPE_CLOSED:
                pipe_count -= 1
            elif code == PIPE_OUTPUT:
                yield data[ 1 : ][0]
            if pipe_count == 0:
                return

    def run_script( self ):
        """ Run the script in a separate thread """
        from automation_menu.utils.localization import _

        def worker():
            """ Start a process to run the script """

            from automation_menu.utils.localization import _

            try:
                self.script_menu.withdraw()
                self.master_self.tabControl.select( 0 )
                self.master_self.output_message_manager.info( _( 'Starting ' ) + self.script_info.Synopsis + "'" )

                if self.script_info.filename.endswith( '.py' ) and self.script_info.get_attr( 'UsingBreakpoint' ):
                    env = os.environ
                    #env['PYTHONBREAKPOINT'] = "0"
                    self.process = subprocess.Popen( 
                        args = [ 'python', self.script_path ],
                        stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE,
                        stdin = subprocess.PIPE,
                        text = True,
                        bufsize = 0,
                        encoding = 'utf-8',
                        shell = True,
                        env = env
                    )
                elif self.script_info.filename.endswith( '.py' ):
                    self.process = subprocess.Popen(
                        args = [ 'python', self.script_path ],
                        stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE,
                        stdin = subprocess.PIPE,
                        text = True,
                        bufsize = 0,
                        encoding = 'utf-8',
                        shell = True
                    )
                elif ( self.script_info.filename.endswith( '.ps1' ) ):
                    # -*- coding: iso-8859-1 -*-
                    self.process = subprocess.Popen(
                        args = [ 'powershell.exe', self.script_path, '-NoExit' ],
                        stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE,
                        stdin = subprocess.PIPE,
                        text = True,
                        bufsize = 0
                    )
                self.master_self.app_state.running_automation = self

                # Need to make a copy of stderr, to separate the stdout and stderr pipes
                fd = self.process.stderr.fileno()
                my_stderr = os.fdopen( os.dup( fd ) )
                os.close( fd )

                for output in self.read_process_pipes( out = self.process.stdout, err = my_stderr ):
                    match_py = re.search( r'^.*\((.*)\)<module>\(\)', output[ 'line' ].lower() )
                    match_ps = re.search( r'^entering debug mode', output[ 'line' ].lower() )
                    if match_py:
                        line_nr = match_py.group( 1 )
                        self.enter_debug( row = line_nr )
                    elif match_ps:
                        self.enter_debug()
                    else:
                        if not self._in_debug:
                            if output[ 'n' ] == 'stdout':
                                self.master_self.output_message_manager.info( output[ 'line' ] )
                            else:
                                self.master_self.output_message_manager.error( output[ 'line' ] )

                self.process.stdout.close()
                my_stderr.close()
                self.process.wait()

                if self.process.returncode == 0:
                    self.master_self.output_message_manager.finished( _( 'Done ✅' ) )
                else:
                    self.master_self.output_message_manager.error( _( 'Exited with code {return_code} ❌' ).format( return_code = str( self.process.returncode ) ), finished = True )
                    self._report_error()

                if hasattr( self.script_info , 'DisableMinimizeOnRunning' ) and not self.script_info.DisableMinimizeOnRunning:
                    self.set_window_minimized_on_running()

            except Exception as e:
                self.master_self.output_message_manager.error( _( 'Exception ❗: {error}' ).format( error = str( e ) ), finished = True )
                self._report_error( message = e )
            finally:
                self.process = None

        if self.master_self.app_state.running_automation.process == None:
            if hasattr( self.script_info , 'DisableMinimizeOnRunning' ) and not self.script_info.DisableMinimizeOnRunning:
                self.set_window_minimized_on_running()
            self.master_self.output_controller.start_polling()
            threading.Thread( target = worker, daemon = True ).start()
        else:
            self.master_self.output_message_manager.error( _( 'Another script is running, only one allowed at a time.' ), finished = True )
        self.master_self.tbOutput.see( 'end' )

    def _report_error( self, message: str = None ):
        """ Send report to author of script error """
        from automation_menu.utils.localization import _

        if not message:
            message = self.master_self.tbOutput.get( '1.0', 'end-1c' )

        if self.master_self.app_state.settings.include_ss_in_error_mail:
            ss_path = take_screenshot( root_window = self.master_self.root, script = self.script_info, file_name_prefix = self.master_self.app_state.secrets.get( 'error_ss_prefix' ) )
        else:
            ss_path = None

        report_script_error( app_state = self.master_self.app_state,
                            error_msg = message,
                            script_info = self.script_info,
                            screenshot = ss_path
                            )
        self.master_self.output_message_manager.sysinfo( _( 'A mail with the error message was sent to script developer.' ) )

    def enter_debug( self, row: int = None ):
        """ Set application in debug mode

        Args:
            row (int): Row number that have the breakpoint
        """

        from automation_menu.utils.localization import _

        self.master_self.btnContinueBreakpoint.after( 0, self.master_self.enable_breakpoint_button )
        line_nr = str( row ) if row else ''
        line =_( 'A breakpoint occured in the script at row {line_nr}. Click \'Continue\' to reactivate script.' ).format( line_nr = line_nr )
        self.master_self.output_message_manager.sysinfo( line )
        self._in_debug = True

    def exit_debug( self ):
        """ Reset debug flag """

        self._in_debug = False
