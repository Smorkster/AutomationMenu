"""
Function decorators

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-12-11
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, Concatenate, ParamSpec, TypeVar

if TYPE_CHECKING:
    from automation_menu.ui.main_window import AutomationMenuWindow

from functools import wraps
from logging import Logger

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

    def deco( fn: Callable[ Concatenate[ Any, P ], R ] ) -> Callable[ Concatenate[ Any, P ], R ] | None:
        """ Decorator applied to a UI instance method

        Args:
            fn: A bound instance method acting as a UI event handler
        """

        @wraps( fn )
        def wrapper( self: Any, *args: P.args, **kwargs: P.kwargs ) -> R | None:
            """ Wrapped UI callback method

            Executes the original method and intercepts any raised exception,
            logging a structured error message instead of letting the exception
            propagate into the Tkinter mainloop
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
