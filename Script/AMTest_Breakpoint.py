""" ScriptInfo
# Description - Test identification of breakpoint in script code
# Synopsis - Test breakpoint
# State - Prod
# DisableMinimizeOnRunning
# Author - Smorkster (smorkster)
ScriptInfoEnd """

from sys import stderr

print( 'Before breakpoint' )
breakpoint()
print( 'After breakpoint' )