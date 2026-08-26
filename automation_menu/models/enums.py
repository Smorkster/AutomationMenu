"""
Collecting enums used throughout the application

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from enum import Enum, StrEnum, auto


class ApplicationRunState( Enum ):
    """ Valid application run states """

    DEV = 'Dev'
    TEST = 'Test'
    PROD = 'Prod'


class ExecutionState( StrEnum ):
    """ Execution lifecycle states for one-time and persistent scripts. """

    CLOSED = auto()
    FORCED_STOPPING = auto()
    FORCED_STOPPING_FAILED = auto()
    IDLE = auto()
    PAUSED = auto()
    PAUSED_BY_SCRIPT = auto()
    RUNNING = auto()
    STARTING = auto()
    STOP_FAILED = auto()
    STOPPED = auto()
    STOPPING = auto()
    UNLAUNCHED = auto()


class OutputStyleTags( Enum ):
    """ Tags for output text styling """

    ERROR = 'suite_error'
    INFO = 'suite_info'
    SUCCESS = 'suite_success'
    WARNING = 'suite_warning'
    SYSERROR = 'suite_syserror'
    SYSINFO = 'suite_sysinfo'
    SYSWARNING = 'suite_syswarning'


class ScriptState( Enum ):
    """ Valid script states """

    DEV = 'Dev'
    TEST = 'Test'
    PROD = 'Prod'


class SysInstructions( Enum ):
    """ Statuses for application operations """

    CLEAROUTPUT = 'SI_ClearOutput'
    PROCESSTERMINATED = 'SI_ProcessTerminated'


class ValidScriptInfoFields ( Enum ):
    """ Valid names in ScriptInfo block/docstring """

    ALLOWEDUSERS = 'allowed_users'
    AUTHOR = 'author'
    DESCRIPTION = 'description'
    DISABLEMINIMIZEONRUNNING = 'disable_minimize_on_running'
    PERSISTENTGUI = 'persistent_gui'
    PERSISTENTGUIMULTIPLE = 'persistent_gui_multiple'
    REQUIREDADGROUPS = 'required_ad_groups'
    STATE = 'state'
    SYNOPSIS = 'synopsis'
    VERSION = 'version'
