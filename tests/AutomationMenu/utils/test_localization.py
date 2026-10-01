"""
Test cases for localization

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pytest import CaptureFixture, MonkeyPatch

from automation_menu.utils import localization
from automation_menu.utils.localization import change_language, find_locales_directory, get_available_languages, get_system_locale, setup_localization, translate


@pytest.fixture
def module() -> str:
    """ Module import path

    Returns:
        (str): Returns module import path
    """

    return 'automation_menu.utils.localization'


@pytest.fixture( autouse = True )
def restore_translator( monkeypatch: MonkeyPatch ) -> None:
    """ Restore the original translator after tests that replace module-level _.

    Args:
        monkeypatch (MonkeyPatch): Patch mechanism
    """

    monkeypatch.setattr( localization, '_', localization._ )


class TestChangeLanguage:

    def test_change_language_calls_setup_with_requested_language( self, module: str ) -> None:
        """ Pass the supplied language code to setup_localization.

        Args:
            module (str): Fixture for module import path
        """

        input: str = 'sv'

        with patch( f'{ module }.setup_localization' ) as setup:
            change_language( input )

            setup.assert_called_once_with( language = input )


class TestFindLocalesDirectory:

    def test_returns_existing_locales_directory( self, module: str, tmp_path: Path ) -> None:
        """ Return app_path()/locales without attempting to recreate it.

        Args:
            module (str): Fixture for module import path
            tmp_path (Path): Temporary directory
        """

        ( tmp_path / 'locales' ).mkdir()

        with patch( f'{ module }.app_path', return_value = tmp_path ) as app_path:
            locales_path = find_locales_directory()

            app_path.assert_called_once_with()
            assert locales_path == tmp_path / 'locales'


    def test_creates_missing_locales_directory( self, module: str, tmp_path: Path ) -> None:
        """ Create and return the locales directory when it does not exist.

        Args:
            module (str): Fixture for module import path
            tmp_path (Path): Temporary directory
        """

        expected_path = tmp_path / 'locales'
        assert not expected_path.exists()

        with patch( f'{ module }.app_path', return_value = tmp_path ) as app_path:
            locales_path = find_locales_directory()

        app_path.assert_called_once_with()
        assert locales_path == expected_path
        assert locales_path.is_dir()


class TestAvailableLanguages:

    def test_returns_languages_with_compiled_catalogs_in_sorted_order( self, module: str, tmp_path: Path ) -> None:
        """ Include directories containing LC_MESSAGES/messages.mo, sorted by name.

        Args:
            module (str): Fixture for module import path
            tmp_path (Path): Temporary directory
        """

        locale_dir = Mock( spec = Path )
        locale_dir.iterdir.return_value = iter( [ tmp_path / 'sv',
                                                 tmp_path / 'en' ] )

        ( tmp_path / 'sv' / 'LC_MESSAGES' ).mkdir( parents = True )
        ( tmp_path / 'sv' / 'LC_MESSAGES' / 'messages.mo' ).touch( exist_ok = True )
        ( tmp_path / 'en' / 'LC_MESSAGES' ).mkdir( parents = True )
        ( tmp_path / 'en' / 'LC_MESSAGES' / 'messages.mo' ).touch( exist_ok = True )

        with patch( f'{ module }.find_locales_directory', return_value = locale_dir ):
            lang_list = get_available_languages()

            locale_dir.iterdir.assert_called_once_with()
            assert len( lang_list ) == 2
            assert lang_list == [ 'en', 'sv' ]


    def test_ignores_files_and_directories_without_compiled_catalogs( self, module: str, tmp_path: Path ) -> None:
        """ Exclude ordinary files, incomplete directories, and .po-only languages.

        Args:
            module (str): Fixture for module import path
            tmp_path (Path): Temporary directory
        """

        ( tmp_path / 'sv' / 'LC_MESSAGES' ).mkdir( parents = True )
        ( tmp_path / 'sv' / 'LC_MESSAGES' / 'messages.mo' ).touch( exist_ok = True )
        ( tmp_path / 'en' / 'LC_MESSAGES' ).mkdir( parents = True )
        ( tmp_path / 'en' / 'LC_MESSAGES' / 'messages.mo' ).touch( exist_ok = True )
        ( tmp_path / 'dk' / 'LC_MESSAGES' ).mkdir( parents = True )
        ( tmp_path / 'dk' / 'LC_MESSAGES' / 'messages.po' ).touch( exist_ok = True )
        ( tmp_path / 'de' / 'MESSAGES' ).mkdir( parents = True )
        ( tmp_path / 'de' / 'MESSAGES' / 'messages.po' ).touch( exist_ok = True )
        ( tmp_path / 'fi_messages.po' ).touch( exist_ok = True )

        with patch( f'{ module }.find_locales_directory', return_value = tmp_path ):
            lang_list = get_available_languages()

            assert len( lang_list ) == 2
            assert lang_list == [ 'en', 'sv' ]


    def test_returns_empty_list_when_no_languages_exist( self, module: str ) -> None:
        """ Return an empty list for an empty locales directory.

        Args:
            module (str): Fixture for module import path
        """

        with patch( f'{ module }.find_locales_directory', return_value = [] ):
            lang_list = get_available_languages()

            assert len( lang_list ) == 0


    def test_scan_error_is_reported_and_returns_empty_list( self, capsys: CaptureFixture[ str ], module: str ) -> None:
        """ Report a scan failure occurring before any languages are found.

        Args:
            capsys (CaptureFixture[ str ]): Fixture to capture print output
            module (str): Fixture for module import path
        """

        locale_dir = Mock( spec = Path )
        locale_dir.iterdir.side_effect = Exception( 'Some error' )

        with patch( f'{ module }.find_locales_directory', return_value = locale_dir ):
            lang_list = get_available_languages()

            locale_dir.iterdir.assert_called_once_with()
            assert len( lang_list ) == 0

            captured = capsys.readouterr()
            assert captured.out == 'Error scanning for languages: Some error\n'


    def test_scan_error_preserves_languages_already_found( self, capsys: CaptureFixture[ str ], module: str, tmp_path: Path ) -> None:
        """ Return sorted languages collected before a later scan failure.

        Args:
            capsys (CaptureFixture[ str ]): Fixture to capture print output
            module (str): Fixture for module import path
            tmp_path (Path): Temporary directory
        """

        ( tmp_path / 'sv' / 'LC_MESSAGES' ).mkdir( parents = True )
        ( tmp_path / 'sv' / 'LC_MESSAGES' / 'messages.mo' ).touch( exist_ok = True )
        ( tmp_path / 'en' / 'LC_MESSAGES' ).mkdir( parents = True )
        ( tmp_path / 'en' / 'LC_MESSAGES' / 'messages.mo' ).touch( exist_ok = True )

        locale_dir = Mock( spec = Path )
        locale_dir.iterdir.return_value = [ tmp_path / 'sv',
                                           tmp_path / 'en',
                                           1 ]

        with patch( f'{ module }.find_locales_directory', return_value = locale_dir ):
            lang_list = get_available_languages()

            locale_dir.iterdir.assert_called_once_with()
            assert lang_list == [ 'en', 'sv' ]

            captured = capsys.readouterr()
            assert captured.out.startswith( 'Error scanning for languages: ' )


class TestSystemLocale:

    @pytest.mark.parametrize( ( 'detected_locale', 'expected_locale' ),
                             [ ( 'sv_SE', 'sv_SE' ),
                              ( 'en_US', 'en_US' ),
                              ( 'sv_SE.UTF-8', 'sv_SE' ),
                              ( None, 'sv_SE' ), ], )
    def test_returns_detected_locale_or_swedish_fallback( self, module: str, detected_locale: str | None, expected_locale: str ) -> None:
        """ Remove an encoding suffix and use Swedish when detection returns None.

        Args:
            module (str): Fixture for module import path
            detected_locale (str | None): Simulated locale from getdefaultlocale
            expected_locale (str): Expected decided locale
        """

        with patch( f'{ module }.locale.getdefaultlocale', return_value = ( detected_locale, 'UTF-8' ) ):
            decided_locale = get_system_locale()

            assert expected_locale == decided_locale


    @pytest.mark.parametrize( 'error_type', [ ValueError, TypeError ] )
    def test_locale_detection_error_returns_swedish( self, module: str , error_type: type[ ValueError ] | type[ TypeError ] ) -> None:
        """ Return sv_SE when locale detection raises a handled exception.

        Args:
            module (str): Fixture for module import path
            error_type (type[ ValueError] | type[ TypeError ]): Simulated error
        """

        with patch( f'{ module }.locale.getdefaultlocale', side_effect = error_type ):
            decided_locale = get_system_locale()

            assert decided_locale == 'sv_SE'


class TestSetupLocalization:

    def test_explicit_language_skips_system_locale_detection( self, module: str, tmp_path: Path ) -> None:
        """ Use the supplied language without consulting the system locale.

        Args:
            module (str): Fixture for module import path
            tmp_path (Path): Temporary directory
        """

        lang = 'sv_SE'

        with ( patch( f'{ module }.get_system_locale' ) as get,
              patch( f'{ module }.find_locales_directory', return_value = tmp_path ),
              patch( f'{ module }.gettext.translation' ) as gettext ):
            setup_localization( language = lang )

            get.assert_not_called()
            gettext.assert_called_once_with( 'messages',
                                            localedir = str( tmp_path ),
                                            languages = [ lang ],
                                            fallback = True )


    def test_missing_language_uses_system_locale( self, module: str, tmp_path: Path ) -> None:
        """ Detect the system locale when language is None.

        Args:
            module (str): Fixture for module import path
            tmp_path (Path): Temporary directory
        """

        with ( patch( f'{ module }.get_system_locale', return_value = 'sv_SE' ) as get,
              patch( f'{ module }.find_locales_directory', return_value = tmp_path ),
              patch( f'{ module }.gettext.translation' ) as gettext ):
            setup_localization()

            get.assert_called_once_with()
            gettext.assert_called_once_with( 'messages',
                                            localedir = str( tmp_path ),
                                            languages = [ get.return_value ],
                                            fallback = True )


    @pytest.mark.parametrize( 'domain',
                             [ 'messages', 'custom' ] )
    def test_loads_translation_with_domain_directory_language_and_fallback( self, module: str, tmp_path: Path, domain: str ) -> None:
        """ Pass the domain, string directory, language list, and fallback=True.

        Args:
            module (str): Fixture for module import path
            tmp_path (Path): Temporary directory
            domain (str): Domain name to look for
        """

        with ( patch( f'{ module }.get_system_locale', return_value = 'sv_SE' ) as get,
              patch( f'{ module }.find_locales_directory', return_value = tmp_path ),
              patch( f'{ module }.gettext.translation' ) as gettext ):
            setup_localization( domain = domain, )

            get.assert_called_once_with()
            gettext.assert_called_once_with( domain,
                                            localedir = str( tmp_path ),
                                            languages = [ get.return_value ],
                                            fallback = True )


    def test_stores_and_returns_loaded_translation_function( self, module: str ) -> None:
        """ Assign translation.gettext to the module's _ and return that function.

        Args:
            module (str): Fixture for module import path
        """

        with ( patch( f'{ module }.gettext.translation', return_value = Mock() ) as get_,
              patch( f'{ module }.get_system_locale' ),
              patch( f'{ module }.find_locales_directory' ) ):
            lang = setup_localization()

            assert lang is get_.return_value.gettext
            assert localization._ is lang


    def test_loading_error_reports_warning_and_uses_identity_translation( self, module: str, capsys: CaptureFixture[ str ] ) -> None:
        """ Report loading failure and store/return a function preserving input.

        Args:
            module (str): Fixture for module import path
            capsys (CaptureFixture[ str ]): Fixture to capture print output
        """

        with ( patch( f'{ module }.gettext.translation', side_effect = Exception( 'SimError' ) ),
              patch( f'{ module }.find_locales_directory' ) ):
            lang = setup_localization()

            output = capsys.readouterr().out
            assert 'SimError' in output
            assert 'Falling back to English' in output
            assert 'Warning: Could not load translation' in output

            for text in [ 'Sométhing', '', 'ÅäÖ' ]:
                assert lang( text ) == text


class TestTranslate:

    @pytest.mark.parametrize( 'text', [ 'Sométhing', '', 'ÅäÖ' ] )
    def test_translate_calls_current_translator_and_returns_result( self, module: str, text: str ) -> None:
        """ Pass text to the module's current _ function and return its result.

        Args:
            module (str): Fixture for module import path
            text (str): String to test translation
        """

        with patch( f'{ module }._', return_value = 'Translated result', ) as translator:
            result = translate( text )

        translator.assert_called_once_with( text )
        assert result == 'Translated result'


    def test_translate_uses_replacement_translator_after_language_change( self, module: str, tmp_path: Path ) -> None:
        """ Use the newly installed translation function after change_language.

        Args:
            module (str): Fixture for module import path
            tmp_path (Path): Temporary directory
        """

        eng = Mock()
        eng.gettext.return_value = 'Hello'

        sv = Mock()
        sv.gettext.return_value = 'Hej'

        with ( patch( f'{ module }.find_locales_directory', return_value = tmp_path ),
              patch( f'{ module }.gettext.translation', side_effect = [ eng, sv ] ) as load_translation ):
            change_language( 'en_US' )
            assert translate( 'Greeting' ) == 'Hello'
            assert localization._ is eng.gettext

            change_language( 'sv_SE' )
            assert translate( 'Greeting' ) == 'Hej'
            assert localization._ is sv.gettext

            eng.gettext.assert_called_once_with( 'Greeting' )
            sv.gettext.assert_called_once_with( 'Greeting' )

            assert [ recorded.kwargs[ 'languages' ]
                    for recorded in load_translation.call_args_list ] == [ [ 'en_US' ], [ 'sv_SE' ] ]
