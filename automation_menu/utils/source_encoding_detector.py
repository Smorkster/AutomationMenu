"""
Parse file for detection of encoding header

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


import re
from pathlib import Path

CODING_RE = re.compile( rb'coding[:=]\s*([-\w.]+)' )

def get_python_source_encoding( script_path: str, detected_encoding : str ) -> str:
    """ Try to detect any file encoding header

    Args:
        script_path (str): Path to file to parse
        detected_encoding (str): File encoding to enabled line reads

    Returns:
        (str): Found encoding string
    """

    with Path( script_path ).open( 'r', encoding = detected_encoding ) as f:
        line1 = f.readline()
        line2 = f.readline()

    for line in [ line1, line2 ]:
        match = CODING_RE.search( bytes( line, detected_encoding ) )

        if match:

            return match.group( 1 ).decode( 'ascii' )

    return ''
