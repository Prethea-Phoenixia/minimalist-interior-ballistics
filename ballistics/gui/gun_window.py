from __future__ import annotations

import logging
from tkinter import Toplevel, filedialog
from tkinter.ttk import Button, Entry, Frame, Label, LabelFrame, Treeview
from typing import Callable, Optional, Tuple, Union

from ..gun import Gun
from . import DEFAULT_ENTRY_WIDTH, DEFAULT_PAD

logger = logging.getLogger(__name__)


class DefineGunWindow(Toplevel):
    def __init__(self, *args, basis: Optional[Gun] = None, **kwargs):
        super().__init__(*args, **kwargs)
        # self.master = master

        self.title("Define Gun")
        self.columnconfigure(1, weight=1)

        self.value_entries = tuple(
            self.add_label_entry_label_groups(i, v)
            for i, v in enumerate(
                [
                    ("Cross Section", basis.cross_section if basis else None, "dm²"),
                    ("Shot Mass", basis.shot_mass if basis else None, "kg"),
                    ("Charge Mass", basis.charge_mass if basis else None, "kg"),
                    ("Chamber Volume", basis.charge_volume if basis else None, "L"),
                    ("Loss Fraction", basis.loss_fraction if basis else None, "%"),
                    ("Start Pressure", basis.start_pressure if basis else None, "MPa"),
                ]
            )
        )

        button = Button(self, text="Confirm", command=self.define_gun)
        button.grid(
            row=len(self.value_entries), column=0, columnspan=3, sticky="nsew", **DEFAULT_PAD
        )

        self.gun = None

    def add_label_entry_label_groups(
        self, row, values: Tuple[str, Optional[Union[int, float]], str]
    ) -> Entry:
        label_text, entry_value, unit_text = values
        Label(self, text=label_text).grid(row=row, column=0, sticky="nsew", **DEFAULT_PAD)
        e = Entry(self, width=DEFAULT_ENTRY_WIDTH)  # entry width is in characters
        e.delete(0, "end")
        e.insert(0, f"{entry_value}" if entry_value else "")
        e.grid(row=row, column=1, sticky="nsew", **DEFAULT_PAD)
        Label(self, text=unit_text).grid(row=row, column=2, sticky="nsew", **DEFAULT_PAD)
        return e

    def define_gun(self):
        pass


class GunFrame(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=8)

        self.tree = Treeview(self)
        self.tree.grid(row=0, column=0, sticky="nsew")

        self.ops = GunOpsFrame(self, add_gun_func=self.add_gun)
        self.ops.grid(row=1, column=0, sticky="nsew")

        overview_frame = OverviewPane(self)
        overview_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")

        self.guns = {}

    def add_gun(self):
        dgw = DefineGunWindow(self)
        self.wait_window(dgw)

        gun = dgw.get_gun()

        gid = self.tree.insert("", "end", text="Gun")
        self.guns[gid] = gun


class GunOpsFrame(LabelFrame):
    def __init__(self, *args, text="Operations", add_gun_func: Callable, **kwargs):
        super().__init__(*args, text=text, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.add_button = Button(self, text="Add Gun", command=add_gun_func)
        self.add_button.grid(row=0, column=0, sticky="nsew")


class OverviewPane(LabelFrame):
    def __init__(self, *args, text="Overview", **kwargs):
        super().__init__(*args, text=text, **kwargs)

        self.label = Label(self, text="testy")
        self.label.grid(row=0, column=0, sticky="nsew")
