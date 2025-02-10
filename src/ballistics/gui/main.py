from __future__ import annotations

import logging
from ctypes import windll
from tkinter import Menu, Tk, Toplevel
# from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Button, Entry, Frame, Label, Notebook
from typing import Callable

from .. import DEFAULT_ACC, DEFAULT_STEPS
from . import DEFAULT_ENTRY_WIDTH, DEFAULT_PAD
from .gun_window import GunFrame
from .propellant_window import PropellantFrame
from .themed_scrolled_text import ThemedScrolledText as ScrolledText

# from ttkthemes import ThemedTk
# import sv_ttk


logger = logging.getLogger(__name__)


class TextHandler(logging.Handler):
    def __init__(self, text, *args, **kwargs):
        # run the regular Handler __init__
        logging.Handler.__init__(self, *args, **kwargs)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.configure(state="normal")
            self.text.insert("end", msg + "\n")
            self.text.configure(state="disabled")
            # Autoscroll to the bottom
            self.text.yview("end")

        # This is necessary because we can't modify the Text from other threads
        self.text.after(10, append)


class DefineParameterFrame(Toplevel):
    def __init__(
        self,
        parent,
        *args,
        label: str,
        validator: Callable[[float], bool],
        warn: str,
        title: str = "Set Parameter",
        astype: type = float,
        **kwargs,
    ):
        super().__init__(parent, *args, **kwargs)
        self.resizable(False, False)
        self.transient(parent)
        self.title(title)
        self.columnconfigure(0, weight=1)
        self.astype = astype
        self.warn = warn

        self.validator = validator
        Label(self, text=label, anchor="center").grid(row=0, column=0, sticky="nsew", **DEFAULT_PAD)
        self.entry = Entry(self, width=DEFAULT_ENTRY_WIDTH)
        self.entry.grid(row=1, column=0, sticky="nsew", **DEFAULT_PAD)

        Button(self, text="Confirm", command=self.define_val).grid(
            row=2, column=0, sticky="nsew", **DEFAULT_PAD
        )

        self.val = None

    def define_val(self):
        if v := self.entry.get():
            try:
                val = self.astype(v)
                if not self.validator(val):
                    raise ValueError(self.warn)
                self.val = val
                self.destroy()
            except ValueError as e:
                logger.warning(str(e))


class MainFrame(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        menubar = Menu(parent)
        parent["menu"] = menubar

        file_menu = Menu(menubar)
        edit_menu = Menu(menubar)
        config_menu = Menu(menubar)

        menubar.add_cascade(menu=file_menu, label="File")
        menubar.add_cascade(menu=edit_menu, label="Edit")
        menubar.add_cascade(menu=config_menu, label="Config")

        self.acc = DEFAULT_ACC
        self.steps = DEFAULT_STEPS

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        notebook = Notebook(self)
        notebook.grid(row=0, column=0, sticky="nsew", **DEFAULT_PAD)

        logs = ScrolledText(self, width=40, height=5)
        logs.grid(row=1, column=0, sticky="nsew", **DEFAULT_PAD)
        logs.configure(font="TkFixedFont")

        fmt = "[{levelname:^8}] {message} -- ({asctime}: {filename}: {lineno})"

        logging.basicConfig(
            level=logging.INFO,
            format=fmt,
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{",
        )

        text_handler = TextHandler(logs)
        text_handler.setFormatter(
            logging.Formatter(
                fmt=fmt,
                datefmt="%Y-%m-%d %H:%M:%S",
                style="{",
            )
        )

        # Add the handler to logger
        logger = logging.getLogger()
        logger.addHandler(text_handler)

        logger.info("logger initialized.")

        notebook.rowconfigure(0, weight=1)
        notebook.columnconfigure(0, weight=1)

        propellant_frame = PropellantFrame(notebook)
        propellant_frame.grid(row=0, column=0, sticky="nsew", **DEFAULT_PAD)

        gun_frame = GunFrame(
            notebook,
            get_props_func=propellant_frame.get_props,
            get_acc_func=lambda: self.acc,
            get_steps_func=lambda: self.steps,
        )
        gun_frame.grid(row=0, column=0, sticky="nsew", **DEFAULT_PAD)

        notebook.add(gun_frame, text="Gun Design(s)")
        notebook.add(propellant_frame, text="Propellants")

        edit_menu.add_command(label="Add/Copy Gun", command=gun_frame.add_edit_gun)
        edit_menu.add_command(label="Delete Gun", command=gun_frame.del_gun)
        edit_menu.add_separator()

        edit_menu.add_command(label="Add/Copy Propellant", command=propellant_frame.add_edit_prop)
        edit_menu.add_command(label="Delete Propellant", command=propellant_frame.del_prop)

        file_menu.add_command(label="Save Gun(s) (file)", command=gun_frame.save_guns)
        file_menu.add_command(label="Save Gun(s) (dir)", command=gun_frame.save_by_family)
        file_menu.add_command(label="Load Gun(s)", command=gun_frame.load_guns)
        file_menu.add_separator()

        file_menu.add_command(label="Load Propellant(s)", command=propellant_frame.load_props)

        config_menu.add_command(label=f"Accuracy ({self.acc:.3g})", command=self.set_acc)
        config_menu.add_command(label=f"Steps ({self.steps:.3g})", command=self.set_steps)

        self.config_menu = config_menu

    def set_acc(self):
        dpf = DefineParameterFrame(
            self,
            label="Accuracy",
            validator=lambda x: 1 > x > 0,
            astype=float,
            warn="Accuracy must be float between 0 and 1",
        )
        self.wait_window(dpf)
        val = dpf.val
        if val:
            self.acc = val
            self.config_menu.entryconfigure(0, label=f"Accuracy ({self.acc:.3g})")

    def set_steps(self):
        dpf = DefineParameterFrame(
            self,
            label="Steps",
            validator=lambda x: x > 0,
            astype=int,
            warn="Steps must be integer greater than 0",
        )
        self.wait_window(dpf)
        val = dpf.val
        if val:
            self.steps = val
            self.config_menu.entryconfigure(1, label=f"Steps ({self.steps:.3g})")


def main():

    # windll.shcore.SetProcessDpiAwareness(1)
    root = Tk()
    root.option_add("*tearOff", False)
    main_frame = MainFrame(root)
    main_frame.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    # Style().theme_use("clam")
    root.mainloop()


if __name__ == "__main__":
    main()
