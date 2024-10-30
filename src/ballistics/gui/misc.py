from tkinter import StringVar, Toplevel
from tkinter.ttk import Entry, Frame, Label
from typing import Optional, Tuple, Union

from . import DEFAULT_ENTRY_WIDTH, DEFAULT_PAD


def tree_selected(treeattr: str = "tree"):
    def selected(func):
        def wrapped(pf, *args, **kwargs):
            return func(pf, *args, tvid=getattr(pf, treeattr).focus(), **kwargs)

        return wrapped

    return selected


def add_frame_group(parent, values) -> Tuple[Frame, Tuple[StringVar, ...]]:
    group_frame = Frame(parent)
    group_frame.columnconfigure(1, weight=1)
    return group_frame, tuple(
        add_label_entry_label_group(group_frame, i, *v) for i, v in enumerate(values)
    )


def add_label_entry_label_group(
    frame: Union[Frame, Toplevel],
    row: int,
    label_text: str,
    unit_text: str,
    entry_value: Optional[Union[float, str]] = None,
    disabled: bool = False,
) -> StringVar:
    Label(frame, text=label_text, anchor="e").grid(row=row, column=0, sticky="nsew", **DEFAULT_PAD)
    sv = StringVar(frame)
    sv.set(value=f"{entry_value}" if entry_value else "")
    Entry(
        frame,
        width=DEFAULT_ENTRY_WIDTH,
        textvariable=sv,
        state="disabled" if disabled else "normal",
    ).grid(row=row, column=1, sticky="nsew", **DEFAULT_PAD)

    Label(frame, text=unit_text, anchor="w").grid(row=row, column=2, sticky="nsew", **DEFAULT_PAD)
    return sv
