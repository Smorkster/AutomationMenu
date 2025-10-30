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

import logging
import sys

from pathlib import Path

# Add the project root to Python path if needed
project_root = Path( __file__ ).parent.parent
sys.path.insert( 0, str( project_root ) )

from automation_menu.core.execution_manager import ScriptExecutionManager
from automation_menu.core.application_state import ApplicationState
from automation_menu.filehandling.exec_history_handler import write_exec_history
from automation_menu.filehandling.secrets_handler import read_secrets_file
from automation_menu.models import Secrets, Settings, User
from automation_menu.ui.history_manager import HistoryManager
from automation_menu.filehandling.settings_handler import read_settingsfile, write_settingsfile
from automation_menu.utils.localization import change_language


def main():
    """ Main entry point """

    def save_settings( obj ):
        write_settingsfile( settings = obj, settings_file_path = app_state.secrets.get( 'settings_file_path' ) )

    try:
        app_state = ApplicationState()
        app_state.history_manager = HistoryManager()
        app_state.secrets = Secrets( read_secrets_file( file_path = Path( __file__ ).resolve().parent / 'secrets.json' ) )
        app_state.settings = Settings( settings_dict = read_settingsfile( app_state.secrets.get( 'settings_file_path' ) ), save_callback = save_settings )

        change_language( language_code = app_state.settings.current_language )

        from automation_menu.core.auth import connect_to_AD, get_user_adobject
        app_state.ldap_connection = connect_to_AD( app_state )
        app_state.current_user = User( get_user_adobject( app_state = app_state ) )

        app_state.script_manager = ScriptExecutionManager( output_queue = app_state.output_queue, app_state = app_state )

        # Launch the main application window
        from automation_menu.ui.main_window import AutomationMenuWindow
        from automation_menu.utils.localization import _
        AutomationMenuWindow( app_state )

        write_exec_history(
            exec_items = app_state.history_manager.get_history_list(),
            root_dir = Path( __file__ ).resolve().parent
        )

    except KeyboardInterrupt:
        print( _( 'Application interrupted by user' ) )
        sys.exit( 0 )

    except SystemExit:
        raise

    except Exception as e:
        from dynamicinputbox import dynamic_inputbox as inputbox

        # Handle any unexpected errors
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
