from tkinter import *
from tkinter import ttk, filedialog
from display import GraphDisplay
from graph   import GraphModel, NodeModel, EdgeModel
from gac import ConstraintNetwork, GacNode
from vertexcoloring import *
from search import *
import threading

class AppUI(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master, relief=SUNKEN, bd=2, highlightthickness=0)
        self.grid(column=0, row=0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.menubar = Menu(self)

        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(label="Open", command=open_problem, accelerator="Ctrl+O")
        master.bind('<Control-o>', open_problem)
        menu.add_command(label="Exit", command=onExit)

        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Run", menu=menu)
        menu.add_command(label="Run k=4", command=run_gac, accelerator="Ctrl+R")
        master.bind('<Control-r>', run_gac)
        
        try:
            self.master.config(menu=self.menubar)
        except AttributeError:
            self.master.tk.call(master, "config", "-menu", self.menubar)
       
        #TODO: Put in a bar where labels can be placed. 
        #self.pack(fill=BOTH, expand=YES)
        self.visualizer = GraphDisplay(self)
        self.visualizer.grid(row=1, column=1)
        self.visualizer.columnconfigure(1, weight=1)
        self.visualizer.rowconfigure(1, weight=1)
        #For resizing purposes. Display can be dynamically resized
        #self.visualizer.pack(fill=BOTH, expand=YES)
        self.visualizer.bind("<Configure>", self.visualizer.on_resize)
        self.visualizer.addtag_all("all")
        self.graph = None

#Start the vertex coloring.
#Convert graph into domain, variables and constraints
#So the general arc consistency can do it's job
def run_gac(*args):
    cn = None
    if app.graph:
        cn = VertexColoring.convert_graph_to_cnet(app.graph, 4)
    #Create initialNode
    constraint_instance = cn.create_instance()
    start_node = GacNode(constraint_instance, is_root=True)
    
    #Run algorithm in it's own thread
    #The algorithm send events that is put in a display queue.
    #This means that the Ui and algorithm can work together
    def callback():
        app.visualizer.start()
        astar = Search(app.visualizer)
        result_node = astar.search(start_node, SearchMode.BEST)
        app.visualizer.stop()
        print("FINISHED")
        if result_node:
            print(result_node.is_solution())
        else:
            print("NO SOLUTION")

    t = threading.Thread(target=callback)
    t.daemon = True
    t.start()



#Opens a file dialog where the input file can be graphically selected
def open_problem(*args):
    filename = filedialog.askopenfilename(title = "Choose text file containing graph data")
    try:
        problem = open(filename, "r")
        colorize_problem_data = init_display(problem)
        app.graph = colorize_problem_data
        app.visualizer.set_model(colorize_problem_data)

    except IOError as e:
        print("File could not be openend" + format(e.errno, e.strerror))

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
root.title("A*-gac map coloring")
app = AppUI(root)
root.bind('<Return>', run_gac)

root.mainloop()