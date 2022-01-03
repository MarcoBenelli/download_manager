from tkinter import ttk
import tkinter

import model


class App(ttk.Frame):
    def __init__(self) -> None:
        super().__init__()
        self.pack()

        self._string_var = tkinter.StringVar()
        entry = ttk.Entry(self, textvariable=self._string_var)
        entry.pack()
        entry.bind('<Key-Return>', self._start_download)

        canvas = tkinter.Canvas(self)
        scrollbar = ttk.Scrollbar(command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(command=canvas.xview)
        self._scrollable_frame = ttk.Frame(canvas)
        self._scrollable_frame.bind('<Configure>', lambda e: canvas.configure(
            scrollregion=canvas.bbox(tkinter.ALL)))
        canvas.create_window((0, 0), window=self._scrollable_frame)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack()
        scrollbar.pack()
        scrollbar_x.pack()

    def _start_download(self, event: tkinter.Event) -> None:
        # geometry
        list_element = ttk.Frame(self._scrollable_frame)
        ttk.Label(list_element, text=self._string_var.get()
                  ).grid(column=0, row=0)
        progressbar = ttk.Progressbar(
            list_element)
        progressbar.grid(column=0, row=1)
        list_element.pack()
        # progressbar.configure(length=list_element['width'])

        # menu
        menu = tkinter.Menu(list_element, tearoff=False)
        progressbar.bind('<3>', lambda e: menu.post(e.x_root, e.y_root))

        # submit url
        handle = model.Model(self._string_var.get(),
                             list_element.destroy, progressbar.step)
        self._string_var.set('')

        # menu commands
        menu.add_command(label='cancel', command=handle.cancel)
        menu.add_command(label='pause/restart', command=handle.toggle_pause)
