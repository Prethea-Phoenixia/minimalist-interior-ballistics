from __future__ import annotations

import logging
from tkinter import StringVar, Text, Toplevel
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import (Button, Combobox, Frame, Label, LabelFrame, Notebook,
                         Scrollbar, Treeview)
from typing import Callable, Optional, Tuple

from ..charge import Charge, Propellant
from ..form_function import FormFunction, MultiPerfShape
from ..gun import Gun
from . import DEFAULT_PAD
from .misc import add_label_entry_label_groups, tree_selected

logger = logging.getLogger(__name__)


class DefineGunWindow(Toplevel):
    def __init__(
        self,
        *args,
        basis: Optional[Gun] = None,
        get_props_func: Callable[[], Tuple[Propellant]],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # self.master = master

        self.title("Define Gun")
        self.columnconfigure(1, weight=1)

        self.value_entries = tuple(
            add_label_entry_label_groups(self, i, *v)
            for i, v in enumerate(
                [
                    ("Name", "", basis.name + " (copy)" if basis else None),
                    ("Cross Section", "dm²", basis.cross_section * 1e2 if basis else None),
                    ("Shot Mass", "kg", basis.shot_mass if basis else None),
                    ("Charge Mass", "kg", basis.charge_mass if basis else None),
                    ("Chamber Volume", "L", basis.chamber_volume * 1e3 if basis else None),
                    ("Loss Fraction", "%", basis.loss_fraction * 1e2 if basis else None),
                    ("Start Pressure", "MPa", basis.start_pressure * 1e-6 if basis else None),
                    ("Reduced Burn Rate", "/s", basis.charge.reduced_burnrate if basis else None),
                ]
            )
        )

        Label(self, text="Propellant").grid(
            row=len(self.value_entries), column=0, sticky="nsew", **DEFAULT_PAD
        )

        self.props = get_props_func()
        self.prop_combo = Combobox(self, state="readonly", values=tuple(p.name for p in self.props))
        self.prop_combo.grid(
            row=len(self.value_entries), column=1, columnspan=2, sticky="nsew", **DEFAULT_PAD
        )

        description_frame = LabelFrame(self, text="Description")
        description_frame.grid(
            row=0, column=3, rowspan=len(self.value_entries) + 3, sticky="nsew", **DEFAULT_PAD
        )
        description_frame.columnconfigure(0, weight=1)
        description_frame.rowconfigure(0, weight=1)

        self.text = Text(description_frame, width=40, height=10, wrap="none")
        self.text.grid(row=0, column=0, sticky="nsew", **DEFAULT_PAD)
        self.text.insert("end", basis.description if basis else "")

        self.form_function_frame = FormFunctionFrame(self)
        self.form_function_frame.grid(
            row=len(self.value_entries) + 1, column=0, columnspan=3, sticky="nsew", **DEFAULT_PAD
        )

        button = Button(self, text="Confirm", command=self.define_gun)
        button.grid(
            row=len(self.value_entries) + 2, column=0, columnspan=3, sticky="nsew", **DEFAULT_PAD
        )

        self.gun = None

    def get_prop(self) -> Optional[Propellant]:
        i = self.prop_combo.current()
        if i == -1:
            raise ValueError("no propellant has been selected.")
        else:
            return self.props[i]

    def define_gun(self):
        try:
            name = self.value_entry[0].get()
            (
                cross_section,
                shot_mass,
                charge_mass,
                chamber_volume,
                loss_fraction,
                start_pressure,
                reduced_burnrate,
            ) = (float(e.get()) for e in self.value_entries[1:])

            cross_section *= 1e-2  # dm^2 to m^2
            chamber_volume *= 1e-3  # L to m^3
            start_pressure *= 1e6  # MPa to Pa
            loss_fraction *= 1e-2  # % to 1

            charge = Charge.from_propellant(
                reduced_burnrate=reduced_burnrate,
                propellant=self.get_prop(),
                form_function=self.form_function_frame.get_form_function(),
            )

            self.gun = Gun(
                name=name,
                description=self.text.get("1.0", "end-1c"),
                cross_section=cross_section,
                shot_mass=shot_mass,
                charge=charge,
                charge_mass=charge_mass,
                chamber_volume=chamber_volume,
                loss_fraction=loss_fraction,
                start_pressure=start_pressure,
            )
            self.destroy()

        except (ValueError, IndexError) as e:
            logger.error(e)


class GunFrame(Frame):
    def __init__(self, *args, get_props_func=Callable[[], Tuple[Propellant]], **kwargs):
        self.get_props_func = get_props_func
        super().__init__(*args, **kwargs)

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(2, weight=8)

        self.tree = Treeview(self, show="tree")

        vsb = Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=1, column=1, sticky="nsew", **DEFAULT_PAD)

        self.tree.config(yscrollcommand=vsb.set)

        self.tree.grid(row=1, column=0, sticky="nsew", **DEFAULT_PAD)

        self.overview_frame = LabelFrame(self, text="Overview")
        self.overview_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", **DEFAULT_PAD)

        self.guns = {}

    @tree_selected
    def add_edit_gun(self, tvid):
        dgw = DefineGunWindow(
            self, basis=self.guns[tvid] if tvid else None, get_props_func=self.get_props_func
        )
        self.wait_window(dgw)
        gun = dgw.gun
        if gun:
            self.add_gun(gun)

    def add_gun(self, gun: Gun):
        gid = self.tree.insert("", "end", text=gun.name)
        self.guns[gid] = gun

    @tree_selected
    def del_gun(self, tvid):
        if tvid:
            self.guns.pop(tvid)
            self.tree.delete(tvid)


