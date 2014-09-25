from tkinter import *
from tkinter import ttk, filedialog, messagebox
from display import GraphDisplay
from graph   import GraphModel, NodeModel, EdgeModel
from gac import ConstraintNetwork, GacNode
from vertexcoloring import *
from search import *
import threading

class AppUI(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master, relief=SUNKEN, bd=2, highlightthickness=0)
        self.grid(sticky=N+S+E+W)
        
        self.menubar = Menu(self)
        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(label="Open", command=open_problem, accelerator="Ctrl+O")
        master.bind('<Control-o>', open_problem)
        menu.add_command(label="Exit", command=onExit)
        menu = Menu(self.menubar, tearoff=0)
        
        self.menubar.add_cascade(label="Run", menu=menu)  
        shortcuts = [(3, "q"), (4, "w"), (5, "e"), (6, "r"), (7, "t"), (8, "y"), (9, "u"), (10, "i")]
        for num, key in shortcuts:
            menu.add_command(
                label="Run k=" + str(num),
                command=lambda n=num: callback(n),
                accelerator="Ctrl+" + str(key).upper())
            master.bind("<Control-" + key +">", lambda event, n=num: callback(n)) 
        menu.add_command(label="Run (custom k)", command=lambda: custom(), accelerator="Ctrl+A")
        master.bind("<Control-a>", lambda event: custom())
        
        def callback(n):
            run_gac(k=n)
        
        def custom():
            d = CustomDialog(master)
            master.wait_window(d.top)
            value = int(d.result)
            run_gac(k=value)

        try:
            self.master.config(menu=self.menubar)
        except AttributeError:
            self.master.tk.call(master, "config", "-menu", self.menubar)

        self.visualizer = GraphDisplay(self)
        self.visualizer.grid(row=1, column=0, columnspan=10, sticky=N+S+E+W)
        #For resizing purposes. Display can be dynamically resized
        self.visualizer.bind("<Configure>", self.visualizer.on_resize)
        self.visualizer.addtag_all("all")
        self.graph = None

        unsatisfied_text = Label(self, text="Unsatisfied: ")
        unsatisfied_text.grid(row=0, column=0, sticky=W, padx=2)

        self.unsatisfied_counter = Label(self, text="", fg="red")
        self.unsatisfied_counter.grid(row=0, column=1, sticky=W, padx=2)

        unassigned_text = Label(self, text="Unassigned: ")
        unassigned_text.grid(row=0, column=2, sticky=W ,padx=2)

        self.unassigned_counter = Label(self, text="", fg="red")
        self.unassigned_counter.grid(row=0, column=3, sticky=W, padx=2)

        nodenumber_text = Label(self, text="Node generated: ")
        nodenumber_text.grid(row=0, column=4, sticky=W, padx=2)

        self.nodenumber_counter = Label(self, text="", fg="red")
        self.nodenumber_counter.grid(row=0, column=5, sticky=W, padx=2)

        nodepopped_text = Label(self, text="Nodes popped: ")
        nodepopped_text.grid(row=0, column=6, sticky=W, padx=2)

        self.nodepopped_counter = Label(self, text="", fg="red")
        self.nodepopped_counter.grid(row=0, column=7, sticky=W, padx=2)

        pathlength_text = Label(self, text="Assumptions: ")
        pathlength_text.grid(row=0, column=8, sticky=W,padx=2)

        self.pathlength_counter = Label(self, text="", fg="red")
        self.pathlength_counter.grid(row=0, column=9, sticky=W, padx=2)


        #How widgets should expand on resize
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=1)
        self.columnconfigure(7, weight=1)
        self.columnconfigure(8, weight=1)
        self.columnconfigure(9, weight=1)
        self.rowconfigure(1, weight=1)

    def set_labels(self, unsatisfied="", unassigned="", nodenumber="", nodepopped="", assumptions=""):
        self.unsatisfied_counter.config(text=str(unsatisfied))
        self.unassigned_counter.config(text=str(unassigned))
        self.nodenumber_counter.config(text=str(nodenumber))
        self.nodepopped_counter.config(text=str(nodepopped))
        self.pathlength_counter.config(text=str(assumptions))


class CustomDialog(object):
    def __init__(self, parent):

        top = self.top = Toplevel(parent)

        Label(top, text="K value").pack()

        self.e = Entry(top)
        self.e.pack(padx=5)
        self.result = ""
        b = Button(top, text="OK", command=self.ok)
        b.pack(pady=5)

    def ok(self):
        self.result = self.e.get()
        self.top.destroy()


#Start the vertex coloring.
#Convert graph into domain, variables and constraints
#So the general arc consistency can do it's job
def run_gac(*args, k=4):
    if not app.graph:
        messagebox.showinfo("Error", "Open problem instance before running.")
        raise Exception("Open problem instance before running")
    cn = VertexColoring.convert_graph_to_cnet(app.graph, k)
    #Create initialNode
    constraint_instance = cn.create_instance()
    start_node = GacNode(constraint_instance, is_root=True)
    
    #Run algorithm in it's own thread
    #The algorithm send events that is put in a display queue.
    #This UI and algorithm can work on seperate threads
    def callback():
        app.visualizer.draw_label("K = " + str(k))
        app.visualizer.start()
        astar = Search(app.visualizer)
        result_node = astar.search(start_node, SearchMode.BEST)
        app.visualizer.stop()
        print("FINISHED")
        if result_node:
            print("SOLUTION")
            print(result_node)
        else:
            print("NO SOLUTION")

    t = threading.Thread(target=callback)
    t.daemon = True
    t.start()



#Opens a file dialog where the input file can be graphically selected.
#The file is converted into a graph which Display use as a model.
def open_problem(*args):
    filename = filedialog.askopenfilename(title = "Choose text file containing graph data")
    try:
        problem = open(filename, "r")
        colorize_problem_data = init_display(problem)
        app.graph = colorize_problem_data
        app.visualizer.set_model(colorize_problem_data)

    except (Exception) as e:
        messagebox.showinfo("Error", "File could not be read. \n" + str(e))

#Configure the display when new data is presented,
#and converts input data to objects which will be used to setup the a*-gac
def init_display(problem_file):
    app.visualizer.reset()
    temp = problem_file.readline().split()
    nr_vertices = eval(temp[0])
    nr_edges = eval(temp[1])
    max_x = 0
    max_y = 0
    min_x = 0
    min_y = 0
    graphModel = GraphModel()

    #The vertices are read in first from file, and the min and max of coordinates are registered
    for l in range(nr_vertices):
        vertex = problem_file.readline().split()
        x = float(vertex[1])
        y = float(vertex[2])
        nodeModel = NodeModel( int(vertex[0]) , x , y )
        graphModel.add_vertex(nodeModel)

        if max_x < x: max_x = x
        if max_y < y: max_y = y
        if min_x > x: min_x = x
        if min_y > y: min_y = y

    #The edges are read and the vertices it connects put into an edgemodel
    for e in range(nr_edges):
        edge = problem_file.readline().split()
        edgeModel = EdgeModel(graphModel.get_vertex("N" + str(edge[0])), graphModel.get_vertex("N" + str(edge[1]) ))
        graphModel.add_edge(edgeModel)

    problem_file.close()
    app.visualizer.set_dimension(max_x, max_y, min_x, min_y)
    return graphModel


def onExit(*args):
        print("TEST_EXIT")
        root.quit()


root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.title("A*-gac map coloring")
app = AppUI(root)
root.bind('<Return>', run_gac)

root.mainloop()