"""
Collecting enums used throughout the application

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-20
"""


from enum import Enum


class OutputStyleTags(Enum):
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

    STATE = 'state'
    AUTHOR = 'author'
    VERSION = 'version'
    SYNOPSIS = 'synopsis'
    DESCRIPTION = 'description'
    REQUIREDADGROUPS = 'required_ad_groups'
    ALLOWEDUSERS = 'allowed_users'
    DISABLEMINIMIZEONRUNNING = 'disable_minimize_on_running'
