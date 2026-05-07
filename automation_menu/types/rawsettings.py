"""
Define typed raw settings data loaded from and written to the settings file.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from typing import TypedDict

from automation_menu.types.keepassshortcut import KeePassShortcut


class RawSettings( TypedDict, total = False ):
    """ Typed dictionary describing the serialized settings file format."""

    current_language: str
    force_focus_post_execution: bool
    include_ss_in_error_mail: bool
    keepass_shortcut: KeePassShortcut
    minimize_on_running: bool
    on_top: bool
    send_mail_on_error: bool
    saved_sequences: list[ dict ]
    script_folders: list[ str ]
