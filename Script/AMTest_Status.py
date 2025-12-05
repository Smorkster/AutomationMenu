"""
Test status text API

:synopsis: Test status
:state: Prod
:disable_minimize_on_running:
:author: Smorkster (smorkster)
"""

import time
from automation_menu.api.script_api import clear_status, get_status, set_status

speed = 1
print( 'Setting status ''Test status''' )
set_status( text = 'Test status' )
time.sleep( speed )

print( 'Clearing status' )
clear_status()
time.sleep( speed )

print( 'Setting status ''Test status 2''' )
set_status( text = 'Test status 2' )
time.sleep( speed )

print( 'Appending status with ''appended''' )
set_status( text = 'appended', append = True )
time.sleep( speed )

print( 'Getting status' )
s = get_status()
print( f'Status got: { s }' )

time.sleep( speed )
