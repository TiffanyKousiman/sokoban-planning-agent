"""
The functions and classes defined in this module will be called by a marker script. 
"""
import search 

class SokobanPuzzle(search.Problem):
    """
    An instance of the class 'SokobanPuzzle' represents a Sokoban puzzle.
    An instance contains information about the walls, the targets, the boxes
    and the worker.
    """
    def __init__(self, warehouse,initial=None,goal=None):
        
        # initialise a Sokoban Puzzle with the required environment elements (both static and dynamic) 
        self.worker = warehouse.worker
        self.boxes = warehouse.boxes
        self.weights = warehouse.weights
        self.targets = warehouse.targets
        self.walls = warehouse.walls
        self.ncols = warehouse.ncols
        self.nrows = warehouse.nrows
        
        # only initialise dynamic elements as the initial state
        if initial==None:
            self.initial=tuple([warehouse.worker] +warehouse.boxes)

    def actions(self, state):
        """
        Return the list of legal actions that can be executed in the given state.
        """
        # empty list L to store the legal actions
        L=[] 
        # get worker location from state
        w_x, w_y = state[0]
        # get boxes location from state
        boxes_location=state[1:]

        # all of the following conditions must be met for a move to be executable, take 'Right' action as an example:
            # condition 1: the right grid of the worker cannot be a wall
            # condition 2: a box is on the right grid of the worker, and the right grid to the box cannot be a wall
            # condition 3: a box is on the right grid of the worker, and the right grid to the box cannot be another box
        # same rules applied in validating actions "Left", "Down" and "Up"
    
        if (not (w_x+1,w_y) in self.walls) and (not ((w_x+1,w_y) in boxes_location and (w_x+2,w_y) in self.walls )) and (not ((w_x+1,w_y) in boxes_location and (w_x+2,w_y) in boxes_location )):
            L.append("Right")
        if (not (w_x-1,w_y) in self.walls) and (not ((w_x-1,w_y) in boxes_location and (w_x-2,w_y) in self.walls )) and (not ((w_x-1,w_y) in boxes_location and (w_x-2,w_y) in boxes_location )):
            L.append("Left")
        if (not (w_x,w_y+1) in self.walls) and (not ((w_x,w_y+1) in boxes_location and (w_x,w_y+2) in self.walls )) and (not ((w_x,w_y+1) in boxes_location and (w_x,w_y+2) in boxes_location )):
            L.append("Down")
        if (not (w_x,w_y-1) in self.walls) and (not ((w_x,w_y-1) in boxes_location and (w_x,w_y-2) in self.walls )) and (not ((w_x,w_y-1) in boxes_location and (w_x,w_y-2) in boxes_location )):
            L.append("Up")
        
        #Return all valid actions
        return L

    def result(self, state, action):
        """
        Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state).
        """

        # make an dictionary of action offsets for easier calculation of the new location tuples from actions 
        action_offset = {'Left' :(-1,0), 'Right':(1,0) , 'Up':(0,-1), 'Down':(0,1)}
        
        # defensive programming - affirm that the action is legal
        assert action in self.actions(state)  
        
        # retrieve worker location from state
        w_x, w_y = state[0]
        # change to a mutable list
        worker_location=list((w_x, w_y))

        # retrieve boxes location from state
        boxes_location=state[1:]
        # change to a mutable list
        boxes_location_list=list(boxes_location)

        # find the offset of the given action
        d_x,d_y=action_offset[action]
        # update worker location after the action
        worker_location=(w_x+d_x,w_y+d_y)
        
        # if it is a push move, update the box location
        if worker_location in boxes_location:
            # find out which box has been moved
            i_box=boxes_location_list.index(worker_location)
            # update the pushed box location (2 moves away from the worker)
            boxes_location_list[i_box]=(w_x+2*d_x,w_y+2*d_y)

        # return the updated state 
        return tuple([worker_location]+boxes_location_list)

    def goal_test(self, state):
        """
        This function overrides the parent's function in the Problem class. 
        Specific to this problem, this goal test is checking only the partial 
        state component - the boxes, against the goal, player is not involved.
        """
        # return true if all the boxes are found in the targets in any combinations
        return set(state[1:])== set(self.targets)

    def path_cost(self, c, state1, action, state2):
        """
        overrides the parent's path_cost() function to update the path cost with 
        the recent action with the consideration of the box weights. 
        If it is a push action, this function will add 1 (default move cost) plus the weight of 
        pushed box to the input path cost c.
        """
        
        # if none of the boxes has weight, simply return input cost c + 1
        if all(item == 0 for item in self.weights):
            return c+1

        # otherwise if any box has weight
        else:          
            # increment c by 1 if no box has been pushed
            if(state1[1:]==state2[1:]):
                return c+1
            # if a box has been pushed, add 1 + the weight of the pushed box to c
            else:
                moved_box = [element for element in state1[1:] if element not in state2[1:]]
                i_moved_box=state1[1:].index(moved_box[0])
                return c+1+self.weights[i_moved_box]

    def h(self, n):
        """
        Heuristic cost for a current state to the goal state.
        
        """
        # defensive programming - assert that the number of targets = number of boxes
        assert len(self.targets)==len(self.boxes)
        
        # heuristic cost of the current state to the goal state
        h_costs=0
        
        ## Step 1: worker to box
        # Calculate the Manhattan distance from worker to each box which is not in the target
        # Add the maximum distance to h_costs
        boxNotInTarget = [box for box in n.state[1:] if box not in self.targets]
        w_to_b=[]
        
        # get the worker location
        w_x,w_y=n.state[0]
        
        for i in range(len(boxNotInTarget)):            
            b_x,b_y=boxNotInTarget[i]
            w_to_b.append(abs(b_x-w_x)+abs(b_y-w_y))
        
        if w_to_b:
            h_costs+=max(w_to_b)
            
        ## Step 2: box to target
        # Calculate the Manhattan distances from each box to all targets
        # Add the minimal distance (distance of a box to its nearest target) to h_costs
        for i in range(len(self.boxes)):
            distances=[]
            b_x,b_y=n.state[1:][i]      
            for j in range(len(self.targets)):
                t_x,t_y=self.targets[j]
                distances.append(abs(b_x-t_x)+abs(b_y-t_y))
            # if the box has no weight, only add the Manhattan distance to the nearest target to the h_costs
            if self.weights[i]==0:
                h_costs+=min(distances)
            # if the box has weight, add the distance to the closest target multiplied by the box weight
            else:
                h_costs+=min(distances)*self.weights[i]
       
        return h_costs
        

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def check_elem_action_seq(warehouse, action_seq):
    """
    Determine if the sequence of actions listed in 'action_seq' is legal or not.
    
    Important notes:
      - a legal sequence of actions does not necessarily solve the puzzle.
      - an action is legal even if it pushes a box onto a taboo cell.
        
    @param warehouse: a valid Warehouse object

    @param action_seq: a sequence of legal actions.
           For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
           
    @return
        The string 'Impossible', if one of the action was not valid.
           For example, if the agent tries to push two boxes at the same time,
                        or push a box into a wall.
        Otherwise, if all actions were successful, return                 
               A string representing the state of the puzzle after applying
               the sequence of actions.  This must be the same string as the
               string returned by the method  Warehouse.__str__()
    """
    
    # initialise a SokobanPuzzle with the input warehouse object 
    sp=SokobanPuzzle(warehouse)
    
    # get the initial state
    state=sp.initial
        
    while(len(action_seq)>0):
        # return list of valid actions for a given state
        actions=sp.actions(state) 
        # remove the first element from the action_seq 
        action=action_seq.pop(0)
        # return 'Impossible' if the popped action is not legal
        if action not in actions:
            return 'Impossible'
        # otherwise, update the state with the legal action
        else:
            state=sp.result(state,action)
      
    # reposition the worker and the boxes in the original warehouse
    warehouse.worker=state[0]
    warehouse.boxes=list(state)[1:]
    
    # return warehouse string map if all actions in the action_seq are executable
    return warehouse.__str__()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def solve_weighted_sokoban(warehouse):
    """
    This function analyses the given warehouse.
    It returns the two items. The first item is an action sequence solution. 
    The second item is the total cost of this action sequence.
    
    @param 
     warehouse: a valid Warehouse object

    @return
    
        If puzzle cannot be solved 
            return 'Impossible', None
        
        If a solution was found, 
            return S, C 
            where S is a list of actions that solves
            the given puzzle coded with 'Left', 'Right', 'Up', 'Down'
            For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
            If the puzzle is already in a goal state, simply return []
            C is the total cost of the action sequence C
    """
    sp=SokobanPuzzle(warehouse)
    result=search.astar_graph_search(sp)
    if(result==None):
        return 'Impossible',None
    else:
        return result.solution(),result.path_cost

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -