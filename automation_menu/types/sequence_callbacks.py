"""
Define typed callback references used by the sequence UI.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from dataclasses import dataclass
from typing import Callable


@dataclass
class SequenceCallbacks:
    """ Store callbacks used by sequence UI construction and interaction."""

    # In controller
    clear_sequence_info: Callable
    clear_sequence_steps: Callable
    get_selected_sequence_id: Callable
    on_listbox_click: Callable
    on_step_click: Callable
    on_step_script_selected: Callable
    populate_sequence_form: Callable
    populate_sequence_steps: Callable
    create_new_sequence: Callable
    edit_sequence: Callable
    run_sequence: Callable
    add_sequence_step: Callable
    save_sequence: Callable
    delete_sequence: Callable
    abort_sequence_edit: Callable
    remove_sequence_step: Callable
    abort_add_sequence_step: Callable

    # Inhouse
    list_sequences: Callable
    show_step_form: Callable
    show_step_form_input: Callable
    save_edited_step: Callable

    get_script_list: Callable
