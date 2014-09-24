from copy import deepcopy
from collections import deque
import itertools
from abstractnode import Node
#Where the constraint network should be placed
#The subclass of abstractNode will utilize this class 
#getting code chucks and using revise, initilze
class ConstraintNetwork(object):

    def __init__(self):
        self.variables = []
        self.domain = {}
        self.constraints = {}
    #Add a new variable for the general constraint satisfaction problem
    def add_variable(self, v):
        self.variables.append(v)
        self.constraints[v] = []


    #The string c will be converted to a function using lambda, and
    #associated with the correct variables.
    def add_constraint(self, variable_list, expression):
        for potential_var in variable_list:
            self.check_variable(potential_var)

        constraint_function = self.makefunc(variable_list, expression)
        constraint = Constraint(constraint_function, variable_list)

        #Add the constraint to each variable part of the expression
        #The expressions associated with a variable can easily be retrieved
        for variable in variable_list:
            self.constraints[variable].append(constraint)
    
    def check_variable(self, v):
        if v not in self.variables:
            raise Exception("Variable " + str(v) + " not found in network")

    def check_domain(self, d):
        #Check if list. Just for convenience
        pass

    #Sets the domain d for a variable v
    def set_domain(self, v, d):
        self.check_variable(v)
        self.check_domain(d)
        self.domain[v] = d

    #Returns all constraints that involve the variable v
    def get_constraints(self, v):
        return self.constraints[v]

    def create_instance(self):
        return ConstraintInstance(self, self.variables, self.domain)

    def makefunc(self,var_names, expression, envir=globals()):
        args = ""
        for n in var_names:
            args = args + "," + n
        return eval( "(lambda " + args[1:] + ": " + expression + ") " , envir)


class Constraint(object):
    def __init__(self, constraint, variables):
        self.function = constraint
        self.variables = variables


#The constraintInstance is a restricted instance of the constraintNetwork object
#It has pointers to the constraints, copies of a potentially restricted domain for each variable
class ConstraintInstance(object):
    def __init__(self, network, v,d):
        self.queue = deque()
        self.variables = v
        self.domain = deepcopy(d)
        self.cnet = network

    def revise(self, v, c):
        revised = False
        constraint = c.function
        domains = []
        for vi in c.variables:
            if vi != v:
                domains.append(self.domain[vi])
        
        for focal_value in self.domain[v]:
            retain = False
            for non_focal in itertools.product(*domains):
                #Retrain focal_value if for some non_focal combination
                #satisfies the constraint
                
                if constraint(focal_value, *non_focal):
                    retain = True
            if not retain:
                revised = True
                self.domain[v].remove(focal_value)
        #if revised:
            #print("Revised " + str(v))
        return revised

    def copy_object(self):
        return ConstraintInstance(self.cnet, self.variables, self.domain)

    def is_contradictory(self):
        for key, domain in self.domain.items():
            if len(domain) == 0:
                return True
        return False

    #GAC heuristic
    def get_next_assumption(self):
        smallest = float("inf")
        small_variable = None
        for v in self.variables:
            domain_size = len(self.domain[v])
            if domain_size<smallest and domain_size > 1:
                smallest = domain_size
                small_variable = v
        return small_variable

    def domain_filtering(self):
        while self.queue:
            variable, constraint = self.queue.popleft()
            reduced = self.revise(variable, constraint)
            if reduced:
                #If the domain is reduced, other domains might
                #need be reduced because of constraint between 
                #the current variable and other variables.
                for c in self.cnet.get_constraints(variable):
                    if c is not constraint:
                        revise_request = (variable, c)
                        self.queue.append(revise_request)
                    for v in c.variables:
                        if v is not variable:
                            revise_request =(v, c)
                            self.queue.append(revise_request)
                

    #Helper method for adding all revise request combination for a variable v
    #constraints
    def add_constraints_to_queue(self, v):
        for c in self.cnet.get_constraints(v):
            revise_request = (v, c)
            self.queue.append(revise_request)

    def initialize(self):
        #Schedule a revise for all variables.
        for v in self.variables:
            for c in self.cnet.get_constraints(v):
                revise_request = (v, c)
                self.queue.append(revise_request)

            
    #Given that an assumtion was made about a variable.
    # X's domain is set to a value
    def rerun(self, assumption):
        for c in self.cnet.get_constraints(assumption):
            for v in c.variables:
                if v is not assumption:
                    self.add_constraints_to_queue(v)

        self.domain_filtering()

class GacNode(Node):

    def __init__(self, instance, is_root=False):
        super().__init__()
        self.ci = instance
        if is_root:
            self.ci.initialize()
            self.ci.domain_filtering()

    def generate_successors(self):
        successors = []
        v = self.ci.get_next_assumption()
        if v:
            for value in self.ci.domain[v]:
                potential_instance = self.ci.copy_object()
                potential_instance.domain[v] = [value]
                potential_instance.rerun(v)
                if not potential_instance.is_contradictory():
                    successors.append(GacNode(potential_instance))
        print("Created " + str(len(successors)) + " number of successors")
        return successors

    #successors heuristic based on the total size of the instance variable domains
    #Possible closer to a solution if more domains have been reduced.
    def calc_H(self):
        domain_size = 0
        for key, domain in self.ci.domain.items():
            domain_size += len(domain)
        return domain_size-1

    def generate_id(self):
        #TODO: Better way?
        unique = ""
        for key, domain in self.ci.domain.items():
            for value in domain:
                unique += str(value) + ","
            unique +=":"
        return unique

    def arc_cost(self, child):
        return 1

    def is_solution(self):
        for key, domain in self.ci.domain.items():
            if(len(domain) is not 1):
                return False
        return True

    def gui_representation(self):
        value_reduction = []
        for key, domain in self.ci.domain.items():
            if len(domain) == 1:
                value_reduction.append((key, domain[0]))
            else:
                value_reduction.append((key, -1))
        return value_reduction

    #How the node should represent itself if printed.
    def __repr__(self):
        return self.ci
