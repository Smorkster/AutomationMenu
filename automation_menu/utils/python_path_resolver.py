"""
Resolver to locate Python install path.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
import sys


def find_python_exe() -> str:
    """ Find out the path to current Python interpreter.

    Returns:
        (str): Full path to the file of Python interpreter.

    Raises:
        FileNotFoundException when no interpreter can be used for testing.
    """

    candidates = []

    if sys.prefix != sys.base_prefix:
        candidates.extend( [ [ sys.executable ] ] )

    py_launcher = shutil.which( 'py' )

    if py_launcher:
        candidates.extend( [ [ py_launcher, '-3.14' ],
                            [ py_launcher, '-3' ], ] )

    # PATH fallbacks
    for name in ( 'python.exe', 'python3.exe', 'python' ):
        found = shutil.which( name )

        if found:
            candidates.append( [ found ] )

    # Common install locations
    roots = [ Path.home() / 'AppData' / 'Local' / 'Programs' / 'Python',
             Path( 'C:/Program Files' ),
             Path( 'C:/Program Files (x86)' ), ]

    for root in roots:

        if root.exists():
            candidates.extend( [ str( p ) ]
                              for p in root.glob( '**/python.exe' )
                              if 'WindowsApps' not in str( p ) )

    for candidate in candidates:
        try:
            result = subprocess.run( candidate + [ '-c', 'import sys; print( sys.executable )' ],
                                    capture_output = True,
                                    text = True,
                                    timeout = 5, )

            if result.returncode == 0:
                python_exe = result.stdout.strip()

                if python_exe and Path( python_exe ).exists():

                    return python_exe

        except Exception:

            continue

    raise FileNotFoundError( 'Could not find a usable Python installation. '
                            'Install Python or add it to PATH.' )
