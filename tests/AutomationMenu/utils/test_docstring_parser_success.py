from automation_menu.models.enums import ScriptState
from automation_menu.models.scriptinputparameter import ScriptInputParameter
from automation_menu.utils.docstring_parser import docstring_parser


def test_docstring_parser_emtpy_docstring() -> None:
    """ Returns empty results for an empty docstring. """

    parsed, warnings = docstring_parser( '' )

    assert parsed == {}
    assert warnings == {}


def test_docstring_parser_description_only() -> None:
    """ Testing for only script description """

    parsed, warnings = docstring_parser( 'My script description' )

    assert parsed[ 'description' ] == 'My script description'
    assert parsed[ 'script_input_parameters' ] == []
    assert warnings == { 'keys': [],
                        'values': [],
                        'other': [] }


def test_docstring_parser_test_base_info() -> None:
    """ Testing ordinary base info """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster) """ )

    assert parsed[ 'synopsis' ] == 'Test info'
    assert parsed[ 'state' ] == ScriptState.PROD
    assert parsed[ 'author' ] == 'Smorkster (smorkster)'
    assert warnings == { 'keys': [],
                        'values': [],
                        'other': [] }


def test_docstring_parser_test_for_parameter_old_format() -> None:
    """ Will a parameter in the new format be identified """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param App: Some app name """ )

    test_obj =  parsed[ 'script_input_parameters' ][ 0 ]

    assert isinstance( test_obj, ScriptInputParameter )
    assert hasattr( test_obj, 'name' )
    assert test_obj.description == 'Some app name'


def test_docstring_parser_test_for_required_parameter_new_format() -> None:
    """ Will a parameter with setting 'required' be identified """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param App: description = Some app name : required """ )

    test_obj = parsed[ 'script_input_parameters' ][ 0 ]

    assert isinstance( test_obj, ScriptInputParameter )
    assert hasattr( test_obj, 'required' )
    assert test_obj.required == True


def test_docstring_parser_test_for_parameter_with_alternatives_new_format() -> None:
    """ Will a parameter with alternatives be identified """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param o: description = Test o : options = A | B  huhi ii | jiojoi""" )

    test_obj = parsed[ 'script_input_parameters' ][ 0 ]

    assert isinstance( test_obj, ScriptInputParameter )
    assert hasattr( test_obj, 'alternatives' )
    assert test_obj.alternatives and len( test_obj.alternatives ) == 3


def test_docstring_parser_test_for_parameter_with_type_float_new_format() -> None:
    """ Will a parameter with type 'float' be identified """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param ooo: description = Test ooo : type = float""" )

    test_obj = parsed[ 'script_input_parameters' ][ 0 ]

    assert isinstance( test_obj, ScriptInputParameter )
    assert hasattr( test_obj, 'type' )
    assert test_obj.type == 'float'


def test_docstring_parser_test_for_parameter_with_type_int_new_format() -> None:
    """ Will a parameter with type 'int' be identified """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param ooo: description = Test ooo : type = int""" )

    test_obj = parsed[ 'script_input_parameters' ][ 0 ]

    assert isinstance( test_obj, ScriptInputParameter )
    assert hasattr( test_obj, 'type' )
    assert test_obj.type == 'int'


def test_docstring_parser_test_for_parameter_with_type_bool_new_format() -> None:
    """ Will a parameter with type 'bool' be identified """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param boooool: description = Test boooool : type = bool : default = False""" )

    test_obj = parsed[ 'script_input_parameters' ][ 0 ]

    assert isinstance( test_obj, ScriptInputParameter )
    assert hasattr( test_obj, 'type' )
    assert test_obj.type == 'bool'


def test_docstring_parser_misspelled_synopsis() -> None:
    """ Test for misspelled 'synopsis' """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:ssynopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param App: Some app name """ )

    assert 'ssynopsis' in warnings[ 'keys' ]


def test_docstring_parser_misspelled_author() -> None:
    """ Test for misspelled 'author' """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:aauthor: Smorkster (smorkster)
:param App: Some app name """ )

    assert 'aauthor' in warnings[ 'keys' ]


def test_docstring_parser_data_sctructure_not_specified_for_metadata() -> None:
    """ Test for not approved field name """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:foo: bar""" )

    assert 'foo' in warnings[ 'keys' ]


def test_docstring_parser_base_info_without_description() -> None:
    """ Test for missing description """

    parsed, warnings = docstring_parser( """:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)""" )

    assert parsed[ 'description' ] == ''
    assert parsed[ 'synopsis' ] == 'Test info'
    assert parsed[ 'state' ] == ScriptState.PROD
    assert parsed[ 'author' ] == 'Smorkster (smorkster)'


def test_docstring_parser_invalid_state() -> None:
    """ Test for invalid state string  """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Validate
:author: Smorkster (smorkster)""" )

    assert 'Validate' in warnings[ 'values' ]


def test_docstring_parser_verify_parameter_values() -> None:
    """ Parses a parameter name, description, and default value. """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Param
:author: Smorkster (smorkster)
:param Param : description = Test desc : default = Something""" )

    test_param = parsed[ 'script_input_parameters' ][ 0 ]

    assert isinstance( test_param, ScriptInputParameter )
    assert test_param.name == 'Param'
    assert test_param.description == 'Test desc'
    assert test_param.default == 'Something'


def test_docstring_parser_verify_int_parameter_default() -> None:
    """ Preserves a valid integer parameter default. """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param Param : description = Test desc : type = int : default = 12""" )

    test_param = parsed[ 'script_input_parameters' ][ 0 ]

    assert isinstance( test_param, ScriptInputParameter )
    assert test_param.name == 'Param'
    assert isinstance( test_param.default, str )
    assert test_param.default == '12'


def test_docstring_parser_verify_int_parameter_default_invalid_format() -> None:
    """ Replaces an invalid integer default and records a warning. """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param Param : description = Test desc : type = int : default = Test""" )

    test_param = parsed[ 'script_input_parameters' ][ 0 ]

    assert isinstance( test_param, ScriptInputParameter )
    assert isinstance( test_param.default, str )
    assert test_param.default == '0'
    assert 'Param has invalid integer default value: ''Test''' in warnings[ 'values' ]


def test_docstring_parser_verify_int_parameter_default_not_present() -> None:
    """ Uses zero as the default for an integer parameter without one. """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param Param : description = Test desc : type = int""" )

    test_param: ScriptInputParameter = parsed[ 'script_input_parameters' ][ 0 ]

    assert test_param.default == '0'


def test_docstring_parser_verify_float_parameter_default_invalid_format() -> None:
    """ Replaces an invalid float default and records a warning. """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param Param : description = Test desc : type = float : default = Test""" )

    test_param = parsed[ 'script_input_parameters' ][ 0 ]

    assert isinstance( test_param, ScriptInputParameter )
    assert isinstance( test_param.default, str )
    assert test_param.default == '0.0'
    assert 'Param has invalid float default value: Test' in warnings[ 'values' ]


def test_docstring_parser_verify_float_parameter_default_not_present() -> None:
    """ Uses zero point zero as the default for a float parameter without one. """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param Param : description = Test desc : type = float""" )

    test_param: ScriptInputParameter = parsed[ 'script_input_parameters' ][ 0 ]

    assert test_param.default == '0.0'


def test_docstring_parser_verify_bool_parameter_default_not_present() -> None:
    """ Uses False as the default for a boolean parameter without one. """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param Param : description = Test desc : type = bool""" )

    test_param: ScriptInputParameter = parsed[ 'script_input_parameters' ][ 0 ]

    assert test_param.default == 'False'


def test_docstring_parser_verify_bool_parameter_invalid_default() -> None:
    """ Replaces an invalid boolean default and records a warning. """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param Param : description = Test desc : type = bool : default = Test""" )

    test_param: ScriptInputParameter = parsed[ 'script_input_parameters' ][ 0 ]

    assert test_param.default == 'False'
    assert 'Param has invalid boolean default value: Test'


def test_docstring_parser_verify_alternatives_count() -> None:
    """ Parses every supplied parameter alternative. """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param Param : description = Test desc : options = int | float""" )

    test_param: ScriptInputParameter = parsed[ 'script_input_parameters' ][ 0 ]

    assert isinstance( test_param, ScriptInputParameter )
    assert hasattr( test_param, 'alternatives' )
    assert test_param.alternatives is not None
    assert len( test_param.alternatives ) == 2


def test_docstring_parser_verify_alternatives_default_in_options() -> None:
    """ Keeps a parameter default when it is one of the alternatives. """

    parsed, warnings = docstring_parser( """ Script description running
over more than one line

:synopsis: Test info
:state: Prod
:author: Smorkster (smorkster)
:param Param : default = int : description = Test desc : options = int | float""" )

    test_param: ScriptInputParameter = parsed[ 'script_input_parameters' ][ 0 ]

    assert isinstance( test_param, ScriptInputParameter )
    assert hasattr( test_param, 'alternatives' )
    assert test_param.alternatives is not None
    assert test_param.default == 'int'
    assert test_param.default in test_param.alternatives
