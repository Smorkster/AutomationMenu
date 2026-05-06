"""
Define widget references used by the sequence management UI.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter import BooleanVar, Canvas
from tkinter.ttk import Button, Checkbutton, Combobox, Entry, Frame, Label, Scrollbar, Treeview


class SequenceUi():
    """ Store widget references used by the sequence management UI."""

    def __init__(self) -> None:
        """ Initialize the sequence UI widget reference container."""

        pass

    stop_sequence_on_error_var: BooleanVar
    stop_step_on_error_var: BooleanVar

    step_input_window_id: int | None = None
    steps_list_input_window_id: int | None = None

    new_sequence_btn: Button
    edit_sequence_btn: Button
    run_sequence_btn: Button
    add_step_btn: Button
    save_sequence_btn: Button
    delete_sequence_btn: Button
    abort_sequence_edit_btn: Button

    steps_list_container_canvas: Canvas
    step_form_container_canvas: Canvas

    stop_sequence_on_error_field: Checkbutton

    step_script_list: Combobox

    name_field: Entry
    description_field: Entry

    sequence_ops: Frame
    sequence_form: Frame
    steps_display_frame: Frame
    display_container: Frame
    steps_container: Frame
    step_form: Frame
    step_input_container: Frame
    step_input_frame: Frame
    main_frame: Frame
    input_params_frame: Frame | None = None

    step_input_title: Label

    container_scrollbar: Scrollbar

    sequence_list: Treeview
