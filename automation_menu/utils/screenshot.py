"""
Take a screenshot of main window
Convert to PNG and save to disc

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import os
import tempfile
import win32con
import win32gui
import win32ui

from datetime import datetime
from PIL import Image
from tkinter import Tk

from automation_menu.models import ScriptInfo

def _convert_bmp_to_png( bmp_path: str = '', delete_bmp: bool = False ) -> str:
    """ Convert a BMP file to PNG format

    Args:
        bmp_path (str): Path to BMP-file to convert
        delete_bmp (bool): Should the BMP-file be deleted after convertion

    Returns:
        str: Path to the new PNG-file
    """

    png_path = os.path.join( tempfile.gettempdir() , f'{ os.path.basename( bmp_path ).split( '.' )[0] }.png' )
    img = Image.open( fp = bmp_path )
    img.save( fp = png_path, format = 'PNG' )

    if delete_bmp:
        os.remove( bmp_path )

    return png_path


def take_screenshot( root_window: Tk, script_info: ScriptInfo, file_name_prefix: str ) -> str:
    """ Take a screenshot of the main window and save it as a PNG file

    Args:
        root_window (Tk): TopLevel Tk widget to take screenshot of
        script (ScriptInfo): ScriptInfo about script last run
        file_name_prefix (str): A prefix for the file name

    Returns:
        str: Path to the new BMP-file
    """

    hwnd = win32gui.FindWindow( None, root_window.title() )
    wDC = win32gui.GetWindowDC( hwnd )
    dcObj=win32ui.CreateDCFromHandle( wDC )
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap( dcObj, root_window.winfo_width(), root_window.winfo_height() )
    cDC.SelectObject( dataBitMap )
    cDC.BitBlt( ( 0 , 0 ) , ( root_window.winfo_width() , root_window.winfo_height() ) , dcObj , ( 0 , 0 ), win32con.SRCCOPY )
    bmp_tempfile = os.path.join( tempfile.gettempdir(), f'{ file_name_prefix }_{ script_info.get_attr( 'filename' ) }_{ datetime.now().strftime( '%Y-%m-%d_%H.%M.%S' ) }.bmp' )
    dataBitMap.SaveBitmapFile( cDC , bmp_tempfile )

    png_path = _convert_bmp_to_png( bmp_path = bmp_tempfile, delete_bmp = True )

    # Free resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC( hwnd, wDC )
    win32gui.DeleteObject( dataBitMap.GetHandle() )

    return png_path
