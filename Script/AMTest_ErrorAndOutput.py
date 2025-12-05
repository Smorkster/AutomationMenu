""" ScriptInfo
# Description - Test message written to stderr then stdout
# Synopsis - Test error output and output
# State - Prod
# DisableMinimizeOnRunning
# Author - Smorkster (smorkster)
ScriptInfoEnd """


from sys import stderr
import time

stderr.writelines( 'Error testing' )
stderr.flush()
time.sleep( 4 )
print( 'Ordinary testing' )
