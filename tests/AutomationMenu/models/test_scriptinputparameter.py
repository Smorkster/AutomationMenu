"""
Test cases for ScriptInputParameter

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from automation_menu.models.scriptinputparameter import ScriptInputParameter


class TestCreation:

    def test_create( self ) -> None:
        """ Test creation of one ScriptInputParameter """

        alts: list[ str ] = [ 'a' ]
        default: str = 'def'
        desc: str = 'desc'
        name: str = 'n'
        req: bool = True
        type: str = 'str'

        sip: ScriptInputParameter = ScriptInputParameter( alternatives = alts,
                                                         default = default,
                                                         description = desc,
                                                         name = name,
                                                         required = req,
                                                         type = type )

        assert sip.alternatives == alts
        assert sip.default == default
        assert sip.description == desc
        assert sip.name == name
        assert sip.required == req
        assert sip.type == type


    def test_from_dict( self ) -> None:
        """ Test create from a dict """

        alts: list[ str ] = [ 'a' ]
        default: str = 'def'
        desc: str = 'desc'
        name: str = 'n'
        req: bool = True
        type: str = 'str'

        sip: ScriptInputParameter = ScriptInputParameter().from_dict( { 'alternatives': alts,
                                                                       'default': default,
                                                                       'description': desc,
                                                                       'name': name,
                                                                       'required': req,
                                                                       'type': type } )

        assert sip.alternatives == alts
        assert sip.default == default
        assert sip.description == desc
        assert sip.name == name
        assert sip.required == req
        assert sip.type == type


class TestUse:

    def test_convert_to_dict( self ) -> None:
        """ Are values preserved after conversion """

        alts: list[ str ] = [ 'a' ]
        default: str = 'def'
        desc: str = 'desc'
        name: str = 'n'
        req: bool = True
        type: str = 'str'

        sip: ScriptInputParameter = ScriptInputParameter( alternatives = alts,
                                                         default = default,
                                                         description = desc,
                                                         name = name,
                                                         required = req,
                                                         type = type )

        d: dict = sip.to_dict()

        assert d[ 'alternatives' ] == alts
        assert d[ 'default' ] == default
        assert d[ 'description' ] == desc
        assert d[ 'name' ] == name
        assert d[ 'required' ] == req
        assert d[ 'type' ] == type
