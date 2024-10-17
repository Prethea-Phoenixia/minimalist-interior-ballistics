from __future__ import annotations

import logging
from tkinter import Toplevel, filedialog
from tkinter.ttk import (Button, Entry, Frame, Label, LabelFrame, Scrollbar,
                         Treeview)
from typing import Optional, Tuple, Union

from ..charge import Propellant
from . import DEFAULT_ENTRY_WIDTH, DEFAULT_PAD
from .misc import tree_selected

logger = logging.getLogger(__name__)


class DefinePropellantWindow(Toplevel):
    def __init__(self, *args, basis: Optional[Propellant] = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Define Propellant")
        self.columnconfigure(1, weight=1)

        self.value_entries = tuple(
            self.add_label_entry_label_groups(i, v)
            for i, v in enumerate(
                [
                    ("Name", basis.name if basis else None, ""),
                    ("Description", basis.description if basis else None, ""),
                    ("Density", basis.density * 1e-3 if basis else None, "g/cm³"),
                    ("Force", basis.force * 1e-3 if basis else None, "J/g"),
                    ("Pressure Exponent", basis.pressure_exponent if basis else None, ""),
                    ("Covolume", basis.covolume * 1e3 if basis else None, "cm³/g"),
                    ("Adiabatic Index", basis.adiabatic_index if basis else None, ""),
                ]
            )
        )
        button = Button(self, text="Confirm", command=self.define_prop)
        button.grid(
            row=len(self.value_entries), column=0, columnspan=3, sticky="nsew", **DEFAULT_PAD
        )

        self.prop = None

    def define_prop(self):
        try:
            density, force, pressure_exponent, covolume, adiabatic_index = (
                float(e.get()) for e in self.value_entries[2:]
            )
            force *= 1000  # J/kg
            covolume /= 1000
            density *= 1000

            self.prop = Propellant(
                density=density,
                force=force,
                pressure_exponent=pressure_exponent,
                covolume=covolume,
                adiabatic_index=adiabatic_index,
                description=self.value_entries[1].get(),
                name=self.value_entries[0].get(),
            )
            self.destroy()

        except ValueError as e:
            logger.error(e)

    def add_label_entry_label_groups(
        self, row, values: Tuple[str, Optional[Union[int, float, str]], str]
    ) -> Entry:
        label_text, entry_value, unit_text = values
        Label(self, text=label_text).grid(row=row, column=0, sticky="nsew", **DEFAULT_PAD)
        e = Entry(self, width=DEFAULT_ENTRY_WIDTH)  # entry width is in characters
        e.delete(0, "end")
        e.insert(0, f"{entry_value}" if entry_value else "")
        e.grid(row=row, column=1, sticky="nsew", **DEFAULT_PAD)
        Label(self, text=unit_text).grid(row=row, column=2, sticky="nsew", **DEFAULT_PAD)
        return e


class PropellantFrame(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        cols = ("name", "desc", "ρ (g/cm³)", "f (J/g)", "n", "ɑ (cm³/g)", "γ")
        widths = (100, 400, 100, 100, 100, 100, 100)

        self.tree = Treeview(self, columns=cols, show="headings")

        vsb = Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=1, column=1, sticky="nsew", **DEFAULT_PAD)

        self.tree.config(yscrollcommand=vsb.set)

        for width, col in zip(widths, self.tree["columns"]):
            self.tree.heading(column=f"{col}", text=f"{col}", anchor="c")
            self.tree.column(column=f"{col}", width=width, minwidth=width, stretch=True, anchor="c")

        self.tree.grid(row=1, column=0, sticky="nsew", **DEFAULT_PAD)
        button_frame = LabelFrame(self, text="Operations")
        button_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", **DEFAULT_PAD)
        # for i in range(2):
        #     button_frame.columnconfigure(i, weight=1)

        # button_frame.column
        add_edit_button = Button(button_frame, text="Add/Edit", command=self.add_edit_prop)
        add_edit_button.grid(row=0, column=0, sticky="nsew")

        del_button = Button(button_frame, text="Delete", command=self.del_prop)
        del_button.grid(row=0, column=1, stick="nsew")

        load_button = Button(button_frame, text="Load from File", command=self.load_props)
        load_button.grid(row=0, column=2, sticky="nsew")

        self.props = {}

    def add_prop(self, prop: Propellant):
        pid = self.tree.insert(
            "",
            "end",
            values=(
                prop.name,
                prop.description,
                f"{prop.density * 1e-3:.3f}",
                f"{prop.force * 1e-3:.0f}",
                f"{prop.pressure_exponent:.3f}",
                f"{prop.covolume * 1e3:.3f}",
                f"{prop.adiabatic_index:.3f}",
            ),
        )
        self.props[pid] = prop

    @tree_selected
    def add_edit_prop(self, pid):

        dpw = DefinePropellantWindow(self, basis=self.props[pid] if pid else None)
        self.wait_window(dpw)
        prop = dpw.prop
        if prop:
            self.add_prop(prop)

    @tree_selected
    def del_prop(self, pid):
        if pid:
            self.props.pop(pid)
            self.tree.delete(pid)

    def load_props(self):
        try:
            file_name = filedialog.askopenfilename(
                parent=self,
                title="Load Propellant File",
                filetypes=[("Comma Separated Values", ".csv")],
            )
            if file_name:
                props = Propellant.from_csv_file(file_name)
                for prop in props:
                    self.add_prop(prop)
        except ValueError as e:
            logger.info(str(e))

    def get_props(self) -> Tuple[Propellant]:
        return tuple(self.props.values())
