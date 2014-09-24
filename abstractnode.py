from abc import ABCMeta, abstractmethod

#Node object, important for traversing the search graph. Abstract class
#that contain abstract methods that has to be implemented by subclasses.
#These abstract methods, is what constitute the specialization of the A*
#for this problem domain.
class Node(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.children = []
        self.parents = []

    #Generate successor nodes/states from itself.
    @abstractmethod
    def generate_successors(self):
        pass

    #A getter for the heuristic. The heuristic is the estimate of the nearness to
    #the goal the specific node is. In case of a distance A to B problem, 
    #the H is the admissable (no overestimates) distance from the goal from the nodes position.
    @abstractmethod
    def calc_H(self):
        pass

    #The actual distance from start to the node. The path cost.
    def get_G(self):
        return self.g

    def set_G(self, cost):
        self.g = cost

    #Each node has to have to generate a id, to assess the uniqueness of the node. 
    @abstractmethod
    def generate_id(self):
        pass

    #ArcCost from self to children. The pathcost from one node to another
    @abstractmethod
    def arc_cost(self, child):
        pass

    #If node is a solution
    @abstractmethod
    def is_solution(self):
        pass

    def add_child(self, node):
        self.children.append(node)

    def set_parent(self, node):
        #TODO: ONE PARENT?
        self.parents = []
        self.parents.append(node)

    def get_children(self):
        return self.children

    def get_parent(self):
        #TODO: ONE PARENT?
        if not self.parents:
            return None

        return self.parents[0]

    def calc_F(self):
        return self.get_G() + self.calc_H()

    def __lt__(self, other):
        return self.calc_F() < other.calc_F()

    #Representation for the GUI
    @abstractmethod
    def gui_representation(self):
        pass
