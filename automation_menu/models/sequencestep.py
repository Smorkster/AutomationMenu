"""
Definition of a step for an automatic sequence

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import uuid

from automation_menu.models.presetparam import PreSetParam
from automation_menu.models.scriptinfo import ScriptInfo


@dataclass
class SequenceStep:
    """ Definition of a sequence step """

    _script_info: ScriptInfo | None = None
    _script_file: Path | None = None
    _pre_set_parameters: list[ PreSetParam ] = field( default_factory = list )
    step_index: int = 0
    stop_on_error: bool = False
    id: str = field( default_factory = lambda: str( uuid.uuid4() ) )


    @property
    def pre_set_parameters( self ) -> list[ PreSetParam ]:
        """ Get the parameters for this step

        Returns:
            list[ PreSetParam ]: List of parameters for running the script
        """

        return self._pre_set_parameters


    @pre_set_parameters.setter
    def pre_set_parameters( self, value: list[ PreSetParam ] ) -> None:
        """ Set parameter list for the script

        Args:
            value (list[ PreSetParam ]): List of parameters
        """

        self._pre_set_parameters = value


    @property
    def script_file( self ) -> Path:
        """ Get the script associated with this step

        Returns:
            Path: Path to the script file

        Raises:
            ValuError: If the script file is not set
        """

        if self._script_file == None:

            raise ValueError( 'Script file is not set' )

        return self._script_file


    @script_file.setter
    def script_file( self, value: Path ) -> None:
        """ Set script file path

        Args:
            value (Path): Path to the script file
        """

        self._script_file = value


    @property
    def script_info( self ) -> ScriptInfo:
        """ Get script info for the associated script

        Returns:
            (ScriptInfo): Info parsed from the file

        Raises:
            ValueError: If the script info is not set
        """

        if self._script_info == None:

            raise ValueError( 'Script info is not set' )

        return self._script_info


    @script_info.setter
    def script_info( self, value: ScriptInfo ) -> None:
        """ Set the script info

        Args:
            value (ScriptInfo): ScriptInfo parsed from the script file
        """

        self._script_info = value


    @classmethod
    def from_dict( cls: type[ SequenceStep ], data: dict ) -> SequenceStep:
        """ Create a sequence step from a dict

        Args:
            cls (type[ SequenceStep ]): Current sequence step
            data (dict): Dict to transform to a step

        Raises:
            TypeError: If value argument is of type other than dict
        """

        if not isinstance( data, dict ):
            from automation_menu.utils.localization import _

            raise TypeError( _( 'Expected dict, got {t}').format( t = type( data ) ) )

        return cls(
            _script_file = data.get( 'script_file' ),
            _pre_set_parameters = [
                PreSetParam.from_dict( psp )
                for psp in data.get( 'pre_set_parameters', [] )
            ],
            _script_info = None,
            step_index = data.get( 'step_index', 0 ),
            stop_on_error = data.get( 'stop_on_error', False ),
            id = data.get( 'id', str( uuid.uuid4() ) )
        )


    @classmethod
    def from_step( cls: type[ SequenceStep ], step: SequenceStep ) -> SequenceStep:
        """ Create a sequence step from another sequence step.

        Args:
            cls (type[SequenceStep]): Current sequence step class.
            step (SequenceStep): Sequence step to copy.

        Returns:
            SequenceStep: New sequence step with copied values.
        """

        return cls(
            _script_info = step.script_info,
            _script_file = step.script_file,
            _pre_set_parameters = [ PreSetParam().from_psp( psp ) for psp in step.pre_set_parameters ],
            step_index = step.step_index,
            stop_on_error = step.stop_on_error,
            id = step.id
        )


    def to_dict( self ) -> dict:
        """ Return step as JSON (dict)

        Returns:
            (dict): Sequence step as a dict
        """

        from automation_menu.utils.localization import _

        parameters: list[ dict[ str, str ] ] = []

        if self.pre_set_parameters:
            for param in self.pre_set_parameters:
                if not isinstance( param, PreSetParam ):

                    raise ValueError( _( 'Invalid pre_set_parameters for step {f}: {p}' ).format( f = self.script_file, p = param ) )

                new_param: dict[ str, str ] = {
                    'name': param.name,
                    'set': param.set
                }
                parameters.append( new_param )

        return {
            'script_file': self.script_file,
            'stop_on_error': self.stop_on_error,
            'step_index': self.step_index,
            'pre_set_parameters': parameters,
            'id': self.id
        }
