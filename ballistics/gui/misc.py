from tkinter import Entry, Label
from typing import Optional, Tuple, Union

from . import DEFAULT_ENTRY_WIDTH, DEFAULT_PAD


def tree_selected(func):
    def wrapped(pf, *args, **kwargs):
        return func(pf, *args, tvid=pf.tree.focus(), **kwargs)

    return wrapped


def add_label_entry_label_groups(
    frame, row, values: Tuple[str, Optional[Union[int, float, str]], str]
) -> Entry:
    label_text, entry_value, unit_text = values
    Label(frame, text=label_text, anchor="e").grid(row=row, column=0, sticky="nsew", **DEFAULT_PAD)
    e = Entry(frame, width=DEFAULT_ENTRY_WIDTH)  # entry width is in characters
    e.delete(0, "end")
    e.insert(0, f"{entry_value}" if entry_value else "")
    e.grid(row=row, column=1, sticky="nsew", **DEFAULT_PAD)
    Label(frame, text=unit_text, anchor="w").grid(row=row, column=2, sticky="nsew", **DEFAULT_PAD)
    return e
