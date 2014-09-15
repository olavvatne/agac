from tkinter import *
from tkinter import ttk
from enum import Enum
import math
from collections import deque

class GraphDisplay(Canvas):
	cWi = 600
	cHi = 400
	pixelSize = 10

	def __init__(self, parent):
		self.padding = 20
		self.queue = deque([])
		super().__init__(parent, bg='white', width=self.cWi, height=self.cHi)

	def setModel(self, model):
		self.model = model

	def draw(self):
		self.reset()
		self.setDimension( self.model.width, self.model.height )

		if len(self.queue)>0:
			timeSlice = self.queue.popleft()
			currentPath = timeSlice[0]
			#generated = timeSlice[1]
			#isSolution = timeSlice[2]
			#pathLength = len(currentPath) -1
			
			#self.create_text(400, 20, text=("Generated: " + str(generated)))
			#self.create_text(400, 40, text=("Best path: " + str(pathLength)))
			#if isSolution:
			#	self.create_text(400, 60, text=("A solution!"))
			#else:
				#self.create_text(400, 60, text=("Not a solution!"))


		if not self.stopped or len(self.queue) > 0:
			self.after(100, self.draw)


	def start(self):
		self.stopped = False
		self.draw()

	def stop(self):
		self.stopped = True

	#The actual position of a board cell/pixel.
	def gridPos(self, pos):
		return self.padding+ (pos*self.pixelSize)

	def reset(self):
		self.delete(ALL)

	#By setting the dimension the pixelSize is determined.
	#Based on the width and height the board is scaled to fit inside the canvas.
	def setDimension(self, width, height):
		pass
		#self.reset()
		#self.width = width
		#self.height = height
		#if height >= width:
	#		self.pixelSize = math.floor((self.cHi-2*self.padding) / height)
	#	else:
	#		self.pixelSize = math.floor( (self.cWi-2*self.padding) / width)
	#	self.create_rectangle(self.padding, self.padding,
	#						  self.padding + width*self.pixelSize,
	#						  self.padding + height*self.pixelSize,
	#						  fill="white")

	def setPadding(self, padding):
		self.padding = padding

	#Event listener method. For the object to be accepted as a listener it has to have
	#this method, or else an exception is raised.
	def event(self, node, generated, solution):
		self.queue.append((node.guiRepresentation(), generated, solution))
	
	def translateHeight(self, y):
		return math.fabs(self.height -y)

#Enum for fill colors for the different cells in the canvas.
class FillColor(Enum):
	PATH = "blue"
	OBSTACLE = "red"
	GOAL = "grey"
	START = "grey"
	NONE = "white"
