from tkinter import *
from tkinter import ttk, filedialog
from display import GraphDisplay, FillColor


class AppUI(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master, relief=SUNKEN, bd=2)
        self.grid(column=0, row=0, sticky=(N,W,E,S))
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.menubar = Menu(self)

        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(label="Open", command=open_problem, accelerator="Control + o")
        master.bind('<Control-o>', open_problem)
        menu.add_command(label="Exit", command=onExit)

        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Run", menu=menu)
        menu.add_command(label="Run", command=run_gac, accelerator="Control+r")
        master.bind('<Control-r>', run_gac)

        try:
            self.master.config(menu=self.menubar)
        except AttributeError:
            # master is a toplevel window (Python 1.4/Tkinter 1.63)
            self.master.tk.call(master, "config", "-menu", self.menubar)

        self.visualizer = GraphDisplay(self)
        self.visualizer.grid(column=0, row=0, sticky=E)
        
        self.visualizer.pack()

def run_gac(*args):
    print("TEST_RUN")

def open_problem(*args):
    print("Open")
    return filedialog.askopenfilename(title = "Choose text file containing graph data")

def onExit(*args):
        print("TEST_EXIT")
        root.quit()

root = Tk()
root.title("A*-gac map coloring")
app = AppUI(root)

#mainframe = ttk.Frame(root, padding="3 3 12 12")
#mainframe.grid(column=0, row=0, sticky=(N,W,E,S))
#mainframe.columnconfigure(0, weight=1)
#mainframe.rowconfigure(0, weight=1)


#ttk.Button(mainframe, text="Run", command=run_gac).grid(column=1, row=3, sticky=W)

#visualizer = GraphDisplay(mainframe)
#visualizer.grid(column=0, row=0, sticky=E)
#for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)
#
root.bind('<Return>', run_gac)

root.mainloop()

