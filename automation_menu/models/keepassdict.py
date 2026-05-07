"""
Define the typed dictionary used for KeePass shortcut configuration.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from typing import TypedDict


class KeePassDict( TypedDict ):
    """ Typed dictionary describing a KeePass keyboard shortcut.

    Attributes:
        alt: Whether the Alt modifier is included.
        ctrl: Whether the Ctrl modifier is included.
        shift: Whether the Shift modifier is included.
        key: Non-modifier key used in the shortcut.
    """

    alt: bool
    ctrl: bool
    shift: bool
    key: str
