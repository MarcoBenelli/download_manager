from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import tkinter

import history_frame
import model


class App(ttk.Frame):
    def __init__(self, master: tkinter.Tk) -> None:
        # container
        super().__init__(master)
        self._master = master
        master.protocol("WM_DELETE_WINDOW", self._delete_window)
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
        canvas.columnconfigure(0, weight=1)

        # menu
        menubar = tkinter.Menu(master)
        master.configure(menu=menubar)
        menu_edit = tkinter.Menu(menubar)
        menubar.add_cascade(menu=menu_edit, label='Edit')
        menu_edit.add_command(
            label='Change download directory', command=self._change_dir)
        menu_view = tkinter.Menu(menubar)
        menubar.add_cascade(menu=menu_view, label='View')
        menu_view.add_command(label='History', command=self._view_history)

    def _start_download(self, event: tkinter.Event) -> None:
        # geometry
        list_element = ttk.Frame(self._scrollable_frame, relief=tkinter.SOLID)
        entry = ttk.Entry(list_element)
        entry.insert(0, self._string_var.get())
        entry.configure(state='readonly')
        entry.grid(column=0, row=0, sticky=(tkinter.E, tkinter.W))
        progressbar = ttk.Progressbar(list_element)
        progressbar.grid(column=0, row=1, sticky=(tkinter.E, tkinter.W))
        list_element.pack(expand=True, fill=tkinter.X)  # does not expand

        # menu
        menu = tkinter.Menu(list_element)
        progressbar.bind('<3>', lambda e: menu.post(e.x_root, e.y_root))

        # submit url
        list_element.bind('<<Destroy>>', lambda e: list_element.destroy())
        progressbar.bind('<<Step>>', lambda e: progressbar.step())
        job = model.DownloadJob.create(
            self._string_var.get(),
            lambda: list_element.event_generate('<<Destroy>>'),
            lambda: progressbar.event_generate('<<Step>>'),
            lambda exc: messagebox.showerror(type(exc), exc))
        self._string_var.set('')

        # menu commands
        menu.add_command(label='cancel', command=job.cancel)
        menu.add_command(label='pause/restart', command=job.toggle_pause)

    def _delete_window(self) -> None:
        model.DownloadJob.delete_all()
        print('destroying root')
        self._master.destroy()

    def _change_dir(self) -> None:
        if d := filedialog.askdirectory():
            model.DownloadJob.downloads_dir = d

    def _view_history(self) -> None:
        toplevel = tkinter.Toplevel(self._master)
        toplevel.columnconfigure(0, weight=1)
        toplevel.rowconfigure(0, weight=1)
        frame = history_frame.HistoryFrame(toplevel)
        frame.grid(column=0, row=0, sticky=(
            tkinter.N, tkinter.S, tkinter.E, tkinter.W))
