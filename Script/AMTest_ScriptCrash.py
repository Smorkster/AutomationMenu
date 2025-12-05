"""
Test script crash

:synopsis: Test script crash
:state: Prod
:disable_minimize_on_running:
:author: Smorkster (smorkster)
"""

print( 'Test script crash' )

raise Exception( 'Test crash' )

print( 'This shouldnt print' )