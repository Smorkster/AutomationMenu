"""
Test working with the progressbar

:synopsis: Test progressbar
:state: Prod
:disable_minimize_on_running:
:author: Smorkster (smorkster)
"""


from sys import stderr
import time

from automation_menu.api import set_progress, indeterminate_progress, determinate_progress, show_progress

print( 'Show progress' )
show_progress()
indeterminate_progress()
time.sleep( 2 )
print( 'Determinate progress + 30%' )
determinate_progress()
set_progress( percent = 30 )

time.sleep( 4 )
indeterminate_progress()
time.sleep( 0.5 )
determinate_progress()
print( 'Determinate + 70%' )
set_progress( percent = 70 )

time.sleep( 2 )
set_progress( percent = 100 )
