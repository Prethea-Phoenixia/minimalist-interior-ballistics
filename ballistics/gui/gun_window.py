from __future__ import annotations

import logging
from tkinter import Toplevel
from tkinter.filedialog import askopenfilename
from tkinter.ttk import (Button, Combobox, Frame, Label, LabelFrame, Notebook,
                         Scrollbar, Treeview)
from typing import Callable, Optional, Tuple

from ..charge import Charge, Propellant
from ..form_function import FormFunction, MultiPerfShape
from ..gun import Gun
from . import DEFAULT_PAD, DEFAULT_TEXT_HEIGHT, DEFAULT_TEXT_WIDTH
from .misc import add_frame_group, add_label_entry_label_group, tree_selected
# from tkinter.scrolledtext import ScrolledText
from .themed_scrolled_text import ThemedScrolledText as ScrolledText

logger = logging.getLogger(__name__)


class DefineGunWindow(Toplevel):
    def __init__(
        self,
        parent,
        *args,
        basis: Optional[Gun] = None,
        get_props_func: Callable[[], Tuple[Propellant]],
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)

        self.resizable(False, False)
        self.transient(parent)

        self.title("Define Gun")
        self.columnconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)

        self.value_entries = tuple(
            add_label_entry_label_group(self, i, *v)
            for i, v in enumerate(
                [
                    ("Name", "", basis.name + " (copy)" if basis else None),
                    ("Cross Section", "dm²", basis.cross_section * 1e2 if basis else None),
                    ("Shot Mass", "kg", basis.shot_mass if basis else None),
                    ("Charge Mass", "kg", basis.charge_mass if basis else None),
                    ("Chamber Volume", "L", basis.chamber_volume * 1e3 if basis else None),
                    ("Loss Fraction", "%", basis.loss_fraction * 1e2 if basis else None),
                    ("Start Pressure", "MPa", basis.start_pressure * 1e-6 if basis else None),
                    (
                        "Reduced Burn Rate",
                        "/ns",
                        basis.charge.reduced_burnrate * 1e9 if basis else None,
                    ),
                ]
            )
        )

        prop_frame = LabelFrame(self, text="Propellant")
        prop_frame.grid(
            row=len(self.value_entries), column=0, columnspan=3, sticky="nsew", **DEFAULT_PAD
        )
        prop_frame.columnconfigure(0, weight=1)

        self.props = get_props_func()
        self.prop_combo = Combobox(
            prop_frame, state="readonly", values=tuple(p.name for p in self.props)
        )
        self.prop_combo.grid(row=0, column=0, sticky="nsew", **DEFAULT_PAD)

        self.form_function_frame = FormFunctionFrame(self)
        self.form_function_frame.grid(
            row=len(self.value_entries) + 1, column=0, columnspan=3, sticky="nsew", **DEFAULT_PAD
        )

        button = Button(self, text="Confirm", command=self.define_gun)
        button.grid(
            row=len(self.value_entries) + 2, column=0, columnspan=3, sticky="nsew", **DEFAULT_PAD
        )

        description_frame = LabelFrame(self, text="Description")
        description_frame.grid(
            row=0, column=3, rowspan=len(self.value_entries) + 3, sticky="nsew", **DEFAULT_PAD
        )
        description_frame.columnconfigure(0, weight=1)
        description_frame.rowconfigure(0, weight=1)

        self.text = ScrolledText(
            description_frame, width=DEFAULT_TEXT_WIDTH, height=DEFAULT_TEXT_HEIGHT, wrap="none"
        )
        self.text.grid(row=0, column=0, sticky="nsew", **DEFAULT_PAD)
        self.text.insert("end", basis.description if basis else "")

        self.gun = None

    def get_prop(self) -> Optional[Propellant]:
        i = self.prop_combo.current()
        if i == -1:
            raise ValueError("no propellant has been selected.")
        else:
            return self.props[i]

    def define_gun(self):
        try:
            name = self.value_entries[0].get()
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
            reduced_burnrate *= 1e-9  # ns to s

            prop = self.get_prop()
            ff = self.form_function_frame.get_form_function()
            # the charge name is automatically generated.
            charge = Charge.from_propellant(
                name=" ".join((prop.name, ff.name)),
                description=ff.description,
                reduced_burnrate=reduced_burnrate,
                propellant=prop,
                form_function=ff,
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

        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(3, weight=8)

        self.tree = Treeview(self, show="tree", selectmode="browse")
        vsb = Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, rowspan=3, sticky="nsew")
        self.tree.config(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, rowspan=3, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.set_overview)

        overview_frame = self.add_overview_frame()
        overview_frame.grid(row=0, column=2, columnspan=2, sticky="nsew", **DEFAULT_PAD)

        derived_frame = self.add_derived_frame()
        derived_frame.grid(row=1, column=2, sticky="nsew", **DEFAULT_PAD)

        control_frame = self.add_control_frame()
        control_frame.grid(row=1, column=3, stick="nsew", **DEFAULT_PAD)

        states_frame = StatesFrame(self)
        states_frame.grid(row=2, column=2, columnspan=2, stick="nsew", **DEFAULT_PAD)

        self.guns = {}

    def add_control_frame(self) -> LabelFrame:
        control_frame = LabelFrame(self, text="Control")

        Label(control_frame, text="To Length:").grid(row=0, column=0, stick="nsew", **DEFAULT_PAD)
        Label(control_frame, text="To Velocity:").grid(row=1, column=0, stick="nsew", **DEFAULT_PAD)

        return control_frame

    def add_overview_frame(self) -> LabelFrame:
        overview_frame = LabelFrame(self, text="Overview")

        overview_frame.columnconfigure(0, weight=1)
        overview_frame.columnconfigure(1, weight=1)
        overview_frame.columnconfigure(2, weight=1)
        overview_frame.columnconfigure(3, weight=1)

        ov_top_frame, self.ov_top_params = add_frame_group(
            overview_frame, ((v, "", None, True) for v in ("Charge Name", "Charge Desc."))
        )
        ov_top_frame.grid(row=0, column=1, columnspan=2, sticky="nsew", **DEFAULT_PAD)

        ov_left_frame, self.ov_left_params = add_frame_group(
            overview_frame,
            (
                (*v, None, True)
                for v in (("Cross Section", "dm²"), ("Shot Mass", "kg"), ("Charge Mass", "kg"))
            ),
        )
        ov_left_frame.grid(row=1, column=1, stick="nsew", **DEFAULT_PAD)

        ov_mid_frame, self.ov_mid_params = add_frame_group(
            overview_frame,
            (
                (*v, None, True)
                for v in (("Chamber Vol.", "L"), ("Start Pressure", "MPa"), ("Loss Fraction", "%"))
            ),
        )
        ov_mid_frame.grid(row=1, column=2, stick="nsew", **DEFAULT_PAD)

        ov_right_frame, self.ov_right_params = add_frame_group(
            overview_frame,
            (
                (*v, None, True)
                for v in (("χ", ""), ("λ", ""), ("μ", ""), ("Zₖ", ""), ("u/e", "/ns"))
            ),
        )
        ov_right_frame.grid(row=0, column=3, rowspan=2, stick="nsew", **DEFAULT_PAD)

        self.overview_text = ScrolledText(
            overview_frame,
            state="disabled",
            width=DEFAULT_TEXT_WIDTH,
            height=DEFAULT_TEXT_HEIGHT,
            wrap="none",
        )
        self.overview_text.grid(row=0, column=0, rowspan=2, sticky="nsew", **DEFAULT_PAD)

        return overview_frame

    def add_derived_frame(self) -> LabelFrame:
        derived_frame = LabelFrame(self, text="Derived")
        derived_frame.columnconfigure(0, weight=1)

        dv_frame, self.dv_params = add_frame_group(
            derived_frame,
            (
                (*v, None, True)
                for v in (
                    ("Velocity Limit", "m/s"),
                    ("Load Density", "g/cm³"),
                )
            ),
        )
        dv_frame.grid(row=0, column=0, sticky="nsew", **DEFAULT_PAD)

        return derived_frame

    @tree_selected()
    def set_overview(self, *args, tvid, **kwargs):
        self.overview_text.config(state="normal")
        self.overview_text.delete(1.0, "end")
        if tvid:
            gun = self.guns[tvid]
            self.overview_text.insert("insert", gun.description)

            for v, sv in zip(
                (gun.charge.name, gun.charge.description),
                self.ov_top_params,
            ):
                sv.set(v)

            for v, sv in zip(
                (gun.cross_section * 1e2, gun.shot_mass, gun.charge_mass),
                self.ov_left_params,
            ):
                sv.set(v)

            for v, sv in zip(
                (gun.chamber_volume * 1e3, gun.start_pressure * 1e-6, gun.loss_fraction * 1e2),
                self.ov_mid_params,
            ):
                sv.set(v)

            ff = gun.charge.form_function
            for v, sv in zip(
                (ff.chi, ff.labda, ff.mu, ff.Z_k, gun.charge.reduced_burnrate * 1e9),
                self.ov_right_params,
            ):
                sv.set(v)

            for v, sv in zip((gun.velocity_limit, gun.delta * 1e-3), self.dv_params):
                sv.set(v)

        self.overview_text.config(state="disabled")

    @tree_selected()
    def add_edit_gun(self, tvid):
        dgw = DefineGunWindow(
            self, basis=self.guns[tvid] if tvid else None, get_props_func=self.get_props_func
        )
        self.wait_window(dgw)
        gun = dgw.gun
        if gun:
            self.add_gun(gun)

    def save_guns(self):
        fn = askopenfilename(
            parent=self, title="Save To File", filetypes=[("JavaScript Object Notation", ".json")]
        )
        if fn:
            Gun.to_file(guns=self.guns.values(), filename=fn)

    def load_guns(self):
        fn = askopenfilename(
            parent=self, title="Load From File", filetypes=[("JavaScript Object Notation", ".json")]
        )
        if fn:
            for gun in Gun.from_file(filename=fn):
                self.add_gun(gun)

    def add_gun(self, gun: Gun):
        gid = self.tree.insert("", "end", text=gun.name)
        self.guns[gid] = gun

    @tree_selected()
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
        tab_frame.columnconfigure(0, weight=1)
        self.notebook.add(tab_frame, text=tab_text)
        return tab_frame

    def add_non_perf(self):
        non_perf_frame = self.prepare_tab("Non Perf.")

        self.non_perf_entries = tuple(
            add_label_entry_label_group(non_perf_frame, i, *v)
            for i, v in enumerate([("Length", "mm"), ("Width", "mm"), ("Height", "mm")])
        )

    def add_single_perf(self):
        single_perf_frame = self.prepare_tab("Single Perf.")

        self.single_perf_entries = tuple(
            add_label_entry_label_group(single_perf_frame, i, *v)
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
            add_label_entry_label_group(multi_perf_frame, i, *v)
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
            length, width, height = (float(sv.get()) for sv in self.non_perf_entries)
            return FormFunction.non_perf(length=length, width=width, height=height)

        elif tab_index == 1:
            arch_width, height = (float(sv.get()) for sv in self.single_perf_entries)
            return FormFunction.single_perf(arch_width=arch_width, height=height)

        elif tab_index == 2:
            arch_width, perforation_diameter, height = (
                float(sv.get()) for sv in self.multi_perf_entries
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


class StatesFrame(LabelFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(text="States", *args, **kwargs)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        cols = (
            "marker",
            "time ms",
            "travel m",
            "velocity m/s",
            "burnup",
            "breech p. MPa",
            "average p. MPa",
            "shot p. MPa",
        )
        widths = (100, 100, 100, 100, 100, 100, 100, 100)

        self.tree = Treeview(self, columns=cols, show="headings", selectmode="browse")
        vsb = Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="nsew")
        self.tree.config(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")

        for width, col in zip(widths, self.tree["columns"]):
            self.tree.heading(column=col, text=col, anchor="c")
            self.tree.column(column=col, width=width, minwidth=width, stretch=True, anchor="c")
