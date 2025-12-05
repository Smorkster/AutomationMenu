"""
Test normal output

To get text to be displayed in the AutomationMenu
output textbox, use print() for the text to be sent to stdout

:synopsis: Test output
:state: Prod
:author: Smorkster (smorkster)
"""

import time

for _ in range( 5 ):
    print( 'Test output' )
    time.sleep( 0.5 )

timeout = 2
print( f'Taking timeout { timeout }' )
time.sleep( timeout )

for _ in range( 5 ):
    print( 'Test output 2' )
    time.sleep( 0.5 )