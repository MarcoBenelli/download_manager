from tkinter import ttk
import tkinter

import model


class HistoryFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # model
        self._history = model.DownloadJob.history()
        choices = [x['name'] for x in self._history]
        choicesvar = tkinter.StringVar(value=choices)

        # listbox
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self._listbox = tkinter.Listbox(self, listvariable=choicesvar)
        self._listbox.grid(column=0, row=0, rowspan=5, sticky=(
            tkinter.N, tkinter.S, tkinter.E, tkinter.W))
        self._listbox.bind('<<ListboxSelect>>', lambda e: self._show_stats())
        self._listbox.selection_set(0)

        # labels
        self._completed = tkinter.StringVar()
        tkinter.Label(self, textvariable=self._completed).grid(
            column=1, row=1, sticky=(tkinter.E, tkinter.W))
        self._time_s = tkinter.StringVar()
        tkinter.Label(self, textvariable=self._time_s).grid(
            column=1, row=2, sticky=(tkinter.E, tkinter.W))
        self._time_c = tkinter.StringVar()
        tkinter.Label(self, textvariable=self._time_c).grid(
            column=1, row=3, sticky=(tkinter.E, tkinter.W))

    def _show_stats(self):
        try:
            history_el = self._history[self._listbox.curselection()[0]]
        except IndexError:
            pass
        else:
            self._completed.set(
                'aborted' if history_el['result'] else 'completed')
            self._time_s.set(f'time started: {history_el["t_start"]}')
            self._time_c.set(f'time completed: {history_el["t_complete"]}')
