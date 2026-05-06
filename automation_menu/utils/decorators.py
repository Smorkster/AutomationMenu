"""
Function decorators

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from functools import wraps
from logging import Logger
from typing import Any, Callable, Concatenate, ParamSpec, TypeVar

P = ParamSpec( 'P' )
R = TypeVar( 'R' )

def ui_guard_method( when_message: str | None = None ) -> Callable[ [ Callable[ Concatenate[ Any, P ], R ] ], Callable[ Concatenate[ Any, P ], R | None ],
]:
    """ Decorator for guarding UI callback instance methods

    Intended for methods on AutomationMenuWindow that are invoked
    directly from UI interactions (buttons, menus, shortcuts).

    Args:
        when_message (str | None): Contextual description of operation being performed
    """

    def deco( fn: Callable[ Concatenate[ Any, P ], R ] ) -> Callable[ Concatenate[ Any, P ], R | None ]:
        """ Decorator applied to a UI instance method

        Args:
            fn (Callable[ Concatenate[ Any, P ], R ]): A bound instance method acting as a UI event handler

        Returns:
            Callable[ Concatenate[ Any, P ], R | None ]: A wrapped UI callback that returns the original method result, or None if an exception is caught and logged.
        """

        @wraps( fn )
        def wrapper( self: Any, *args: P.args, **kwargs: P.kwargs ) -> R | None:
            """ Wrapped UI callback method

            Executes the original method and intercepts any raised exception,
            logging a structured error message instead of letting the exception
            propagate into the Tkinter mainloop

            Args:
                self (Any): Instance owning the decorated UI callback, expected to expose app_context.debug_logger.
                *args (P.args): Positional arguments passed through to the wrapped method.
                **kwargs (P.kwargs): Keyword arguments passed through to the wrapped method.

            Returns:
                R | None: The wrapped method's return value, or None if an exception is caught and logged.
            """

            log: Logger = self.app_context.debug_logger

            try:

                return fn( self, *args, **kwargs )

            except Exception as e:
                msg: str = f'UI callback crashed: { fn.__qualname__ }\n'

                if when_message:
                    msg += f'Error occured when: { when_message }\n'

                msg += f'Error message:\n\n{ e }'

                log.error( msg )

                return None

        return wrapper

    return deco
