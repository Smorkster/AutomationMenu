"""
Placeholder ScriptInfo for scripts that have not been loaded

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from dataclasses import dataclass
from pathlib import Path

from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.scriptmetadata import ScriptMetadata
from automation_menu.utils.localization import _

@dataclass
class ScriptInfoNotLoaded( ScriptInfo ):
    """ A placeholder object for a script that hasn't been loaded """

    def __init__( self, fullpath: Path ) -> None:
        """ Creates an empty placeholder ScriptInfo object

        Args:
            fullpath (Path): Path to script file
        """

        placeholder_synopsis: str = _( 'Script not loaded' )
        placeholder_description: str = _( 'Placeholder for a script referenced, but not currently loaded' )
        placeholder_meta: ScriptMetadata = ScriptMetadata( synopsis = placeholder_synopsis,
                                                          author = 'AutomationMenu',
                                                          description = placeholder_description )

        super().__init__( fullpath = fullpath,
                         filename = fullpath.name,
                         scriptmeta = placeholder_meta )
