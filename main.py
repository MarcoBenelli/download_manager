import tkinter
from tkinter import ttk

import model


class App(tkinter.Frame):
    def __init__(self) -> None:
        super().__init__()
        self.pack()

        entry = tkinter.Entry()
        entry.pack()
        self._string_var = tkinter.StringVar()
        entry['textvariable'] = self._string_var
        entry.bind('<Key-Return>', self._start_download)

        canvas = tkinter.Canvas()
        scrollbar = tkinter.Scrollbar(command=canvas.yview)
        self._scrollable_frame = tkinter.Frame(canvas)
        self._scrollable_frame.bind('<Configure>', lambda e: canvas.configure(
            scrollregion=canvas.bbox(tkinter.ALL)))
        canvas.create_window((0, 0), window=self._scrollable_frame)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack()
        scrollbar.pack()

    def _start_download(self, event: tkinter.Event) -> None:
        list_element = tkinter.Frame(self._scrollable_frame)
        message = tkinter.Message(list_element, text=self._string_var.get())
        progressbar = ttk.Progressbar(list_element, mode='determinate')
        list_element.pack()
        message.pack()
        progressbar.pack()
        model.Model.submit_url(self._string_var.get(),
                               list_element.destroy, progressbar.step)
        self._string_var.set('')


app = App()
app.mainloop()
