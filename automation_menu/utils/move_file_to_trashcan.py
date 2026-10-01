"""
Move file to Recycle bin

Source - https://stackoverflow.com/a/79656812

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


import os

from ctypes import Structure, POINTER, byref, windll
from ctypes.wintypes import HWND, UINT, LPCWSTR, BOOL, LPVOID

class SHFILEOPSTRUCTW( Structure ):
    _fields_ = [ ( 'hwnd', HWND ),
                ( 'wFunc', UINT ),
                ( 'pFrom', LPCWSTR ),
                ( 'pTo', LPCWSTR ),
                ( 'fFlags', UINT ),
                ( 'fAnyOperationsAborted', BOOL ),
                ( 'hNameMappings', LPVOID ),
                ( 'lpszProgressTitle', LPCWSTR ), ]

shell32 = windll.shell32
shell32.SHFileOperationW.argtypes = ( POINTER( SHFILEOPSTRUCTW ), )


def recycle( file_path: str ) -> bool:
    """ Move file to Recycle bin.

    Args:
        file_path (str): Path of file to recycle.
    """

    fop = SHFILEOPSTRUCTW()
    # Path must be absolute, string must be double-null terminated
    fop.pFrom = os.path.normpath( os.path.abspath( file_path ) ) + '\0'
    fop.wFunc = 3  # FO_DELETE
    fop.fFlags = 1620  # FOF_ALLOWUNDO | FOF_NO_UI

    return shell32.SHFileOperationW( byref( fop ) ) == 0
