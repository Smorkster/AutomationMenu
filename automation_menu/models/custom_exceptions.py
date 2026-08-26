"""
Collection of custom exceptions

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from typing import Any


class ScriptInfoError( ValueError ):
    """ Raised when script metadata cannot be parsed or validated. """

    def __init__( self, message: str, *args: Any ) -> None:
        """ Exception for error in script info block/docstring

        Args:
            message (str): Error message
        """

        self.message: str = message

        super( ScriptInfoError, self ).__init__( self.message, *args )


class MissingDocstringError( ValueError ):
    """ Raised when a script is missing its required metadata docstring. """

    def __init__( self, message: str, *args: Any ) -> None:
        """ Exception for missing Python style docstring in file

        Args:
            message (str): Error message
        """

        self.message: str = message

        super( MissingDocstringError, self ).__init__( self.message, *args )
