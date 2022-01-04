from tkinter import ttk
import tkinter

import model


class App(ttk.Frame):
    def __init__(self, master: tkinter.Tk) -> None:
        # container
        super().__init__(master)
        self.grid(column=0, row=0, sticky=(
            tkinter.N, tkinter.S, tkinter.E, tkinter.W))
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # entry
        self._string_var = tkinter.StringVar()
        entry = ttk.Entry(self, textvariable=self._string_var)
        entry.grid(column=0, row=0, columnspan=2,
                   sticky=(tkinter.E, tkinter.W))
        entry.bind('<Key-Return>', self._start_download)

        # canvas
        canvas = tkinter.Canvas(self)
        scrollbar = ttk.Scrollbar(self, command=canvas.yview)
        self._scrollable_frame = ttk.Frame(canvas)
        self._scrollable_frame.bind('<Configure>', lambda e: canvas.configure(
            scrollregion=canvas.bbox(tkinter.ALL)))
        canvas.create_window((0, 0), window=self._scrollable_frame)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.grid(column=0, row=1, sticky=(
            tkinter.N, tkinter.S, tkinter.E, tkinter.W))
        scrollbar.grid(column=1, row=1, sticky=(tkinter.N, tkinter.S))

    def _start_download(self, event: tkinter.Event) -> None:
        # geometry
        list_element = ttk.Frame(self._scrollable_frame, relief=tkinter.SOLID)
        entry = ttk.Entry(list_element)
        entry.insert(0, self._string_var.get())
        entry.configure(state='readonly')
        entry.grid(column=0, row=0, sticky=(tkinter.E, tkinter.W))
        progressbar = ttk.Progressbar(list_element)
        progressbar.grid(column=0, row=1, sticky=(tkinter.E, tkinter.W))
        list_element.pack()

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
