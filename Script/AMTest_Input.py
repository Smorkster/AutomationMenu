"""
Test sending input to script

:synopsis: Test input
:state: Prod
:author: Smorkster (smorkster)
:param t: Test
:param tt: Test (default: Testing)
:param ttt: Test (required)
:param tttt: Test (required) (default: Test3)
:param a: Test
:param aa: Test (default: Testing)
:param aaa: Test (required)
:param aaaa: Test (required) (default: Test3)
:param s: Test
:param ss: Test (default: Testing)
:param sss: Test (required)
:param ssss: Test (required) (default: Test3)
:param t: Test
:param tt: Test (default: Testing)
:param ttt: Test (required)
:param tttt: Test (required) (default: Test3)
:param a: Test
:param aa: Test (default: Testing)
:param aaa: Test (required)
:param aaaa: Test (required) (default: Test3)
:param s: Test
:param ss: Test (default: Testing)
:param sss: Test (required)
:param ssss: Test (required) (default: Test3)
:param t: Test
:param tt: Test (default: Testing)
:param ttt: Test (required)
:param tttt: Test (required) (default: Test3)
:param a: Test
:param aa: Test (default: Testing)
:param aaa: Test (required)
:param aaaa: Test (required) (default: Test3)
:param s: Test
:param ss: Test (default: Testing)
:param sss: Test (required)
:param ssss: Test (required) (default: Test3)
"""

import sys
import time


input_count = len( sys.argv ) - 1
print( f'Got { input_count } input arguments' )

i = 0
for arg in sys.argv[ 1 : ]:
    print( f'Args { i }: { arg }' )
    time.sleep( 0.5 )
    i += 1

