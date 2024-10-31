from __future__ import annotations

import logging
from tkinter import Toplevel, filedialog
from tkinter.ttk import Button, Frame, LabelFrame, Scrollbar, Treeview
from typing import Optional, Tuple

from ..charge import Propellant
from . import DEFAULT_PAD, DEFAULT_TEXT_HEIGHT, DEFAULT_TEXT_WIDTH
from .misc import add_label_entry_label_group, tree_selected
# from tkinter.scrolledtext import ScrolledText
from .themed_scrolled_text import ThemedScrolledText as ScrolledText

logger = logging.getLogger(__name__)


class DefinePropellantWindow(Toplevel):
    def __init__(self, parent, *args, basis: Optional[Propellant] = None, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.resizable(False, False)
        self.transient(parent)

        self.title("Define Propellant (* fields are optional)")
        self.columnconfigure(0, weight=1)

        self.value_entries = tuple(
            add_label_entry_label_group(self, i, *v)
            for i, v in enumerate(
                [
                    ("Name", "", basis.name + " (copy)" if basis else None),
                    ("Density", "g/cm³", basis.density * 1e-3 if basis else None),
                    ("Force", "J/g", basis.force * 1e-3 if basis else None),
                    (
                        "Pressure Exponent",
                        "",
                        basis.pressure_exponent if basis else None,
                    ),
                    ("Covolume", "cm³/g", basis.covolume * 1e3 if basis else None),
                    ("Adiabatic Index", "", basis.adiabatic_index if basis else None),
                    (
                        "Burn Rate Coefficient*",
                        "(nm/s)/Paⁿ",
                        (
                            basis.burn_rate_coefficient * 1e9
                            if basis and basis.burn_rate_coefficient
                            else None
                        ),
                    ),
                ]
            )
        )

        description_frame = LabelFrame(self, text="Description")
        description_frame.grid(
            row=0,
            column=3,
            rowspan=len(self.value_entries) + 1,
            sticky="nsew",
            **DEFAULT_PAD,
        )
        description_frame.columnconfigure(0, weight=1)
        description_frame.rowconfigure(0, weight=1)

        self.text = ScrolledText(
            description_frame,
            width=DEFAULT_TEXT_WIDTH,
            height=DEFAULT_TEXT_HEIGHT,
            # wrap="none",
        )
        self.text.grid(row=0, column=0, sticky="nsew", **DEFAULT_PAD)
        self.text.insert("end", basis.description if basis else "")

        button = Button(self, text="Confirm", command=self.define_prop)
        button.grid(
            row=len(self.value_entries),
            column=0,
            columnspan=3,
            sticky="nsew",
            **DEFAULT_PAD,
        )

        self.prop = None

    def define_prop(self):
        try:
            density, force, pressure_exponent, covolume, adiabatic_index = (
                float(sv.get()) for sv in self.value_entries[1:-1]
            )
            brcs = self.value_entries[-1].get()
            burn_rate_coefficient = float(brcs) * 1e-9 if brcs else None

            force *= 1e3  # J/kg
            covolume *= 1e-3
            density *= 1e3

            self.prop = Propellant(
                density=density,
                force=force,
                pressure_exponent=pressure_exponent,
                covolume=covolume,
                adiabatic_index=adiabatic_index,
                description=self.text.get("1.0", "end-1c"),
                name=self.value_entries[0].get(),
                burn_rate_coefficient=burn_rate_coefficient,
            )
            self.destroy()

        except ValueError as e:
            logger.warning(e)


class PropellantFrame(Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        cols = ("name", "ρ g/cm³", "f J/g", "n", "ɑ cm³/g", "γ", "u (nm/s)/Paⁿ")
        widths = (200, 100, 100, 100, 100, 100, 200)

        self.tree = Treeview(self, columns=cols, show="headings", selectmode="browse")
        vsb = Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=1, column=1, sticky="nsew")
        self.tree.config(yscrollcommand=vsb.set)

        for width, col in zip(widths, self.tree["columns"]):
            self.tree.heading(column=f"{col}", text=f"{col}", anchor="c")
            self.tree.column(column=f"{col}", width=width, minwidth=width, stretch=True, anchor="c")

        self.tree.grid(row=1, column=0, sticky="nsew")

        overview_frame = LabelFrame(self, text="Overview")
        overview_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", **DEFAULT_PAD)
        overview_frame.rowconfigure(0, weight=1)
        overview_frame.columnconfigure(0, weight=1)
        self.overview_text = ScrolledText(
            overview_frame,
            state="disabled",
            width=DEFAULT_TEXT_WIDTH,
            height=DEFAULT_TEXT_HEIGHT,
            # wrap="none",
        )
        self.overview_text.grid(row=0, column=0, sticky="nsew", **DEFAULT_PAD)

        self.tree.bind("<<TreeviewSelect>>", self.set_overview)
        self.props = {}

    @tree_selected()
    def set_overview(self, *args, tvid, **kwargs):
        self.overview_text.config(state="normal")
        self.overview_text.delete(1.0, "end")
        if tvid:
            self.overview_text.insert("insert", self.props[tvid].description)
        self.overview_text.config(state="disabled")

    def add_prop(self, prop: Propellant):
        tvid = self.tree.insert(
            parent="",
            index="end",
            values=(
                prop.name,
                f"{prop.density * 1e-3:.3f}",
                f"{prop.force * 1e-3:.0f}",
                f"{prop.pressure_exponent:.3f}",
                f"{prop.covolume * 1e3:.3f}",
                f"{prop.adiabatic_index:.3f}",
                (
                    f"{prop.burn_rate_coefficient * 1e9:.3g}"
                    if prop.burn_rate_coefficient
                    else "N/A"
                ),
            ),
        )
        self.props[tvid] = prop

    @tree_selected()
    def add_edit_prop(self, tvid):
        dpw = DefinePropellantWindow(self, basis=self.props[tvid] if tvid else None)
        self.wait_window(dpw)
        prop = dpw.prop
        if prop:
            self.add_prop(prop)

    @tree_selected()
    def del_prop(self, tvid):
        if tvid:
            self.props.pop(tvid)
            self.tree.delete(tvid)

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
            logger.warning(e)

    def get_props(self) -> Tuple[Propellant]:
        return tuple(self.props.values())
