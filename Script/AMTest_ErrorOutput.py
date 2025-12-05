""" ScriptInfo
# Description - Test message written to stderr
# Synopsis - Test error output
# State - Dev
# DisableMinimizeOnRunning
# Author - Smorkster (smorkster)
ScriptInfoEnd """

from sys import stderr


print( 'Test Error output' )

stderr.write( 'Error testing' )
stderr.flush()