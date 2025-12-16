"""
Collection of custom exceptions

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-12-11
"""

from typing import Any


class ScriptInfoError( ValueError ):
    def __init__( self, message: str, *args: Any ) -> None:
        """ Exception for error in script info block/docstring
        
        Args:
            message (str): Error message
        """

        self.message: str = message

        super( ScriptInfoError, self ).__init__( self.message, *args )