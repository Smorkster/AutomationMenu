#!/usr/bin/env python3
"""
Automation Menu - Entry Point
Main launcher for the automation script management interface.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0.0
Created: 2025-09-25
"""

from __future__ import annotations

import argparse
import logging
import sys

from pathlib import Path

# Add the project root to Python path if needed
project_root = Path( __file__ ).parent.parent
sys.path.insert( 0, str( project_root ) )

from automation_menu.core.app_context import ApplicationContext
from automation_menu.core.script_execution_manager import ScriptExecutionManager
from automation_menu.filehandling.exec_history_handler import write_exec_history
from automation_menu.filehandling.secrets_handler import read_secrets_file
from automation_menu.filehandling.settings_handler import read_settingsfile, write_settingsfile
from automation_menu.models import Secrets, Settings, User
from automation_menu.models.application_state import ApplicationState
from automation_menu.ui.history_manager import HistoryManager
from automation_menu.ui.sequence_manager import SequenceManager
from automation_menu.utils.language_manager import LanguageManager
from automation_menu.utils.localization import change_language
from automation_menu.utils.script_manager import ScriptManager


def setup_logger( level: str = 'DEBUG' ) -> logging.Logger:
    """ Create a logger for debug purposes """

    logger = logging.getLogger( 'debug_logger' )
    level = logging._nameToLevel.get( level.upper(), logging.INFO )
    logger.setLevel( level = level )

    if not logger.handlers:
        handler = logging.StreamHandler()

        formater = logging.Formatter(
            "[%(levelname)s] %(filename)s:%(lineno)d - %(message)s"
        )

        handler.setFormatter( formater )
        logger.addHandler( handler )

        return logger


def main() -> None:
    """ Main entry point """

    def save_settings( obj: Settings ) -> None:
        """ Callback function to save settings to file """

        write_settingsfile( settings = obj, settings_file_path = app_state.secrets.get( 'settings_file_path' ) )

    input_parser = argparse.ArgumentParser()
    input_parser.add_argument( '--dev', action = 'store_true' )
    input_parser.add_argument( '--loglevel' )

    input_args = input_parser.parse_args()

    try:
        app_state = ApplicationState()
        app_context = ApplicationContext()
        for arg in input_args._get_kwargs():
            app_context.startup_arguments[ arg[ 0] ] = arg[ 1 ]

        app_context.debug_logger = setup_logger( level = app_context.startup_arguments[ 'loglevel' ] )

        app_state.secrets = Secrets( read_secrets_file( file_path = Path( __file__ ).resolve().parent / 'secrets.json' ) )
        read_settings = read_settingsfile( settings_file_path = app_state.secrets.get( 'settings_file_path' ), debug_logger = app_context.debug_logger )
        app_state.settings = Settings( settings_dict = read_settings, save_callback = save_settings )
        app_context.debug_logger.debug( msg = f'sequence list loaded with "{ len( app_state.settings.saved_sequences ) }" sequences' )

        change_language( language_code = app_state.settings.current_language )
        app_context.language_manager = LanguageManager( current_language = app_state.settings.current_language )

        from automation_menu.core.auth import connect_to_AD, get_user_adobject
        app_context.ldap_connection = connect_to_AD( app_state = app_state, app_context = app_context )
        app_state.current_user = User( get_user_adobject( app_state = app_state, app_context = app_context ) )

        app_context.script_manager = ScriptManager( app_context = app_context, app_state = app_state )
        app_context.execution_manager = ScriptExecutionManager( output_queue = app_context.output_queue, app_state = app_state )
        app_context.sequence_manager = SequenceManager( app_context = app_context, app_state = app_state, saved_sequences = app_state.settings.saved_sequences )
        app_context.history_manager = HistoryManager()

        # Launch the main application window
        from automation_menu.ui.main_window import AutomationMenuWindow
        from automation_menu.utils.localization import _
        AutomationMenuWindow( app_state = app_state, app_context = app_context )

        write_exec_history(
            exec_items = app_context.history_manager.get_history_list(),
            root_dir = Path( __file__ ).resolve().parent
        )

    except KeyboardInterrupt:
        print( _( 'Application interrupted by user' ) )
        sys.exit( 0 )

    except SystemExit:
        raise

    except Exception as e:
        from dynamicinputbox import dynamic_inputbox as inputbox

        # Handle any unexpected/unhandled errors
        message = _( 'An unexpected error occurred:\n\n{error}\n\nThe application will now exit.' ).format( error = str( e ) )
        inputbox(
            title = _( 'Application Error' ),
            message = message,
            buttons=[ 'OK' ]
        )
        logging.error( str( e ) )
        sys.exit( 1 )


if __name__ == "__main__":
    main()
