"""
Test cases for custom menu controls

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter.ttk import Button, Frame
from typing import cast
from unittest.mock import Mock, call, patch

import pytest

from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.sequence import Sequence
from automation_menu.ui.components.custom_menu import CustomMenu
from tests.conftest import script_info


@pytest.fixture
def custom_menu() -> CustomMenu:
    """ Test ficture to provide CustomMenu without creating Tk calls """

    m: CustomMenu = CustomMenu.__new__( CustomMenu )

    m.parent = Mock()
    m.main_object = Mock()
    m.menu_button = Mock()
    m.popup = Mock()
    m._frame = Mock()
    m._canvas = Mock()
    m._scrollbar = Mock()
    m._menu_container = Mock()

    m.exec_list = []
    m._max_height = 500
    m._skip_next_open = False
    m._visible = False
    m._window_id = 1

    m._menu_container.winfo_children.return_value = []
    m._menu_container.grid_slaves.return_value = []
    m.popup.winfo_children.return_value = []

    m._menu_container.winfo_reqwidth.return_value = 200
    m._menu_container.winfo_reqheight.return_value = 100
    m._scrollbar.winfo_reqwidth.return_value = 15
    m._canvas.bbox.return_value = ( 0, 0, 200, 100 )

    m.menu_button.winfo_rootx.return_value = 20
    m.menu_button.winfo_rooty.return_value = 30
    m.menu_button.winfo_height.return_value = 25

    return m


class TestCreation:

    @pytest.mark.parametrize( 'exec_list', [ [ script_info ], { 'a': Sequence() } ] )
    def test_creation_stores_dependencies_and_starts_hidden( self, exec_list: list[ ScriptInfo ] | dict[ str, Sequence ] ) -> None:
        """ Store parent, execution list, and main object; withdraw popup.

        Args:
            exec_list (list[ ScriptInfo ] | dict[ str, Sequence ]): List of entries to add to menu
        """

        module: str = 'automation_menu.ui.components.custom_menu'

        parent = Mock()
        text: str = 'Test menu'
        main_object = Mock()

        with ( patch( f'{ module }.Button', return_value = Mock( spec = Button ) ),
              patch( f'{ module }.Toplevel' ) as tl,
              patch( f'{ module }.Frame' ),
              patch( f'{ module }.Canvas' ),
              patch( f'{ module }.Scrollbar' ) ):

            cm = CustomMenu( parent = parent,
                            text = text,
                            exec_list = exec_list,
                            main_object = main_object )

            assert cm.parent is parent
            assert cm.exec_list is exec_list
            assert cm.main_object is main_object
            assert cm._visible is False

            tl.return_value.withdraw.assert_called_once_with()


    def test_menu_button_opens_popup( self ) -> None:
        """ Register show_popup_menu as the button command. """

        module: str = 'automation_menu.ui.components.custom_menu'

        parent = Mock()
        text: str = 'Test menu'
        main_object = Mock()

        with ( patch( f'{ module }.Button', return_value = Mock( spec = Button ) ) as btn,
              patch( f'{ module }.Toplevel' ),
              patch( f'{ module }.Frame' ),
              patch( f'{ module }.Canvas' ),
              patch( f'{ module }.Scrollbar' ) ):

            cm = CustomMenu( parent = parent,
                            text = text,
                            exec_list = [],
                            main_object = main_object )

            btn.assert_called_once_with( master = parent,
                                        text = text,
                                        command = cm.show_popup_menu )


    def test_creation_registers_popup_and_resize_handlers( self ) -> None:
        """ Bind Escape, focus loss, clicks, and configure events. """

        module: str = 'automation_menu.ui.components.custom_menu'

        parent = Mock()
        text: str = 'Test menu'
        main_object = Mock()

        with ( patch( f'{ module }.Button' ) as btn,
              patch( f'{ module }.Toplevel' ) as tl,
              patch( f'{ module }.Frame' ) as fr,
              patch( f'{ module }.Canvas' ) as cv,
              patch( f'{ module }.Scrollbar' ) ):

            cm = CustomMenu( parent = parent,
                            text = text,
                            exec_list = [],
                            main_object = main_object )

            tl.return_value.overrideredirect.assert_called_once_with( True )
            tl.return_value.config.assert_called_once_with( relief = 'flat',
                                                           borderwidth = 2,
                                                           highlightcolor = "#6F7577",
                                                           highlightthickness = 2 )
            tl_calls = [ call( '<Escape>', cm._on_escape_popup ),
                        call( '<FocusOut>', cm._on_popup_focus_set ),
                        call( '<Button-1>', cm._check_click_outside ) ]
            assert tl.return_value.bind.mock_calls == tl_calls

            fr.return_value.bind.assert_called_once_with( '<Configure>',
                                                         cm._on_container_config )

            cv.return_value.bind.assert_called_once_with( '<Configure>',
                                                         cm._on_canvas_config )


    def test_creation_connects_canvas_and_scrollbar( self ) -> None:
        """ Connect scrolling callbacks and embed the menu container. """

        module: str = 'automation_menu.ui.components.custom_menu'

        parent = Mock()
        text: str = 'Test menu'
        main_object = Mock()

        with ( patch( f'{ module }.Button' ),
              patch( f'{ module }.Toplevel' ),
              patch( f'{ module }.Frame' ),
              patch( f'{ module }.Canvas' ) as cv,
              patch( f'{ module }.Scrollbar' ) as sb ):

            cm = CustomMenu( parent = parent,
                            text = text,
                            exec_list = [],
                            main_object = main_object )

            sb.assert_called_once_with( master = cm._frame,
                                       orient = 'vertical',
                                       command = cm._canvas.yview )
            cv.return_value.configure.assert_called_once_with( yscrollcommand = cm._scrollbar.set )


class TestPopupContent:

    @pytest.mark.parametrize( 'kind_script_info', [ True, False ] )
    def test_creates_menu_items_with_dependencies( self, kind_script_info: bool, script_info: ScriptInfo, custom_menu: CustomMenu ) -> None:
        """ Use the appropriate item class and preserve execution-list order.

        Args:
            kind_script_info (bool): True if testing adding script info's,
                else sequences
            script_info (ScriptInfo): Fixture for a default ScriptInfo
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
        """

        module: str = 'automation_menu.ui.components.custom_menu'
        custom_menu.exec_list = [ script_info ] if kind_script_info else { 'a': Sequence() }

        with ( patch( f'{ module }.SequenceMenuItem', return_value = Mock() ) as seq,
              patch( f'{ module }.ScriptMenuItem', return_value = Mock() ) as si ):
            custom_menu._create_popup_content()

            if isinstance( custom_menu.exec_list, dict ):
                item = list( custom_menu.exec_list.values() )[ 0 ]
                seq.assert_called_once_with( sequence_menu = custom_menu._menu_container,
                                            sequence = item,
                                            main_object = custom_menu.main_object,
                                            menu_hide_callback = custom_menu.hide_popup_menu )

                call_list = [ call( '<Enter>' , seq.return_value.on_enter, add = '+'  ),
                             call( '<Leave>' , seq.return_value.on_leave, add = '+' ) ]
                assert seq.return_value.menu_button.bind.mock_calls == call_list
                seq.return_value.menu_button.grid.assert_called_once_with( row = 0,
                                                                          column = 0,
                                                                          sticky = 'we',
                                                                          padx = 2,
                                                                          pady = 1 )

            else:
                si.assert_called_once_with( script_menu = custom_menu._menu_container,
                                           script_info = custom_menu.exec_list[ 0 ],
                                           main_object = custom_menu.main_object,
                                           menu_hide_callback = custom_menu.hide_popup_menu )

                call_list = [ call( '<Enter>' , si.return_value.on_enter, add = '+'  ),
                             call( '<Leave>' , si.return_value.on_leave, add = '+' ) ]
                assert si.return_value.menu_button.bind.mock_calls == call_list
                si.return_value.menu_button.grid.assert_called_once_with( row = 0,
                                                                          column = 0,
                                                                          sticky = 'we',
                                                                          padx = 2,
                                                                          pady = 1 )

            cast( Mock, custom_menu.popup.update_idletasks ).assert_called_once_with()


    @pytest.mark.parametrize( 'items', [ [], {} ] )
    def test_empty_execution_list_creates_no_items( self, custom_menu: CustomMenu, items: list[ ScriptInfo ] | dict ) -> None:
        """ Handle empty script and sequence collections.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
            items (list[ ScriptInfo ] | dict): Empty collection to test with
        """

        module: str = 'automation_menu.ui.components.custom_menu'
        custom_menu.exec_list = items

        with ( patch( f'{ module }.SequenceMenuItem', return_value = Mock() ) as seq,
              patch( f'{ module }.ScriptMenuItem', return_value = Mock() ) as si ):
            custom_menu._create_popup_content()

            if isinstance( items, dict ):
                seq.return_value.assert_not_called()
                call_list = []
                assert seq.return_value.menu_button.bind.mock_calls == call_list
                seq.return_value.menu_button.grid.assert_not_called()

            else:
                si.return_value.assert_not_called()
                call_list = []
                assert si.return_value.menu_button.bind.mock_calls == call_list
                si.return_value.menu_button.grid.assert_not_called()

            cast( Mock, custom_menu.popup.update_idletasks ).assert_called_once_with()


class TestRebuild:

    @pytest.mark.parametrize( 'use_script_info', [ True, False ] )
    def test_rebuild_menu_replaces_existing_menu_widgets( self, custom_menu: CustomMenu, use_script_info: bool, script_info: ScriptInfo ) -> None:
        """ Forget and destroy old widgets before creating replacement content.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
            use_script_info (bool): True if testing adding script info's,
                else sequences
            script_info (ScriptInfo): Fixture for an ScriptInfo instance
        """

        if use_script_info:
            exec_list = [ script_info ]

        else:
            exec_list = { 'a': Sequence() }

        m_widget = Mock()

        with patch.object( custom_menu, '_create_popup_content' ) as create:
            cast( Mock, custom_menu._menu_container ).grid_slaves.return_value = [ m_widget ]

            custom_menu.rebuild_menu( exec_list = exec_list )

            m_widget.grid_forget.assert_called_once_with()

            create.assert_called_once_with()


    @pytest.mark.parametrize( 'use_script_info', [ True, False ] )
    def test_rebuild_menu_uses_new_execution_list( self, custom_menu: CustomMenu, use_script_info: bool, script_info: ScriptInfo ) -> None:
        """ Make the new execution list available when content is created.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
            use_script_info (bool): True if testing adding script info's,
                else sequences
            script_info (ScriptInfo): Fixture for an ScriptInfo instance
        """

        def check_exec_list() -> None:
            """ Helper to verify if new_exec_list is used at
            at content creation
            """

            assert custom_menu.exec_list is new_exec_list


        if use_script_info:
            new_exec_list = [ script_info ]

        else:
            new_exec_list = { 'a': Sequence() }

        with patch.object( custom_menu, '_create_popup_content', side_effect = check_exec_list ):
            custom_menu.rebuild_menu( new_exec_list )

        assert custom_menu.exec_list is new_exec_list


    @pytest.mark.parametrize( ( 'content_height', 'expected_visible_height' ),
                             [ pytest.param( 100, 100, id = 'below-limit' ),
                              pytest.param( 500, 500, id = 'at-limit' ),
                              pytest.param( 700, 500, id = 'above-limit' ), ], )
    def test_rebuild_updates_canvas_dimensions_and_scrollregion( self, custom_menu: CustomMenu, content_height: int, expected_visible_height: int ) -> None:
        """ Use requested width and limit height to the configured maximum.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
            content_height (int): Anticipated heights
            expected_visible_height (int): Anticipated visible height
        """

        content_width: int = 200
        scroll_reqion = ( 0, 0, content_width, content_height )

        container = cast( Mock, custom_menu._menu_container )
        canvas = cast( Mock, custom_menu._canvas )

        custom_menu._max_height = 500
        container.winfo_reqwidth.return_value = content_width
        container.winfo_reqheight.return_value = content_height
        canvas.bbox.return_value = scroll_reqion

        with patch.object( custom_menu, '_create_popup_content' ):
            cast( Mock, custom_menu )._menu_container.winfo_reqheight.return_value = content_height
            custom_menu.rebuild_menu( [] )

        canvas.bbox.assert_called_once_with( custom_menu._window_id )
        canvas.configure.assert_called_once_with( width = content_width,
                                                 height = expected_visible_height,
                                                 scrollregion = scroll_reqion )


    @pytest.mark.parametrize( 'visible', [ False, True ] )
    def test_rebuild_repositions_only_visible_popup( self, custom_menu: CustomMenu, visible: bool ) -> None:
        """ Position an open popup below the button without opening a hidden one.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
            visible (bool): Should popup be visible
        """

        popup = cast( Mock, custom_menu.popup )
        btn = cast( Mock, custom_menu.menu_button )

        with patch.object( custom_menu, '_create_popup_content' ):
            custom_menu._visible = visible
            custom_menu.rebuild_menu( [] )

            if visible:
                x = btn.winfo_rootx.return_value
                y = btn.winfo_rooty.return_value + btn.winfo_height.return_value
                popup.geometry.assert_called_once_with( f'+{ x }+{ y }' )

            else:
                popup.geometry.assert_not_called()


class TestShowAndHide:

    def test_show_consumes_skip_next_open_without_opening( self, custom_menu: CustomMenu ) -> None:
        """ Clear the skip flag and leave the popup closed.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
        """

        custom_menu._skip_next_open = True
        popup = cast( Mock, custom_menu.popup )

        custom_menu.show_popup_menu()

        assert custom_menu._skip_next_open is False
        assert custom_menu._visible is False
        popup.deiconify.assert_not_called()


    def test_show_hides_popup_when_already_visible( self, custom_menu: CustomMenu ) -> None:
        """ Toggle an already visible popup closed.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
        """

        custom_menu._visible = True

        with patch.object( custom_menu, 'hide_popup_menu' ) as hide:
            custom_menu.show_popup_menu()

            hide.assert_called_once_with()


    @pytest.mark.parametrize( 'has_children', [ False, True ] )
    def test_show_creates_content_only_when_container_is_empty( self, custom_menu: CustomMenu, has_children: bool ) -> None:
        """ Reuse existing menu widgets or create them when needed.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
            has_children (bool): Should children be defined in test
        """

        container = cast( Mock, custom_menu._menu_container )
        container.winfo_children.return_value = [ 1, 2, 3 ] if has_children else []

        with patch.object( custom_menu, '_create_popup_content' ) as create:
            custom_menu.show_popup_menu()

            if has_children:
                create.assert_not_called()

            else:
                create.assert_called_once_with()


    @pytest.mark.parametrize( ( 'content_height', 'visible_height', 'expected_geometry' ),
                             [ pytest.param( 100, 100, '210x110+20+55', id = 'below-limit' ),
                              pytest.param( 500, 500, '210x510+20+55', id  = 'at-limit' ),
                              pytest.param( 700, 500, '225x510+20+55', id = 'above-limit' ), ], )
    def test_show_sizes_and_positions_popup( self, custom_menu: CustomMenu, content_height: int, visible_height: int, expected_geometry: str ) -> None:
        """ Cap height and include scrollbar width only for overflowing content.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
            content_height (int): Height of testing content
            visible_height (int): Height of visible testing content
            expected_geometry (str): Geometry string for testing content
        """

        container = cast( Mock, custom_menu._menu_container )
        canvas = cast( Mock, custom_menu._canvas )
        popup = cast( Mock, custom_menu.popup )

        container.winfo_reqheight.return_value = content_height

        with patch.object( custom_menu, '_create_popup_content' ):
            custom_menu.show_popup_menu()

        assert canvas.configure.call_args_list == [ call( height = visible_height ),
                                                   call( width = 200 ), ]
        canvas.itemconfig.assert_called_once_with( custom_menu._window_id,
                                                  width = 200, )
        popup.geometry.assert_called_once_with( expected_geometry )


    def test_show_displays_focuses_and_enables_mousewheel( self, custom_menu: CustomMenu ) -> None:
        """Show the popup, focus it, bind scrolling, and mark it visible.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
        """

        popup = cast( Mock, custom_menu.popup )

        custom_menu.show_popup_menu()

        popup.deiconify.assert_called_once()
        popup.focus_set.assert_called_once()
        popup.bind_all.assert_called_once_with( '<MouseWheel>',
                                               custom_menu._on_mousewheel )

        assert custom_menu._visible is True


    def test_hide_withdraws_popup_and_disables_mousewheel( self, custom_menu: CustomMenu ) -> None:
        """ Withdraw the popup, unbind scrolling, and mark it hidden.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
        """

        popup = cast( Mock, custom_menu.popup )

        custom_menu.hide_popup_menu()

        popup.withdraw.assert_called_once()
        popup.unbind_all.assert_called_once_with( '<MouseWheel>' )

        assert custom_menu._visible is False


class TestEvents:

    @pytest.mark.parametrize( 'clicked_widget',
                             [ 'popup', 'direct_child','outside', 'none' ], )
    def test_click_hides_popup_only_when_outside( self, custom_menu: CustomMenu, clicked_widget: str ) -> None:
        """ Keep popup/direct-child clicks open; hide for outside clicks.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
            clicked_widget (str): Area to simulate click
        """

        popup = cast( Mock, custom_menu.popup )
        child = Mock()
        outside = Mock()

        popup.winfo_children.return_value = [ child ]

        widgets = { 'popup': popup,
                   'direct_child': child,
                   'outside': outside,
                   'none': None }

        event = Mock()
        event.x_root = 0
        event.y_root = 0
        event.widget.winfo_containing.return_value = widgets[ clicked_widget ]

        with patch.object( custom_menu, 'hide_popup_menu' ) as hide:
            custom_menu._check_click_outside( event )

            if clicked_widget in [ 'outside', 'none' ]:
                hide.assert_called_once_with()

            else:
                hide.assert_not_called()


    def test_canvas_resize_updates_embedded_window_width( self, custom_menu: CustomMenu ) -> None:
        """ Apply the event width to the canvas window item.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
        """

        canvas = cast( Mock, custom_menu._canvas )

        event = Mock()
        event.width = 0

        custom_menu._on_canvas_config( event )

        canvas.itemconfig.assert_called_once_with( custom_menu._window_id, width = 0 )


    @pytest.mark.parametrize( 'height', [ 100, 500, 700 ] )
    def test_container_resize_updates_canvas_and_scrollbar( self, custom_menu: CustomMenu, height: int ) -> None:
        """ Update dimensions and scroll region; show scrollbar above the limit.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
            height (int): Specified height of container
        """

        event = Mock()
        event.height = height

        canvas = cast( Mock, custom_menu._canvas )
        scrollbar = cast( Mock, custom_menu._scrollbar )

        custom_menu._on_container_config( event )

        canvas.configure.call_args_list = [ call( height = height if height <= 500 else 500 ),
                                           call( width = event.width ) ]

        if height > custom_menu._max_height:
            scrollbar.grid.assert_called_once_with( row = 0,
                                                   column = 1,
                                                   sticky = 'ns' )

        else:
            scrollbar.grid_remove.assert_called_once()


    @pytest.mark.parametrize( 'visible', [ False, True ] )
    def test_escape_hides_visible_popup_and_returns_break( self, custom_menu: CustomMenu, visible: bool ) -> None:
        """ Always return break; hide and restore button focus only when visible.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
            visible (bool): Simulated visible state
        """

        event = Mock()

        custom_menu._visible = visible
        btn = cast( Mock, custom_menu.menu_button )

        with patch.object( custom_menu, 'hide_popup_menu') as hide:
            ret = custom_menu._on_escape_popup( event )

            if visible:
                hide.assert_called_once_with()
                btn.focus_set.assert_called_once_with()

        assert ret == 'break'


    @pytest.mark.parametrize( ( 'delta', 'expected_units' ),
                             [ ( 120, -1 ),
                              ( -120, 1 ),
                              ( 240, -2 ),
                              ( 0, 0 ) ], )
    def test_mousewheel_scrolls_canvas( self, custom_menu: CustomMenu, delta: int, expected_units: int ) -> None:
        """ Convert wheel delta to signed canvas scroll units.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
            delta (int): Simulated delta movement
            expected_units (int): 
        """

        event = Mock()
        event.delta = delta
        canvas = cast( Mock, custom_menu._canvas )

        custom_menu._on_mousewheel( event )

        canvas.yview_scroll.assert_called_once_with( expected_units,
                                                    'units' )


    @pytest.mark.parametrize( 'skip_next_open', [ True, False ] )
    def test_focus_loss_does_nothing_when_hidden( self, custom_menu: CustomMenu, skip_next_open: bool ) -> None:
        """ Leave popup state unchanged when it is already hidden.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
            skip_next_open (bool): Test that attribute is unchanged
        """

        custom_menu._visible = False
        custom_menu._skip_next_open = skip_next_open
        parent = cast( Mock, custom_menu.parent )

        with patch.object( custom_menu, 'hide_popup_menu' ) as hide:
            custom_menu._on_popup_focus_set( Mock() )

            hide.assert_not_called()

        assert custom_menu._visible is False
        assert custom_menu._skip_next_open is skip_next_open
        parent.winfo_pointerx.assert_not_called()
        parent.winfo_pointery.assert_not_called()
        parent.winfo_containing.assert_not_called()


    @pytest.mark.parametrize( 'pointer_on_button', [ False, True ] )
    def test_focus_loss_hides_popup_and_sets_skip_flag( self, custom_menu: CustomMenu, pointer_on_button: bool ) -> None:
        """ Skip the next opening only when the pointer is over the menu button.

        Args:
            custom_menu (CustomMenu): Fixture for an CustomMenu instance
            pointer_on_button (bool): True if test should simulatethat pointer was on button when click occured
        """

        custom_menu._visible = True
        custom_menu._skip_next_open = not pointer_on_button
        parent = cast( Mock, custom_menu.parent )
        parent.winfo_pointerx.return_value = 1
        parent.winfo_pointery.return_value = 1

        parent.winfo_containing.return_value = custom_menu.menu_button if pointer_on_button else Mock()

        with patch.object( custom_menu, 'hide_popup_menu' ) as hide:
            custom_menu._on_popup_focus_set( Mock() )

            parent.winfo_containing.assert_called_once_with( 1, 1 )
            hide.assert_called_once_with()
            assert custom_menu._skip_next_open is pointer_on_button
