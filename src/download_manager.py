import os
import sys
import tkinter

import app


root = tkinter.Tk()
root.title(os.path.basename(sys.argv[0]))
app.App().mainloop()
