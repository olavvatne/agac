from copy import deepcopy
from collections import deque
import itertools
from abstractnode import Node

#The ConstraintNetwork object contain the domain, variables
#and constraints defining a problem. To utilize 
#A*-gac a specific problem has to be converted into
#variables, constraints and domains. In this general form
#the revise algorithm can be used to incrementally 
#restrict the domain until all variables have a domain
#of only 1 entry. This is a solution.
#The actual algorithm recide in the ConstraintInstance, where
#limiting domains are done. The constraintNetwork are mostly used
#for converting, bookkeeping and retrieving constraints.
class ConstraintNetwork(object):

    def __init__(self):
        self.variables = []
        self.domain = {}
        self.constraints = {}

    #Add a new variable to the network
    #All variables should also have a domain
    #So for each variable the set_domain method has
    #to be called
    def add_variable(self, v):
        self.variables.append(v)
        self.constraints[v] = []

    #Convienience method
    def add_variable_and_domain(self, v, d):
        self.add_variable(v)
        self.set_domain(v,d)

    #The list of variables and string expression will be converted
    #to a constraint involving 1 or more variables. 
    #A function is dynamically generated using lambda, and this
    #function is then associated with each of the variables in 
    #the variable_list
    def add_constraint(self, variable_list, expression):
        for potential_var in variable_list:
            self.check_variable(potential_var)

        constraint_function = self.makefunc(variable_list, expression)
        constraint = Constraint(constraint_function, variable_list)

        #Add the constraint to each variable part of the expression
        #The expressions associated with a variable can easily be retrieved
        for variable in variable_list:
            self.constraints[variable].append(constraint)
    
    #Check if variable is actually in network
    def check_variable(self, v):
        if v not in self.variables:
            raise Exception("Variable " + str(v) + " not found in network")

    #Checks if domain is set
    def check_domain(self, d):
        #Check if list. Just for convenience
        pass

    #Sets the domain d for a variable v.
    #Argument d should be a list containing values
    #that the lambda functions can utilize.
    def set_domain(self, v, d):
        self.check_variable(v)
        self.check_domain(d)
        self.domain[v] = d

    #Returns all constraints that involve the variable v.
    #Can be used to see how many constraints an variable is
    #involved in or similar.
    def get_constraints(self, v):
        return self.constraints[v]

    #Creates a ConstraintInstance containing pointer to
    #the variables and the full constraint network. The 
    #domain is copied, since it's typically restriced.
    def create_instance(self):
        return ConstraintInstance(self, self.variables, self.domain)

    #Converts a string expression to a full fledged function!
    def makefunc(self,var_names, expression, envir=globals()):
        args = ""
        for n in var_names:
            args = args + "," + n
        return eval( "(lambda " + args[1:] + ": " + expression + ") " , envir)


#Simple Constraint object containing function and the variables
#involved in the constraint. A constraint function is meaningless
#unless the variables is known. 
class Constraint(object):
    def __init__(self, constraint, variables):
        self.function = constraint
        self.variables = variables


#The constraintInstance is a restricted instance of the constraintNetwork object
#It has pointers to the constraints and copies of the potentially restricted
#domains.
class ConstraintInstance(object):
    def __init__(self, network, v,d):
        self.queue = deque()
        self.variables = v
        self.domain = deepcopy(d)
        self.cnet = network

    #The general revise method will potensially restrict
    #v's domain after testing the domain against the constraint
    #c. The constraint can involve n non_focal variables. This is ok,
    #since v domain is tested against the cross product of the non_focal variables'
    #domains. 
    def revise(self, v, c):
        revised = False
        constraint = c.function
        domains = []

        #The domains of all variables involved in constraint is added to a list
        #expect v's domain.
        for vi in c.variables:
            if vi != v:
                domains.append(self.domain[vi])
        
        #Each value in v's domain has to be tested, to see if it deserves to be 
        #retained in the domain.
        for focal_value in self.domain[v]:
            retain = False
            for non_focal in itertools.product(*domains):
                #Retrain focal_value if for some non_focal combination
                #satisfies the constraint. If there does not exist such
                #a combination, it will be removed from v's domain
                
                if constraint(focal_value, *non_focal):
                    retain = True
            if not retain:
                revised = True
                self.domain[v].remove(focal_value)
        #If values has been removed from v's domain true is returned.
        #Important since v smaller domain might have an impact on other
        #variables connected to v through constraints
        return revised

    #Makes a copy of itself where the variables domains are deepcopied.
    #Used when generating successors.
    def copy_object(self):
        return ConstraintInstance(self.cnet, self.variables, self.domain)

    #If any of the domains in the instance is empty, it becomes
    #contradictory and not worth persuing for a solution anymore.
    def is_contradictory(self):
        for key, domain in self.domain.items():
            if len(domain) == 0:
                return True
        return False

    def variable_contradictory(self, v):
        if len(self.domain[v]) == 0:
            return True
        return False

    #GAC heuristic. The choice of which node should be used
    #when making assumptions is important and has a big impact.
    #The variable with the smallest domain but bigger than one is returned.
    def get_next_assumption(self):
    #TODO: Should find variable with most constraints attached?
        smallest = float("inf")
        small_variable = None
        for v in self.variables:
            domain_size = len(self.domain[v])
            if domain_size<smallest and domain_size > 1:
                smallest = domain_size
                small_variable = v
        return small_variable

    #The core of general arc consistency. The queue contains
    #tuples of variable constaint pairs to be tested by the revise algorithm
    #If the revise reduces a domain the other variables and costraint 
    #related to the reduced variable has to be added to the queue for 
    #further testing. This process will propagate domain change until 
    #the instance becomes stable and no more domain reduction is possible.

    def domain_filtering(self):
        while self.queue:
            variable, constraint = self.queue.popleft()
            reduced = self.revise(variable, constraint)
            if reduced:
                if self.variable_contradictory(variable):
                    return
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

    #Init the revise process. Puts all pairs of variable and constraint
    #in the queue. 
    def initialize(self):
        #Schedule a revise for all variables.
        for v in self.variables:
            for c in self.cnet.get_constraints(v):
                revise_request = (v, c)
                self.queue.append(revise_request)

            
    #Given that an assumtion was made about a variable.
    # X's domain is set to a value, and the change of X's domain
    #has to be propagated to the other variables.
    #For all constraints the assumption variable is a part of,
    #retrive other "neighbor" variables and add these to the queue 
    def rerun(self, assumption):
        for c in self.cnet.get_constraints(assumption):
            for v in c.variables:
                if v is not assumption:
                    self.add_constraints_to_queue(v)

        self.domain_filtering()

    def count_unsatisfied_constraints(self):
        unsatisfied = 0
        for key,c in self.cnet.constraints.items():
            satisfied = True
            for c_v in c.variables:
                if len(self.domain[c_v]) != 1:
                    satisfied = False
            if not satisfied:
                unsatisfied += 1
        return unsatisfied

    def __repr__(self):
        output =""
        for v in self.variables:
            output += str(v) + ": "
            for d in self.domain[v]:
                output += str(d) + ", "
            output +="\n"
        return output + "\n"


