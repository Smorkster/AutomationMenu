"""
Definition of a User object

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-31
"""

import os
import re
import ldap3
import ldap3.abstract
import ldap3.abstract.entry

class User:
    """ Class to hold user information from Active Directory """
    def __init__( self, ad_object: ldap3.abstract.entry.Entry = None ) -> None:
        """ Initialize User with an Active Directory object """

        self.UserId:str = os.getenv( key = 'USERNAME' ,default = 'DefaultUser' )
        self.AdObject: ldap3.abstract.entry.Entry = ad_object


    def member_of( self, group_to_check: str ) -> bool:
        """ Check if the user is a member of a specific group """

        for g in self.AdObject.memberof:
            if re.search( group_to_check , g ):
                return True

        return False
