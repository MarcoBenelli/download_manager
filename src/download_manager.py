import os
import sys
import tkinter

import app


tkinter.Tk().title(os.path.basename(sys.argv[0]))
app.App().mainloop()
