import os
import tkinter
from concurrent import futures
from urllib import request, parse


class App(tkinter.Frame):
    def __init__(self) -> None:
        super().__init__()
        self.pack()

        entry = tkinter.Entry()
        entry.pack()
        self._string_var = tkinter.StringVar()
        entry['textvariable'] = self._string_var
        entry.bind('<Key-Return>', self.return_bind)

        frame = tkinter.Frame()
        canvas = tkinter.Canvas(frame)
        scrollbar = tkinter.Scrollbar(command=canvas.yview)
        self._scrollable_frame = tkinter.Frame(canvas)
        self._scrollable_frame.bind('<Configure>', lambda e: canvas.configure(
            scrollregion=canvas.bbox(tkinter.ALL)))
        canvas.create_window((0, 0), window=self._scrollable_frame)
        canvas.configure(yscrollcommand=scrollbar.set)
        frame.pack()
        canvas.pack()
        scrollbar.pack()

        # self._listbox = tkinter.Listbox()
        # self._listbox.pack()

        self._executor = futures.ThreadPoolExecutor()

    def return_bind(self, event: tkinter.Event) -> None:
        future = self._executor.submit(
            self.submittable, self._string_var.get())
        message = tkinter.Message(
            self._scrollable_frame, text=self._string_var.get())
        message.pack()
        # self._listbox.insert(tkinter.END, self._string_var.get())
        future.add_done_callback(lambda f: message.destroy())
        # url = self._string_var.get()
        # self._string_var.set('')
        # future.add_done_callback(lambda f: self._listbox.delete(
        #     self._listbox.get(0, tkinter.END).index(url)))
        future.add_done_callback(lambda f: print(f.exception()))

    def submittable(self, url: str) -> None:
        # print(url)
        with request.urlopen(url) as response:
            # print(os.path.basename(parse.urlparse(url).path))
            # print(response.read())
            with open(os.path.basename(parse.urlparse(url).path), 'wb') as f:
                f.write(response.read())


app = App()
app.mainloop()
