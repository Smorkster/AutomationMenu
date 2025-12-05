"""
2:nd test sending input to script

:synopsis: 2:nd test input
:state: Prod
:author: Smorkster (smorkster)
:param o: Test o [ 'A', 'B' ]
:param t: Test long input parameter description that should wrap to a new line in the input labelframe
:param oo: Test o (default: Testing)
:param ooo: Test o (required)
"""

import sys


#input_count = len( sys.argv ) - 1
#print( f'Got { input_count } input arguments' )

i = 0
for arg in sys.argv[ 1 : ]:
    print( f'Args { i }: { arg }' )
    i += 1

