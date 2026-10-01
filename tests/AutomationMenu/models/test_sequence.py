"""
Test cases for Sequence

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from pathlib import Path
from unittest.mock import patch
import uuid

import pytest

from automation_menu.models.sequence import Sequence
from automation_menu.models.sequencestep import SequenceStep

class TestCreation:

    def test_create_basic( self ) -> None:
        """ Test creating basic sequence """

        s: Sequence = Sequence()

        assert s.description == ''
        assert s.id == ''
        assert s.name == ''
        assert s.steps == []
        assert s.stop_on_error == False


    def test_create_full( self ) -> None:
        """ Test creating fully defined Sequence """

        desc: str = 'D'
        id: str = 'Id'
        name: str = 'Name'
        steps: list[ SequenceStep ] = [ SequenceStep() ]
        soe: bool = False

        s: Sequence = Sequence( description = desc,
                               id = id,
                               name = name,
                               steps = steps,
                               stop_on_error = soe )

        assert s.description == desc
        assert s.id == id
        assert s.name == name
        assert s.steps == steps
        assert s.stop_on_error == soe


    @pytest.mark.parametrize( 'data',
                             [ {},
                              { 'description': 'Desc', 'id': 'Id', 'name': 'Name', 'steps': [ { 'name': 'n' } ], 'stop_on_error': True },
                              'dict' ] )
    def test_create_from_dict( self, data: dict | str ) -> None:
        """ Test create from dictionary

        Args:
            data (dict|str): Definition of dict to create from
        """

        s: Sequence

        with patch( 'automation_menu.utils.localization._', side_effect = lambda t: t ):
            if isinstance( data, str ):
                with pytest.raises( TypeError ):
                    s = Sequence().from_dict( data ) # type: ignore

            else:
                s = Sequence().from_dict( data )

                assert s.description == data.get( 'description' ) if data.get( 'description' ) else '<Description not set>'

                if data.get( 'id' ):
                    assert s.id == data.get( 'id' )

                else:
                    assert str( uuid.UUID( str( s.id ) ) ) == str( s.id )

                assert s.name == data.get( 'name' ) if data.get( 'name' ) else 'Unnamed sequence'

                if data.get( 'steps' ):
                    st: SequenceStep = SequenceStep.from_dict( data.get( 'steps', [] )[ 0 ] )

                    assert s.steps[ 0 ].stop_on_error == st.stop_on_error
                    assert s.steps[ 0 ].step_index == st.step_index
                    assert str( uuid.UUID( str( s.steps[ 0 ].id ) ) ) == str( s.steps[ 0 ].id )

                else:
                    assert s.steps == []

                if 'stop_on_error' in data.keys():
                    assert s.stop_on_error == data.get( 'stop_on_error' )

                else:
                    assert s.stop_on_error == False


    def test_create_from_sequence( self ) -> None:
        """ Test creation from another Sequence """

        s1: Sequence = Sequence( description = 'D',
                                id = 'Id',
                                name = 'Name' )

        s2: Sequence = Sequence.from_sequence( s1 )

        assert s1.description == s2.description
        assert s1.id == s2.id
        assert s1.name == s2.name


class TestUse:

    @pytest.mark.parametrize( 'steps', [ [], [ SequenceStep( step_index = 0 )] ] )
    def test_to_dict( self, steps: list[ SequenceStep ] ) -> None:
        """ Test turning Sequence to dict

        Args:
            steps (list[ SequenceStep ]): Defined list of SequenceStep's
        """

        s: Sequence = Sequence( description = 'D',
                                id = 'Id',
                                name = 'Name',
                                steps = steps )

        for step in s.steps:
            step.script_file = Path( 'test' )

        d: dict = s.to_dict()

        assert d[ 'name' ] == s.name
        assert d[ 'id' ] == s.id
        assert d[ 'description' ] == s.description
        assert d[ 'stop_on_error' ] == s.stop_on_error
        assert len( d[ 'steps' ] ) == len( s.steps )