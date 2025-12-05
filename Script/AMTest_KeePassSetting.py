"""
Test API to retrieve KeePass setting

:synopsis: Test KeePass setting
:state: Prod
:disable_minimize_on_running:
:author: Smorkster (smorkster)
"""

from automation_menu.api.script_api import get_keepass_shortcut


sc = get_keepass_shortcut()

print( sc )