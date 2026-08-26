"""
Define widget references used by the operation buttons for persistent GUI scripts.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter.ttk import Button, Frame


class OpPersistentButtonsUi():
    """ Store widget references used by the operation buttons UI."""

    def __init__( self ) -> None:
        """ Initialize the operation buttons UI widget reference container."""

        pass

    btn_show: Button
    btn_resume_script: Button
    btn_pause_script: Button
    btn_stop_script: Button
    btn_force_stop_script: Button

    op_buttons_frame: Frame
