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

import sys

from pathlib import Path, WindowsPath
from typing import Callable

from automation_menu.models.startup_arguments import StartupArguments
from automation_menu.services.error_manager import ErrorManager

# Add the project root to Python path if needed
project_root = Path( __file__ ).parent.parent
sys.path.insert( 0, str( project_root ) )

import argparse
import logging

from logging import Formatter, Logger, StreamHandler

from automation_menu.core.app_context import ApplicationContext
from automation_menu.core.script_execution_manager import ScriptExecutionManager
from automation_menu.filehandling.exec_history_handler import write_exec_history
from automation_menu.filehandling.secrets_handler import read_secrets_file
from automation_menu.filehandling.settings_handler import read_settingsfile, write_settingsfile
from automation_menu.models import Secrets, Settings, User
from automation_menu.models.enums import ApplicationRunState
from automation_menu.models.application_state import ApplicationState
from automation_menu.ui.history_manager import HistoryManager
from automation_menu.ui.sequence_manager import SequenceManager
from automation_menu.utils.language_manager import LanguageManager
from automation_menu.utils.localization import change_language
from automation_menu.utils.logging_utils import JsonFileHandler
from automation_menu.utils.script_manager import ScriptManager


def setup_logger( level: str = 'DEBUG' ) -> Logger:
    """ Create a logger with set logging level
    Defaults to DEBUG

    Args:
        level (str): Logging level to use for the setup

    Returns:
        logger (logging.Logger): General purpose logging object
    """

    logger: Logger = logging.getLogger( 'debug_logger' )
    level_id: int = logging._nameToLevel.get( level.upper(), logging.INFO )
    logger.setLevel( level = level_id )
    logger.propagate = False

    if not logger.handlers:
        # General purpose logging to terminal
        handler: StreamHandler = StreamHandler()

        formater: Formatter = Formatter(
            "[%(levelname)s] %(filename)s:%(lineno)d - %(message)s"
        )

        handler.setFormatter( formater )
        logger.addHandler( handler )

        # Logging errors to file
        project_root: Path = Path( __file__ ).resolve().parent
        json_handler: JsonFileHandler = JsonFileHandler( project_root )
        logger.addHandler( json_handler )

    return logger


def main() -> None:
    """ Main entry point """

    def save_settings( obj: Settings ) -> None:
        """ Callback function to save settings to file

        Args:
            obj (Settings): Settings object to save
        """

        write_settingsfile( settings = obj, settings_file_path = app_state.secrets[ 'settings_file_path' ] )

    from automation_menu.utils.localization import _ as _

    input_parser = argparse.ArgumentParser()
    input_parser.add_argument( '--application_state', action = 'store', choices = [ 'dev', 'test', 'prod' ], default = 'prod' )
    input_parser.add_argument( '--loglevel', action = 'store' )

    input_args = input_parser.parse_args()

    try:

        startup_arguments: StartupArguments = {
            'app_run_state': ApplicationRunState[ input_args.application_state.upper() ],
            'loglevel': input_args.loglevel
        }

        debug_logger = setup_logger( level = startup_arguments[ 'loglevel' ] )
        secrets = Secrets( read_secrets_file( file_path = str( Path( __file__ ).resolve().parent / 'secrets.json' ) ) )
        read_settings: dict = read_settingsfile( settings_file_path = secrets[ 'settings_file_path' ], debug_logger = debug_logger )
        settings = Settings( settings_dict = read_settings, save_callback = save_settings )

        from automation_menu.core.auth import connect_to_AD, get_user_adobject
        ldap_connection = connect_to_AD( ldap_server = secrets[ 'ldap_server' ], domain_name = secrets[ 'domain_name' ] )
        current_user = User( get_user_adobject( ldap_search_base = secrets[ 'ldap_search_base' ], ldap_connection = ldap_connection ) )

        app_state = ApplicationState( current_user = current_user, secrets = secrets, settings = settings )
        app_context = ApplicationContext( debug_logger = debug_logger, startup_arguments = startup_arguments )

        debug_logger.debug( msg = f'sequence list loaded with "{ len( app_state.settings.saved_sequences ) }" sequences' )

        change_language( language_code = app_state.settings.current_language )
        app_context._language_manager = LanguageManager( current_language = app_state.settings.current_language )
        app_context._script_manager = ScriptManager( script_dir_path = secrets[ 'script_dir_path' ], current_user = current_user )
        app_context._script_manager.gather_scripts( output_queue = app_context.OutputQueue, app_state = app_state, app_run_state = startup_arguments[ 'app_run_state' ] )
        app_context._error_manager = ErrorManager( app_state = app_state, ldap_connection = ldap_connection )
        app_context._execution_manager = ScriptExecutionManager( output_queue = app_context.OutputQueue, app_state = app_state, error_manager = app_context.ErrorManager )
        app_context._sequence_manager = SequenceManager( app_context = app_context, app_state = app_state, saved_sequences = app_state.settings.saved_sequences )
        app_context._history_manager = HistoryManager( logger = app_context.debug_logger )

        # Launch the main application window
        from automation_menu.ui.main_window import AutomationMenuWindow

        AutomationMenuWindow( app_state = app_state, app_context = app_context )

        write_exec_history(
            exec_items = app_context.HistoryManager.get_history_list(),
            root_dir = WindowsPath( Path( __file__ ).resolve().parent ),
            logger = app_context.debug_logger
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
            buttons = [ 'OK' ]
        ).show()
        logging.error( str( e ) )
        sys.exit( 1 )


if __name__ == "__main__":
    main()