#GacNode extends the abstract Node class. The class therefore contains
#all the method neccesary to run an a* search. 
#    -generate_successors
#    -calc_H
#    -generate_id
#    -is_solution
#    -arc_cost
#The gacNode integrate the general arc consistency problem with search
#All GacNode has a reference to a ConstraintInstance, which mean
#domain_filtering and the other methods can be run from this class.
class GacNode(Node):

    def __init__(self, instance, is_root=False):
        super().__init__()
        self.ci = instance
        if is_root:
            #If this is the rootnode in the search tree the constraint instance
            #domain has to be reduced before continueing.
            self.ci.initialize()
            self.ci.domain_filtering()

    #Generate_sucessors consult the constraint instance for getting the next
    #variable to use for an assumption. An assumption make a guess for a 
    #specific variable, and therefore reduce the domain to a single value.
    #Returns a list of successors where 1 variable has been assumed, generating
    #a successor for each of the values in the variables domain. Not added
    #if successor is contradictory (A domain has no values, no solution possible)
    def generate_successors(self):
        successors = []
        v = self.ci.get_next_assumption()
        if v:
            for value in self.ci.domain[v]:
                potential_instance = self.ci.copy_object()
                potential_instance.domain[v] = [value]
                potential_instance.rerun(v)
                #After running rerun the constaint instance's domain
                #has been reduced and hopefully not contradictory.
                #The rerun does inferences on the domains using constraints.
                if not potential_instance.is_contradictory():
                    successors.append(GacNode(potential_instance))
        #print("Created " + str(len(successors)) + " number of successors")
        return successors

    #search heuristic based on the total size of the instance variable domains
    #Possible closer to a solution if more domains have been reduced. 
    #Not an admissable heuristic
    def calc_H(self):
        domain_size = 0
        for key, domain in self.ci.domain.items():
            domain_size += len(domain)
        return domain_size-1

    #How the node id itself. The a star can use the returned value to check
    #if node has been generated before or not, and avoids duplicates in the search
    #tree
    def generate_id(self):
        unique = ""
        for key, domain in self.ci.domain.items():
            for value in domain:
                unique += str(value) + ","
            unique +=":"
        return unique

    #arc_cost the same between all GacNodes.
    def arc_cost(self, child):
        return 1

    #Check if all the domains in the constraint instance has
    #been reduced exactly to the size of one. If this has happened
    #a solution has been found.  
    def is_solution(self):
        for key, domain in self.ci.domain.items():
            if(len(domain) is not 1):
                return False
        return True

    #The display add tuples to a list containing name of variable
    #and a the chosen value. If the domain has not yet been reduced to 1
    #-1 is appended. Still ensure that partial solutions can be represented.
    def gui_representation(self, generated, popped):
        data = {}
        value_reduction = []
        for key, domain in self.ci.domain.items():
            if len(domain) == 1:
                value_reduction.append((key, domain[0]))
            else:
                value_reduction.append((key, -1))
        data["values"] = value_reduction
        data["generated"] = generated
        data["popped"] = popped
        data["solution"] = self.is_solution
        data["assumption"] = self.get_level()
        data["unsatisfied"] = self.ci.count_unsatisfied_constraints()

        return data

    #How the node should represent itself if printed.
    def __repr__(self):
        return repr(self.ci)
