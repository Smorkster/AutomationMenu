"""
Definition of a predefined, automatic, run sequence

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0.0
Created: 2025-11-20
"""

from __future__ import annotations

from dataclasses import dataclass
from automation_menu.models.sequencestep import SequenceStep


@dataclass
class Sequence:
    """ Define an automatic run sequence """

    description: str
    id: str
    name: str
    steps: list[ SequenceStep ]
    stop_on_error: bool


    def to_dict( self ) -> dict:
        """ Transform sequence to a dict

        Returns:
            (dict): Sequence as a dict
        """

        steps: list[ dict ] = []
        for step in self.steps:
            steps.append( step.to_dict() )

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stop_on_error': self.stop_on_error,
            'steps': steps
        }