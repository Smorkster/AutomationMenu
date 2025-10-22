"""
Manage secrets config file

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import json


def read_secrets_file( file_path: str ) -> dict:
    """ Read secrets

    Args:
        file_path (str): Path to the secrets file

    Returns:
        (dict): Dict containing secret data
    """

    with open( file_path, mode = 'r', encoding = 'utf-8' ) as f:
        return json.load( f )