class FormFunctionFrame(LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, text="Geometry", **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.notebook = Notebook(self)
        self.notebook.enable_traversal()
        self.notebook.grid(row=0, column=0, sticky="nsew", **DEFAULT_PAD)

        self.notebook.columnconfigure(0, weight=1)
        self.notebook.rowconfigure(0, weight=1)

        # this order is depended upon for correct functioning of the program.
        self.add_non_perf()
        self.add_single_perf()
        self.add_multi_perf()

    def prepare_tab(self, tab_text: str) -> Frame:
        tab_frame = Frame(self.notebook)
        tab_frame.grid(row=0, column=0, sticky="nsew", **DEFAULT_PAD)
        tab_frame.columnconfigure(1, weight=1)
        self.notebook.add(tab_frame, text=tab_text)
        return tab_frame

    def add_non_perf(self):
        non_perf_frame = self.prepare_tab("Non Perf.")

        self.non_perf_entries = tuple(
            add_label_entry_label_groups(non_perf_frame, i, *v)
            for i, v in enumerate([("Length", "mm"), ("Width", "mm"), ("Height", "mm")])
        )

    def add_single_perf(self):
        single_perf_frame = self.prepare_tab("Single Perf.")

        self.single_perf_entries = tuple(
            add_label_entry_label_groups(single_perf_frame, i, *v)
            for i, v in enumerate([("Arch Width", "mm"), ("Height", "mm")])
        )

    def add_multi_perf(self):
        multi_perf_frame = self.prepare_tab("Muliple Perf.")

        self.multi_perf_shapes = tuple(mps for mps in MultiPerfShape)
        self.multi_perf_combo = Combobox(
            multi_perf_frame,
            state="readonly",
            values=tuple(shape.describe() for shape in self.multi_perf_shapes),
        )
        self.multi_perf_combo.grid(row=0, column=0, columnspan=3, sticky="nsew", **DEFAULT_PAD)

        self.multi_perf_entries = tuple(
            add_label_entry_label_groups(multi_perf_frame, i, *v)
            for i, v in enumerate(
                [
                    ("Arch Width", "mm"),
                    ("Perforation Diameter", "mm"),
                    ("Height", "mm"),
                ],
                1,
            )
        )

    def get_form_function(self) -> Optional[FormFunction]:
        tab_index = self.notebook.index(self.notebook.select())

        # try:
        if tab_index == 0:
            length, width, height = (float(e.get()) for e in self.non_perf_entries)
            return FormFunction.non_perf(length=length, width=width, height=height)

        elif tab_index == 1:
            arch_width, height = (float(e.get()) for e in self.single_perf_entries)
            return FormFunction.single_perf(arch_width=arch_width, height=height)

        elif tab_index == 2:
            arch_width, perforation_diameter, height = (
                float(e.get()) for e in self.multi_perf_entries
            )
            return FormFunction.multi_perf(
                arch_width=arch_width,
                perforation_diameter=perforation_diameter,
                height=height,
                shape=self.get_shape(),
            )

        return None

    def get_shape(self):
        i = self.multi_perf_combo.current()
        if i == -1:
            raise ValueError("no shape selected")
        else:
            return self.multi_perf_shapes[i]


class OverviewFrame(LabelFrame):
    def __init__(self, *args, text="Overview", **kwargs):
        super().__init__(*args, text=text, **kwargs)
