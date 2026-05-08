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
    abort_add_sequence_step: Callable
    abort_sequence_edit: Callable
    add_sequence_step: Callable
    clear_sequence_info: Callable
    clear_sequence_steps: Callable
    create_new_sequence: Callable
    delete_sequence: Callable
    edit_sequence: Callable
    get_selected_sequence_id: Callable
    on_listbox_click: Callable
    on_info_entry_changed: Callable
    on_info_checkbutton_changed: Callable
    on_step_click: Callable
    on_step_script_selected: Callable
    populate_sequence_form: Callable
    populate_sequence_steps: Callable
    remove_sequence_step: Callable
    run_sequence: Callable
    save_sequence: Callable

    # Inhouse
    list_sequences: Callable
    save_edited_step: Callable
    show_step_form: Callable
    show_step_form_input: Callable

    get_script_list: Callable
