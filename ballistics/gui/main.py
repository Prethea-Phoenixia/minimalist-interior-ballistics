from __future__ import annotations

import logging
from ctypes import windll
from tkinter import Menu, Tk
from tkinter.ttk import Frame, Notebook

from .gun_window import GunFrame
from .propellant_window import PropellantFrame

logger = logging.getLogger(__name__)


class MainFrame(Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        menubar = Menu(parent)
        parent["menu"] = menubar

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        notebook = Notebook(self)
        notebook.grid(row=0, column=0, sticky="nsew")

        notebook.rowconfigure(0, weight=1)
        notebook.columnconfigure(0, weight=1)

        propellant_selection_frame = PropellantFrame(notebook)
        propellant_selection_frame.grid(row=0, column=0, sticky="nsew")

        gun_selection_frame = GunFrame(
            notebook, get_props_func=propellant_selection_frame.get_props
        )
        gun_selection_frame.grid(row=0, column=0, sticky="nsew")
        notebook.add(gun_selection_frame, text="Gun Design(s)")
        notebook.add(propellant_selection_frame, text="Propellants")


def main():

    windll.shcore.SetProcessDpiAwareness(1)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)8s] %(message)s",  # (%(filename)s:%(lineno)s),
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.info("Started")

    root = Tk()
    root.option_add("*tearOff", False)

    # menu_file = Menu(menubar)
    # menu_edit = Menu(menubar)
    # menubar.add_cascade(menu=menu_file, label="File")
    # menubar.add_cascade(menu=menu_edit, label="Edit")

    main_frame = MainFrame(root)
    main_frame.grid(row=0, column=0, sticky="nsew")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    root.mainloop()

    logger.info("Ended")


if __name__ == "__main__":
    main()
