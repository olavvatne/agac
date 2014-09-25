
from gac import ConstraintNetwork

#Problem specific class. The a*-gac only accept
#variables, constraints and domains so a specific problem in
#a specific format has to be converted to the general form.
#In this case VertexColoring takes a graph, and convert it to
#constraints, domains and variables.
class VertexColoring(object):

    #Prepares the constraint network from the graph.
    #Convert the graph and k into a variables, constraints and domain
    #the general arc consistency algorithm can solve.
    def convert_graph_to_cnet(graph, k):
        cn = ConstraintNetwork()
        for key,v in graph.vertices.items():
            cn.add_variable(v.id)
            cn.set_domain(v.id, list(range(k)))
        
        #Each edge translate to one constraint involving two vertices.
        #Since a neighboring vertex cant have the same color, the rule is
        #v1 != v2
        for e in graph.edges:
            v1 = e.sp.id
            v2 = e.ep.id
            cn.add_constraint([v1,v2], str(v1) + "!=" + str(v2))

        #When the ConstraintNetwork is returned it contains all domains,
        #constraints and variables necessary for running a*-gac
        return cn