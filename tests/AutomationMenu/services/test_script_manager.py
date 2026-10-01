"""
Test cases for script manager

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


import json
from typing import Callable, cast
import pytest

from json import JSONDecodeError
from pathlib import Path
from queue import Queue
from unittest.mock import Mock, patch

from automation_menu.models.application_state import ApplicationState
from automation_menu.models.enums import ApplicationRunState
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.scriptmetadata import ScriptMetadata
from automation_menu.models.user import User
from automation_menu.services.script_manager import ScriptManager
from tests.conftest import app_run_state, app_state, output_queue


class TestCreate:

      def test_create_manager( self ) -> None:
            """ Create a basic manager """

            user = Mock()
            m: ScriptManager = ScriptManager( script_dir_path = [],
                                             current_user = user )


      @pytest.mark.parametrize( 'output', [ None, output_queue ] )
      @pytest.mark.parametrize( 'app_state', [ None, app_state ] )
      @pytest.mark.parametrize( 'app_run_state', [ None, app_run_state ] )
      def test_create_manager_queue_and_states_adds_through_gather_scripts( self, output: Queue | None, app_state: ApplicationState | None, app_run_state: ApplicationRunState | None, menu_cache_path: Path, mock_user: Callable[ [ str ], User ] ) -> None:
            """ Create a manager and assert that queue and states are
            added when gathering scripts.

            Args:
                output (Queue | None): Fixture for an Queue instance, or not set
                app_state (ApplicationState | None): Fixture for an ApplicationState instance, or not set
                app_run_state (ApplicationRunState | None): Fixture for an ApplicationRunState instance, or not set
                menu_cache_path (Path): Fixture for a Path to mocked cache path
                mock_user (Callable[ [ str ], User ]): Fixture for an User instance
            """

            m: ScriptManager = ScriptManager( script_dir_path = [],
                                             current_user = cast( User, mock_user ) )
            assert not hasattr( m, '_app_run_state' )
            assert not hasattr( m, '_app_state' )
            assert not hasattr( m, '_output_queue' )

            m._output_queue = cast( Queue, output_queue )
            m._app_state = cast( ApplicationState, app_state )
            m._app_run_state = cast( ApplicationRunState, app_run_state )

            module = 'automation_menu.services.script_manager'

            with ( patch( f'{ module }.get_menu_cache_path', return_value = menu_cache_path ),
                  patch( f'{ module }.get_scripts' ),
                  patch( f'{ module }.read_menu_cache'),
                  patch.object( m, 'write_menu_cache' ), ):
                  m.gather_scripts( output_queue = output,
                                   app_state = app_state,
                                   app_run_state = app_run_state )

            assert hasattr( m, '_app_run_state' ) if app_run_state else True
            assert hasattr( m, '_app_state' ) if app_state else True
            assert hasattr( m, '_output_queue' ) if output else True


class TestUsage:
      def test_gather_scripts_discovers_scripts_when_cache_is_missing( self, script_manager: ScriptManager, output_queue: Queue, app_state: ApplicationState, app_run_state: ApplicationRunState, menu_cache_path: Path, script_info: ScriptInfo, ) -> None:
            """ Test script discovery when there is no cache.

            Args:
                script_manager (ScriptManager): Fixture for an ScriptManager instance
                output_queue (Queue): Fixture for an Queue instance
                app_state (ApplicationState): Fixture for an ApplicationState instance
                app_run_state (ApplicationRunState): Fixture for an ApplicationRunState instance
                menu_cache_path (Path): Fixture for a Path to mocked cache path
                script_info (ScriptInfo): Fixture for an ScriptInfo instance
            """

            discovered_scripts = [ script_info ]
            module = 'automation_menu.services.script_manager'

            assert not menu_cache_path.exists()

            with ( patch( f'{ module }.get_menu_cache_path', return_value = menu_cache_path, ),
                  patch( f'{ module }.get_scripts', return_value = discovered_scripts, ) as discover,
                  patch( f'{ module }.read_menu_cache') as read_cache,
                  patch.object( script_manager, 'write_menu_cache' ) as write_cache, ):
                  script_manager.gather_scripts( output_queue = output_queue,
                                                app_state = app_state,
                                                app_run_state = app_run_state, )

                  discover.assert_called_once_with( output_queue = output_queue,
                                                   app_state = app_state,
                                                   app_run_state = app_run_state, )

                  read_cache.assert_not_called()
                  write_cache.assert_called_once_with()

            assert script_manager.get_script_list() == discovered_scripts


      def test_gather_scripts_writes_cache_after_discovery( self, script_manager: ScriptManager, output_queue: Queue, app_state: ApplicationState, app_run_state: ApplicationRunState, menu_cache_path: Path ) -> None:
            """ Test that cache if written after discovery of script has happened.

            Args:
                script_manager (ScriptManager): Fixture for an ScriptManager instance
                output_queue (Queue): Fixture for an Queue instance
                app_state (ApplicationState): Fixture for an ApplicationState instance
                app_run_state (ApplicationRunState): Fixture for an ApplicationRunState instance
                menu_cache_path (Path): Fixture for a Path to mocked cache path
            """

            module = 'automation_menu.services.script_manager'

            with ( patch.object( script_manager, 'write_menu_cache' ) as write,
                  patch( f'{ module }.get_scripts' ) as discover,
                  patch( f'{ module }.get_menu_cache_path', return_value = menu_cache_path, ),
                  patch( f'{ module }.read_menu_cache', return_value = {} ) as read, ):
                  script_manager.gather_scripts( output_queue = output_queue,
                                                app_state = app_state,
                                                app_run_state = app_run_state )

                  assert script_manager._menu_cache_path is not None
                  discover.assert_called_once_with( output_queue = output_queue,
                                                   app_state = app_state,
                                                   app_run_state = app_run_state )
                  write.assert_called_once_with()


      def test_gather_scripts_uses_existing_cache_without_discovery( self, script_manager: ScriptManager, output_queue: Queue, app_state: ApplicationState, app_run_state: ApplicationRunState, menu_cache_path: Path ) -> None:
            """ Test that cache if written after discovery of script has happened.

            Args:
                script_manager (ScriptManager): Fixture for an ScriptManager instance
                output_queue (Queue): Fixture for an Queue instance
                app_state (ApplicationState): Fixture for an ApplicationState instance
                app_run_state (ApplicationRunState): Fixture for an ApplicationRunState instance
                menu_cache_path (Path): Fixture for a Path to mocked cache path
            """

            module = 'automation_menu.services.script_manager'

            m_dict = json.loads( r'{"1948435029372741540":{"filename": "est.py", "fullpath": "C:\\test.py", "using_breakpoint": false, "scriptmeta": {"synopsis": "Test", "author": "Smorkster (smorkster)", "description": "Test", "state": "Prod", "version": "1.0", "required_ad_groups": [], "allowed_users": [], "script_input_parameters": [], "disable_minimize_on_running": true, "persistent_gui": false, "persistent_gui_multiple": false}}}' )
            menu_cache_path.touch()

            with ( patch( f'{ module }.get_menu_cache_path', return_value = menu_cache_path ),
                  patch( f'{ module }.read_menu_cache', return_value = m_dict ) as read,
                  patch( f'{ module }.get_scripts' ) as discover,
                  patch.object( script_manager, 'write_menu_cache' ) as write ):
                  script_manager.gather_scripts( output_queue = output_queue,
                                                app_state = app_state,
                                                app_run_state = app_run_state )


                  assert script_manager._menu_cache_path is not None
                  read.assert_called_once_with( menu_cache_path )

                  assert len( script_manager._script_list ) == 1
                  assert script_manager._script_list[ 0 ].filename == m_dict[ '1948435029372741540' ][ 'filename' ]

                  discover.assert_not_called()
                  write.assert_not_called()


      @pytest.mark.parametrize( ( 'cache_error', 'err_msg' ),
                               [ pytest.param( JSONDecodeError( '', '', 0,  ), 'The menu cache file could not be decoded. Will gather info from script files.' ),
                                pytest.param( FileNotFoundError, 'The menu cache file could not be located. Will gather info from script files.' ) ] )
      def test_gather_scripts_falls_back_to_discovery_when_cache_is_invalid( self, script_manager: ScriptManager, output_queue: Queue, app_state: ApplicationState, app_run_state: ApplicationRunState, menu_cache_path: Path, cache_error: JSONDecodeError | type[ FileNotFoundError ], err_msg: str ) -> None:
            """ Test that cache discovery is fallback at cache read failure,
            and that its informed in the output queue.

            Args:
                script_manager (ScriptManager): Fixture for an ScriptManager instance
                output_queue (Queue): Fixture for an Queue instance
                app_state (ApplicationState): Fixture for an ApplicationState instance
                app_run_state (ApplicationRunState): Fixture for an ApplicationRunState instance
                menu_cache_path (Path): Fixture for a Path to mocked cache path
                cache_error (JSONDecodeError | type[ FileNotFoundError ]): Error type for invalid cache
                err_msg (str): Error message sent to output queue
            """

            module = 'automation_menu.services.script_manager'
            menu_cache_path.touch()

            with ( patch( f'{ module }.get_menu_cache_path', return_value = menu_cache_path ),
                  patch( f'{ module }.read_menu_cache', side_effect = cache_error ),
                  patch( f'{ module }.get_scripts' ) as discover,
                  patch.object( script_manager, 'write_menu_cache' ) as write,
                   patch( f'{ module }.ScriptInfo' ) as si ):

                  script_manager.gather_scripts( output_queue = output_queue,
                                                app_state = app_state,
                                                app_run_state = app_run_state )
                  si.from_dict.assert_not_called()
                  discover.assert_called_once_with( output_queue = output_queue,
                                                   app_state = app_state,
                                                   app_run_state = app_run_state )
                  write.assert_called_once_with()

                  assert output_queue.unfinished_tasks == 1
                  qi = output_queue.get()

                  assert qi[ 'line' ] ==  err_msg


      def test_gather_scripts_clear_cache_rebuilds_script_list( self, script_manager: ScriptManager, output_queue: Queue, app_state: ApplicationState, app_run_state: ApplicationRunState, menu_cache_path: Path, script_info: ScriptInfo ) -> None:
            """ Test that cache if written after discovery of script has happened.

            Args:
                script_manager (ScriptManager): Fixture for an ScriptManager instance
                output_queue (Queue): Fixture for an Queue instance
                app_state (ApplicationState): Fixture for an ApplicationState instance
                app_run_state (ApplicationRunState): Fixture for an ApplicationRunState instance
                menu_cache_path (Path): Fixture for a Path to mocked cache path
                script_info (ScriptInfo): Fixture for an ScriptInfo instance
            """

            module = 'automation_menu.services.script_manager'

            script_manager._script_list.append( ScriptInfo.__new__( ScriptInfo ) )
            old_scripts = [ script_info ]
            script_manager._script_list = old_scripts

            def discover_scripts( **kwargs: dict ) -> list:
                  """ Helper to assert that list is cleared

                  Args:
                        kwargs (dict): Collect any argument
                  """

                  assert old_scripts == []
                  assert script_manager.get_script_list() == []

                  return []

            with ( patch( f'{ module }.get_menu_cache_path', return_value = menu_cache_path ),
                  patch( f'{ module }.recycle' ) as recycle,
                  patch.object( script_manager, 'write_menu_cache' ) as write,
                  patch( f'{ module }.get_scripts', side_effect = discover_scripts ) as discover ):
                  script_manager.gather_scripts( output_queue = output_queue,
                                                app_run_state = app_run_state,
                                                app_state = app_state,
                                                clear_cache = True )

                  recycle.assert_called_once_with( str( menu_cache_path ) )
                  discover.assert_called_once_with( output_queue = output_queue,
                                                   app_state = app_state,
                                                   app_run_state = app_run_state )
                  write.assert_called_once_with()


      def test_write_menu_cache_serializes_script_list( self, script_manager: ScriptManager, menu_cache_path: Path ) -> None:
            """ Test that cache if written after discovery of script has happened.

            Args:
                script_manager (ScriptManager): Fixture for an ScriptManager instance
                menu_cache_path (Path): Fixture for a Path to mocked cache path
            """

            module = 'automation_menu.services.script_manager'

            s1: ScriptInfo = ScriptInfo( filename = 'File1.py', fullpath = Path( 'C:\\File1.py' ), scriptmeta = ScriptMetadata( author = 'Aut 1', synopsis = 'Syn 1' ) )
            script_manager._script_list.append( s1 )
            s2: ScriptInfo = ScriptInfo( filename = 'File2.py', fullpath = Path( 'C:\\Scripts\\File2.py' ), scriptmeta = ScriptMetadata( author = 'Aut 2', synopsis = 'Syn 2' ) )
            script_manager._script_list.append( s2 )

            script_manager._menu_cache_path = menu_cache_path

            with patch( f'{ module }.write_menu_cache_file' ) as write:
                  script_manager.write_menu_cache()

                  write.assert_called_once()
                  assert write.call_args.kwargs[ 'cache_file_path' ] == menu_cache_path
                  assert isinstance( write.call_args.kwargs[ 'cache_content' ], str )

                  written_cache: dict = json.loads( write.call_args.kwargs[ 'cache_content' ] )

                  assert len( written_cache ) == 2

                  cs1, cs2 = list( written_cache.values() )

                  assert cs1[ 'filename' ] == 'File1.py'
                  assert cs1[ 'fullpath' ] == 'C:\\File1.py'
                  assert cs1[ 'scriptmeta' ][ 'author' ] == 'Aut 1'
                  assert cs1[ 'scriptmeta' ][ 'synopsis' ] == 'Syn 1'

                  assert cs2[ 'filename' ] == 'File2.py'
                  assert cs2[ 'fullpath' ] == 'C:\\Scripts\\File2.py'
                  assert cs2[ 'scriptmeta' ][ 'author' ] == 'Aut 2'
                  assert cs2[ 'scriptmeta' ][ 'synopsis' ] == 'Syn 2'


      def test_get_script_by_filename( self, script_manager: ScriptManager ) -> None:
            """ Get a ScriptInfo available in the manager,
            search by filename.

            Args:
                script_manager (ScriptManager): Fixture of a ScriptManager instance
            """

            s1: ScriptInfo = ScriptInfo( filename = 'F1.py', fullpath = Path( 'C:\\F1.py' ), scriptmeta = ScriptMetadata( synopsis = 'S', author = 'A' ) )
            s2: ScriptInfo = ScriptInfo( filename = 'F2.py', fullpath = Path( 'C:\\F2.py' ), scriptmeta = ScriptMetadata( synopsis = 'S', author = 'A' ) )

            script_manager._script_list.append( s1 )
            script_manager._script_list.append( s2 )

            s = script_manager.get_script_info_by_filename( 'F1.py' )

            assert s.filename == s1.filename
            assert s.fullpath == s1.fullpath
            assert s.scriptmeta.synopsis == s1.scriptmeta.synopsis
            assert s.scriptmeta.author == s1.scriptmeta.author


      @pytest.mark.parametrize( 'si_list', [ [],
                                            [ ScriptInfo( filename = 'F1.py', fullpath = Path( 'C:\\F1.py' ), scriptmeta = ScriptMetadata( synopsis = 'S', author = 'A' ) ),
                                             ScriptInfo( filename = 'F2.py', fullpath = Path( 'C:\\F2.py' ), scriptmeta = ScriptMetadata( synopsis = 'S', author = 'A' ) ),
                                             ScriptInfo( filename = 'F3.py', fullpath = Path( 'C:\\F3.py' ), scriptmeta = ScriptMetadata( synopsis = 'S', author = 'A' ) ) ] ] )
      def test_get_script_by_filename_that_is_not_available_in_list( self, script_manager: ScriptManager, si_list: list[ ScriptInfo ] ) -> None:
            """ Try to retrieve a ScriptInfo that is not in the managers list,
            search by filename.

            Args:
                script_manager (ScriptManager): Fixture of a ScriptManager instance
                si_list (list[ ScriptInfo ]): Defined list of ScriptInfo's to test with
            """

            for si in si_list:
                  script_manager._script_list.append( si )

            with pytest.raises( ValueError, match = r'No ScriptInfo with file name .* was found' ):
                  s = script_manager.get_script_info_by_filename( 'NotAvailable.py' )


      @pytest.mark.parametrize( 'search_term', [ 'C:\\F1.py', Path( 'C:\\F1.py' ) ] )
      def test_get_script_by_path( self, script_manager: ScriptManager, search_term: Path | str ) -> None:
            """ Get a ScriptInfo available in the manager,
            search by fullpath.

            Args:
                script_manager (ScriptManager): Fixture of a ScriptManager instance
                search_term (Path | str): Path to search list for
            """

            s1: ScriptInfo = ScriptInfo( filename = 'F1.py', fullpath = Path( 'C:\\F1.py' ), scriptmeta = ScriptMetadata( synopsis = 'S', author = 'A' ) )

            script_manager._script_list.append( s1 )

            s = script_manager.get_script_info_by_path( search_term )

            assert s.filename == s1.filename
            assert s.fullpath == s1.fullpath
            assert s.scriptmeta.synopsis == s1.scriptmeta.synopsis
            assert s.scriptmeta.author == s1.scriptmeta.author


      @pytest.mark.parametrize( 'si_list', [ pytest.param( True, id = 'has_list' ),
                                            pytest.param( False, id = 'no_list' ) ] )
      @pytest.mark.parametrize( 'search_term',
                               [ pytest.param( None, id = 'no_search' ),
                                pytest.param( '', id = 'search_no_str' ),
                                pytest.param( 'C:\\NotAvailable.py', id = 'search_str' ),
                                pytest.param( Path( 'C:\\NotAvailable.py' ), id = 'search_path' ) ] )
      def test_get_script_by_fullpath_that_is_not_available_in_list( self, script_manager: ScriptManager, script_info: ScriptInfo, si_list: bool, search_term: Path | str | None ) -> None:
            """ Try to retrieve a ScriptInfo that is not in the managers list,
            search by fullpath.

            Args:
                script_manager (ScriptManager): Fixture of a ScriptManager instance
                script_info (ScriptInfo): Fixture of a ScriptInfo instance
                si_list (bool): Defined list of ScriptInfo's to test with
                search_term (Path | str | None): Path to look for
            """

            if si_list:
                  script_manager._script_list = [ script_info ]

            with pytest.raises( ValueError, match = r'No ScriptInfo at path .* was found' ):
                  s = script_manager.get_script_info_by_path( search_term )
