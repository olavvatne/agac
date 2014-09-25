from tkinter import *
from tkinter import ttk
from enum import Enum
from math import fabs
from collections import deque


class GraphDisplay(Canvas):
    cWi = 600
    cHi = 400

    def __init__(self, parent):
        self.queue = deque([])
        self.model = None
        self.width = self.cWi
        self.height = self.cHi
        self.padding = int(self.width/64)
        self.parent = parent
        super().__init__(parent, bg='white', width=self.width, height=self.height, highlightthickness=0)

        
    def set_model(self, model):
        self.model = model
        self.draw_graph()
        #Set the label row of parent to the correct values.
        self.parent.set_labels(
            nodenumber=0,
            nodepopped=0,
            assumptions=0,
            unsatisfied="",
            unassigned=len(self.model.vertices)
            )

    def get_model(self):
        return self.model

    #Draw will call itself and redraw (colorize nodes) as long
    #as the display is in running mode or there are timeslices left
    #in the queue. The queue of timeslices allow the algorithm to run at 
    #full speed while the display is delaying the rendering, so it is easy to
    #watch it's progress
    def draw(self):
        if len(self.queue)>0:
            timeslice = self.queue.popleft()
            current_solution = timeslice["values"]
            generated = timeslice["generated"]
            popped = timeslice["popped"]
            assumptions = timeslice["assumption"]
            is_solution = timeslice["popped"]
            unassigned = 0
            unsatisfied = timeslice["unsatisfied"]

            for vertex, color_id in current_solution:
                if color_id == -1:
                    unassigned += 1
                item = self.find_withtag(vertex)
                self.colorize_item(item, Color.get(color_id))

            self.parent.set_labels(
                nodenumber=generated,
                nodepopped=popped,
                assumptions=assumptions,
                unsatisfied=unsatisfied,
                unassigned=unassigned
                )
        if not self.stopped or len(self.queue) > 0:
            self.after(40, self.draw)

    def colorize_item(self, item, color):
        self.itemconfig(item, fill=color)

    #Draws the axis through origo. Shows how the graph is placed
    #on a coordinate system
    def draw_axis(self):
        self.create_line(self.translate_x(0),
            self.translate_y(self.min_y),
            self.translate_x(0),
            self.translate_y(self.max_y),
            fill="#C0C0C0")
        self.create_line(self.translate_x(self.max_x),
            self.translate_y(0),
            self.translate_x(self.min_x),
            self.translate_y(0),
            fill="#C0C0C0")

    def draw_label(self, text):
        self.delete("label")
        self.create_text(self.padding*3, self.padding*2, text=text, tags="label")

    #Method for drawing a graph from a GraphModel. 
    #Draws edges and then vertices to get correct ordering and 
    #correct visual representation.
    def draw_graph(self):
        for e in self.model.edges:
            self.create_line(self.translate_x( e.sp.x ),
                self.translate_y( e.sp.y ),
                self.translate_x( e.ep.x ),
                self.translate_y( e.ep.y ),
                )    

        vertex_radius = int(self.width/256)
        for key in sorted(self.model.vertices):
            n = self.model.vertices[key]
            self.create_oval(self.translate_x(n.x)-(vertex_radius),
                self.translate_y(n.y)-(vertex_radius),
                self.translate_x(n.x)+(vertex_radius*2),
                self.translate_y(n.y)+(vertex_radius*2),
                fill="grey",
                tags=str(n.id))

    def start(self):
        self.stopped = False
        self.draw()

    def stop(self):
        self.stopped = True

    #The actual x position of the graph element on screen
    def translate_x(self, x):
        x_norm = fabs(self.min_x) + x
        x_screen = (self.padding/2) + x_norm*(float((self.width-self.padding)/self.w))
        return x_screen

    #The actual y position of the graph element on screen
    def translate_y(self, y):
        y_norm = fabs(self.min_y) + y
        y_screen = (self.padding/2) + y_norm*(float((self.height-self.padding)/self.h))
        return y_screen

    def reset(self):
        self.delete(ALL)

    def set_padding(self, padding):
        self.padding = padding

    def set_dimension(self, max_x, max_y, min_x, min_y):
        self.w = fabs(min_x) + max_x
        self.h = fabs(min_y) + max_y
        self.max_x = max_x
        self.max_y = max_y
        self.min_y = min_y
        self.min_x = min_x
        self.draw_axis()

    #If window is resized all elements in canvas are scaled up/down
    #along with the window. A new width and height and padding is set.
    #Done so display stays consistent if new model is set.
    def on_resize(self,event):
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        self.padding = int(self.width/64)
        self.config(width=self.width, height=self.height)
        self.scale("all",0,0,wscale,hscale)

    def event(self, data):
        self.queue.append(data)

#A switch case for retriving a color. A somewhat lazy approch
#since there there is a limitied number of colors in the 
#dictionary.
class Color(object):
    options = {
        -1: "grey",
        0 : "red",
        1 : "#00FF00",
        4 : "blue",
        9 : "yellow",
        2 : "magenta",
        3 : "cyan",
        5 : "#D3FAC1",
        6 : "#BB9435",
        7 : "#FFFCC4",
        8 : "#6B8079",
        9 : "#FE605D",
        10: "#3330F5",
        11: "#FF1511",
        12: "#C60B1E"
    }
    def get(n):
        if n < -1 or n > 12:
            return "black"
        else:
            return Color.options[n]
