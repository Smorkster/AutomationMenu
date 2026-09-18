"""
Test cases for ScriptMetadata

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from unittest.mock import Mock, patch

import pytest

from automation_menu.models.enums import ScriptState
from automation_menu.models.scriptinputparameter import ScriptInputParameter
from automation_menu.models.scriptmetadata import ScriptMetadata


class TestCreation:

    def test_create_basic( self ) -> None:
        """ Test creation of one basic ScriptMetadata collection """

        au: str = 'Au'
        syn: str = 'Syn'

        smd: ScriptMetadata = ScriptMetadata( author = au,
                                             synopsis = syn )

        assert smd.author == au
        assert smd.synopsis == syn


    def test_create_full( self ) -> None:
        """ Test creation of a full ScriptMetadata collection """

        au: str = 'Au'
        syn: str = 'Syn'
        desc: str = 'Desc'
        state: ScriptState = ScriptState.PROD
        ver: str = '1'
        req_grps: list[ str ] = [ 'Grp_1' ]
        all_usr: list[ str ] = [ 'Usr1' ]
        inp: list[ ScriptInputParameter ] = [ ScriptInputParameter( name = 'n', ) ]
        per: bool = True

        smd: ScriptMetadata = ScriptMetadata( author = au,
                                             synopsis = syn,
                                             description = desc,
                                             state = state,
                                             version = ver,
                                             required_ad_groups = req_grps,
                                             allowed_users = all_usr,
                                             script_input_parameters = inp,
                                             persistent_gui = per )

        assert smd.author == au
        assert smd.synopsis == syn
        assert smd.description == desc
        assert smd.state == state
        assert smd.version == ver
        assert smd.required_ad_groups == req_grps
        assert smd.allowed_users == all_usr
        assert smd.script_input_parameters == inp
        assert smd.persistent_gui == per


    @pytest.mark.parametrize( 'state', [ 'Prod', 'Pord' ] )
    def test_basic_from_dict( self, state: str ) -> None:
        """ Test create from a dict

        Args:
            state (str): Definition for state to test
        """

        au: str = 'Au'
        syn: str = 'Syn'

        smd: ScriptMetadata = ScriptMetadata.from_dict( { 'author': au,
                                                         'synopsis': syn,
                                                         'state': state } )

        assert smd.author == au
        assert smd.synopsis == syn
        assert smd.state == ScriptState.PROD


    def test_create_full_from_dict( self ) -> None:
        """ Test creation of a full ScriptMetadata collection from a dict """

        au: str = 'Au'
        syn: str = 'Syn'
        desc: str = 'Desc'
        state: str = 'Prod'
        ver: str = '1'
        req_grps: list[ str ] = [ 'Grp_1' ]
        all_usr: list[ str ] = [ 'Usr1' ]
        sip: dict = { 'name': 'n' }
        inp: list[ dict ] = [ sip ]
        per: bool = True

        smd: ScriptMetadata = ScriptMetadata.from_dict( { 'author': au,
                                                         'synopsis': syn,
                                                         'description': desc,
                                                         'state': state,
                                                         'version': ver,
                                                         'required_ad_groups': req_grps,
                                                         'allowed_users': all_usr,
                                                         'script_input_parameters': inp,
                                                         'persistent_gui': per } )

        assert smd.author == au
        assert smd.synopsis == syn
        assert smd.description == desc
        assert smd.state.value == state
        assert smd.version == ver
        assert smd.required_ad_groups == req_grps
        assert smd.allowed_users == all_usr
        assert smd.script_input_parameters[ 0 ].name == inp[ 0 ][ 'name' ]
        assert smd.persistent_gui == per


    def test_post_init_runs_after_creation( self ) -> None:
        """ Test that __post_init__ runs after creation """

        with pytest.raises( ValueError, match = 'Author is required' ):
            ScriptMetadata( synopsis = 'S', author = '' )

        with pytest.raises( ValueError, match = 'Synopsis is required' ):
            ScriptMetadata( synopsis = '', author = 'A' )

        with pytest.raises( ValueError, match = 'persistent_gui and persistent_gui_multiple can''t be used at the same time' ):
            ScriptMetadata( synopsis = 'S', author = 'A', persistent_gui = True, persistent_gui_multiple = True )


    def test_post_init_runs_after_creation_from_dict( self ) -> None:
        """ Test that __post_init__ runs after creation """

        with pytest.raises( ValueError, match = 'Author is required' ):
            ScriptMetadata.from_dict( { 'synopsis': 'S', 'author': '' } )

        with pytest.raises( ValueError, match = 'Synopsis is required' ):
            ScriptMetadata.from_dict( { 'synopsis': '', 'author': 'A' } )

        with pytest.raises( ValueError, match = 'persistent_gui and persistent_gui_multiple can''t be used at the same time' ):
            ScriptMetadata.from_dict( { 'synopsis': 'S', 'author': 'A', 'persistent_gui': True, 'persistent_gui_multiple': True } )


class TestUse:

    def test_convert_to_dict( self ) -> None:
        """ Are values preserved after conversion """

        au: str = 'Au'
        syn: str = 'Syn'
        desc: str = 'Desc'
        state: ScriptState = ScriptState.PROD
        ver: str = '1'
        req_grps: list[ str ] = [ 'Grp_1' ]
        all_usr: list[ str ] = [ 'Usr1' ]
        inp: list[ ScriptInputParameter ] = [ ScriptInputParameter( name = 'n', ) ]
        per: bool = True

        smd: ScriptMetadata = ScriptMetadata( author = au,
                                             synopsis = syn,
                                             description = desc,
                                             state = state,
                                             version = ver,
                                             required_ad_groups = req_grps,
                                             allowed_users = all_usr,
                                             script_input_parameters = inp,
                                             persistent_gui = per )

        d: dict = smd.to_dict()

        assert d[ 'author' ] == au
        assert d[ 'synopsis' ] == syn
        assert d[ 'description' ] == desc
        assert d[ 'state' ] == state.value
        assert d[ 'version' ] == ver
        assert d[ 'required_ad_groups' ] == req_grps
        assert d[ 'allowed_users' ] == all_usr
        assert d[ 'script_input_parameters' ] == [ i.to_dict() for i in inp ]
        assert d[ 'persistent_gui' ] == per


    @pytest.mark.parametrize( ( 'grps', 'usrs' ),
                               [ pytest.param( [], [] ),
                                pytest.param( [ 'Grp1' ], [] ),
                                pytest.param( [], [ 'Usr1' ] ),
                                pytest.param( [ 'Grp1' ], [ 'Usr1' ] ) ] )
    def test_requires_permission_check( self, grps: list[ str ], usrs: list[ str ] ) -> None:
        """ Test if requires_permission_check reports correctly
        
        Args:
            grps (list[ str ]): List of required groups
            usrs (list[ str ]): List of allowed users
        """

        smd: ScriptMetadata = ScriptMetadata( author = 'A',
                                             synopsis = 'S',
                                             required_ad_groups = grps,
                                             allowed_users = usrs )

        if not grps and not usrs:
            assert smd.requires_permission_check() == False

        else:
            assert smd.requires_permission_check() == True


    @pytest.mark.parametrize( 'inp', [ [], [ ScriptInputParameter( name = 'n' ) ] ] )
    def test_check_for_has_input_parameters( self, inp: list[ ScriptInputParameter ] ) -> None:
        """ Test for checking if input parameters are registered

        Args:
            inp (list[ ScriptInputParameter ]): Definition of ScriptInputParameter list
        """

        smd: ScriptMetadata = ScriptMetadata( author = 'A',
                                             synopsis = 'S',
                                             script_input_parameters = inp )

        if inp:
            assert smd.has_input_parameters()

        else:
            assert not smd.has_input_parameters()