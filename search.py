from enum import Enum
from abstractnode import Node
import time
from collections import deque
import heapq

class Search(object):
    

    #Init for the search object. A listner can be passed as a argument. The listner must
    #have a event method. The A* algorithm will during its execution generate gui representation and
    #call the lister.
    def __init__(self, listner):
        if not hasattr(listner, "event"):
            raise Exception("Listner does not have event method handler")
        self.listner = listner
        self.nodes_generated = 0
        self.nodes_popped = 0

    #A* implementation - based on pseudocode from accompanying document, IDAA
    #The search method support, depth, breadth and best first search, which is specified by mode.
    #The method tries to be as general as possible, only relying on mandatory methods subclasses of Node must have.
    def search(self, start_node, mode):
        if not isinstance(start_node, Node):
            raise Exception("Node should be a subclass of Abstractnode")
        if not isinstance(mode, SearchMode):
            raise Exception("Mode is not a SearchMode type")
        if start_node.is_solution():
            return start_node

        closed = set() #O(1) lookup when using a set. Closed mainly used for "in" "not in" 
        frontier = Frontier(mode) #The open list
        unique = {}

        #Start_node added to the frontier, and put into the unique dictionary.
        n0 = start_node
        n0.set_G( 0 )
        frontier.add( n0 )
        self.nodes_generated +=1
        unique[n0.generate_id()] = n0
        solution = None

        #Agenda loop. At each iteration a node is popped from the frontier and expanded.
        #In the case of best first search, the most promising node is always expanded first
        #A estimate H , and G is used to assess how promising a node might be. 
        while solution is None:
            if not frontier.list:
                #All nodes has been expanded and none were found to be a solution
                return None
            x = frontier.pop()
            self.nodes_popped += 1
            self.send_event(x)
            closed.add(x)
            if x.is_solution():
                #Node is return in case node x is the solution
                return x

            #For each successor node of x, it is added as a child of node x,
            #checked for uniqueness (if not unique it is replaced by the already generated successor),
            #If child node is a new unique node it is added to the frontier list/heap. If successor node,
            #has been seen before, it can still impact the search. THe parent til successor path might
            #represent a better way (cost less), than already found. 
            successors = x.generate_successors()
            for s in successors:
                if s.generate_id() in unique:
                    s = unique[s.generate_id()]
                else:
                    unique[s.generate_id()] = s
                    #Only successors that are unique is added to nodes_generated. It is only those that
                    #are used further.
                    self.nodes_generated += 1

                x.add_child(s)

                if s not in frontier and s not in closed:
                    self.attachAndEval(s, x)
                    frontier.add(s)
                elif x.get_G() + x.arc_cost(s) < s.get_G():
                    #Cheaper path to S is found
                    self.attachAndEval(s, x)
                    if s in closed:
                        #When a node is in closed it has
                        #already been popped from the frontier,
                        #which means the improvements has to be
                        #propagated to the nodes children.
                        self.propagatePathImprovements(s)
                        #Propagating improvements can change the F value of some nodes, and
                        #heap list has to be sorted to keep the heap invariant.
                    frontier.reheap()

    def send_event(self, x):
        
        self.listner.event(
            x,
            self.nodes_generated,
            self.nodes_popped,
            x.get_level(),
            x.is_solution()
            )
        #Give thread a chance to yield to other threads
        time.sleep(0.001)

    #Method that construct node graph, and sets the successors G value.
    def attachAndEval(self, child, parent):
        child.set_parent(parent)
        child.set_G( parent.get_G() + parent.arc_cost(child) )
        child.calc_H()
        #calcF add g and together when called
    
    #Recursive method that is used whenever a better way from a node to a successor is found.
    #If this successor is in the closed set, it is reasonable to assume that it might have it's own
    # children nodes. THese also has to be updated with new G values.
    def propagatePathImprovements(self, parent):
        for child in parent.get_children():
            if parent.get_G() + parent.arc_cost(child) < child.get_G():
                child.set_parent(parent)
                child.set_G( parent.get_G() + parent.arc_cost(child) )
                #F(C) auto calculated
                self.propagatePathImprovements(child)

#To support depth, breadth and best search using the same
#algorithm the open list has to have different modes of inserting
#and retrieving nodes. At initialization the mode determine how the add
#and pop method will function.
class Frontier(object):
    def __init__(self, mode):
        self.list = []
        self.mode = mode
        if mode is SearchMode.BEST:
            heapq.heapify(self.list)
        elif mode is SearchMode.BREADTH:
            self.list = deque([])

    #Add is only different if its a best first search. The node has to
    #be added, and the heap has to be reheapifyed.
    def add(self, node):
        if self.mode is SearchMode.BEST:
            heapq.heappush(self.list, node)
        else:
            self.list.append(node)

    #Popping works differently for all modes. For the best first search,
    #the node with the lowest F value is popped from the heap.
    #Depth, the list acts as a stack and the value last appended to the list is popped. FILO
    #Breadth, the list acts as a queue. FIFO. Only the best first uses knownledge about the
    #problem domain. The two others work blindly, and the pop method is the reason why.
    def pop(self):
        if self.mode is SearchMode.BEST:
            return heapq.heappop(self.list)
        elif self.mode is SearchMode.DEPTH:
            return self.list.pop()
        elif self.mode is SearchMode.BREADTH:
            return self.list.popleft()

    #If the G or/and H value change and therefore the F value, the heap has to
    #be sorted again. This can happen is a better path from one node to another is found.
    #This changes the G value.
    def reheap(self):
        if self.mode is SearchMode.BEST:
            self.list.sort()

    def size(self):
        return len(self.list)

    def __contains__(self, key):
        return key in self.list


#Enum for the different supported modes of search. Best,
#depth and breadth first search     
class SearchMode(Enum):
    BEST = 1
    DEPTH = 2
    BREADTH = 3