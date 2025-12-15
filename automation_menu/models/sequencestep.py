"""
Definition of a step for an automatic sequence

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0.0
Created: 2025-11-20
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from automation_menu.models.scriptinfo import ScriptInfo


@dataclass
class SequenceStep:
    """ Definition of a sequence step """

    pre_set_parameters: Dict[ str, str ] = field( default_factory = Dict[ str, str ] )
    script_file: str = None
    script_info: ScriptInfo = None
    step_index: int = None
    stop_on_error: bool = False


    def to_dict( self ) -> dict:
        """ Return step as JSON (dict)

        Returns:
            (dict): Sequence step as a dict
        """

        from automation_menu.utils.localization import _

        parameters: list[ dict ] = []

        if self.pre_set_parameters:
            for i, param in enumerate( self.pre_set_parameters ):
                if not isinstance( param, dict ) or 'name' not in param or 'set' not in param:

                    raise ValueError( _( 'Invalid pre_set_parameters for step {f}: {p}' ).format( f = self.script_file, p = param ) )

                parameters.append( {
                    'name': param[ 'name' ],
                    'set': param[ 'set' ]
                } )

        return {
            'script_file': self.script_file,
            'stop_on_error': self.stop_on_error,
            'step_index': self.step_index,
            'pre_set_parameters': parameters
        }