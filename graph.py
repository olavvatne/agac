#Simple object representation of a graph. 
#The GraphModel object constitute of NodeModel's
#and EdgeModel's. Object used as display model,
#and in the provisional representation for the
#a*-gac
class GraphModel(object):

    def __init__(self):
        self.vertices = {}
        self.edges = []

    def __repr__(self):
        nodes = ""
        for key in self.vertices:
            nodes += key + " "
        return nodes

    def add_edge(self, edge):
        self.edges.append(edge)

    def add_vertex(self, node):
        self.vertices[node.id] = node


    def get_vertex(self, id):
        return self.vertices[id]

class NodeModel(object):

    def __init__(self, id, x,y):
        #Will use this for dicts and lambdas
        self.id = "N" + str(id)
        self.x = x
        self.y = y

class EdgeModel(object):

    def __init__(self, node1, node2):
        self.sp = node1
        self.ep = node2