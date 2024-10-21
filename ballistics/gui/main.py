from __future__ import annotations

import logging
from ctypes import windll
from tkinter import Menu, Tk
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Frame, Notebook

from . import DEFAULT_PAD
from .gun_window import GunFrame
from .propellant_window import PropellantFrame

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


class MainFrame(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        menubar = Menu(parent)
        parent["menu"] = menubar

        file_menu = Menu(menubar)
        edit_menu = Menu(menubar)

        menubar.add_cascade(menu=file_menu, label="File")
        menubar.add_cascade(menu=edit_menu, label="Edit")

        # prop_edit_menu = Menu(edit_menu)
        # edit_menu.add_cascade(menu=prop_edit_menu, label="Propellant")

        # prop_file_menu = Menu(file_menu)
        # file_menu.add_cascade(menu=prop_file_menu, label="Propellant")

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

        gun_frame = GunFrame(notebook, get_props_func=propellant_frame.get_props)
        gun_frame.grid(row=0, column=0, sticky="nsew", **DEFAULT_PAD)
        notebook.add(gun_frame, text="Gun Design(s)")
        notebook.add(propellant_frame, text="Propellants")

        edit_menu.add_command(label="Add/Copy Gun", command=gun_frame.add_edit_gun)
        edit_menu.add_command(label="Delete Gun", command=gun_frame.del_gun)
        edit_menu.add_separator()

        edit_menu.add_command(label="Add/Copy Propellant", command=propellant_frame.add_edit_prop)
        edit_menu.add_command(label="Delete Propellant", command=propellant_frame.del_prop)

        file_menu.add_cascade(label="Load Propellant(s)", command=propellant_frame.load_props)
        file_menu.add_separator()


def main():

    windll.shcore.SetProcessDpiAwareness(1)

    root = Tk()
    root.option_add("*tearOff", False)

    main_frame = MainFrame(root)
    main_frame.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()


if __name__ == "__main__":
    main()
