"""
Take a screenshot of main window
Convert to PNG and save to disc

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

import os
import tempfile
import win32con
import win32gui
import win32ui

from datetime import datetime
from pathlib import Path
from PIL import Image, ImageFile
from tkinter import Tk

from automation_menu.models import ScriptInfo


def _convert_bmp_to_png( bmp_path: str = '', delete_bmp: bool = False ) -> Path:
    """ Convert a BMP file to PNG format.

    Args:
        bmp_path (str): Path to the BMP file to convert.
        delete_bmp (bool): Whether the BMP file should be deleted after conversion.

    Returns:
        png_path (Path): Path to the new PNG file.
    """

    png_path: Path = Path( os.path.join( tempfile.gettempdir() , f'{ os.path.basename( bmp_path ).split( '.' )[0] }.png' ) )
    img: ImageFile.ImageFile = Image.open( fp = bmp_path )
    img.save( fp = png_path, format = 'PNG' )

    if delete_bmp:
        os.remove( bmp_path )

    return png_path


def take_screenshot( root_window: Tk, script_info: ScriptInfo, file_name_prefix: str ) -> Path:
    """ Take a screenshot of the main window and save it as a PNG file.

    Args:
        root_window (Tk): Top-level Tk widget to take a screenshot of.
        script_info (ScriptInfo): Information about the script that was last run.
        file_name_prefix (str): Prefix to use for the screenshot file name.

    Returns:
        png_path (Path): Path to the created PNG file.
    """

    hwnd: int = win32gui.FindWindow( None, root_window.title() )
    wDC: int = win32gui.GetWindowDC( hwnd )
    dcObj = win32ui.CreateDCFromHandle( wDC )
    cDC = dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap( dcObj, root_window.winfo_width(), root_window.winfo_height() )
    cDC.SelectObject( dataBitMap )
    cDC.BitBlt( ( 0 , 0 ) , ( root_window.winfo_width() , root_window.winfo_height() ) , dcObj , ( 0 , 0 ), win32con.SRCCOPY )
    bmp_tempfile: str = os.path.join( tempfile.gettempdir(), f'{ file_name_prefix }_{ script_info.get_attr( 'filename' ) }_{ datetime.now().strftime( '%Y-%m-%d_%H.%M.%S' ) }.bmp' )
    dataBitMap.SaveBitmapFile( cDC , bmp_tempfile )

    png_path: Path = _convert_bmp_to_png( bmp_path = bmp_tempfile, delete_bmp = True )

    # Free resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC( hwnd, wDC )
    win32gui.DeleteObject( dataBitMap.GetHandle() )

    return png_path
