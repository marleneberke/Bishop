# Built for Planner class to manage.
# Map has a simpler representation of the environment (no exit states),
# allowing Planner to build the deep transition matrix.

# Structure is a little different. Planner handles how to build
# the MDP.

import numpy as np
import sys
import math

class Map(object):

    """
    Map class.

    This class stores the environments states (S) and the terrain type (StateTypes), the possible actions (A), the transition matrix (T), and reward locations (Locations).
    It also stores human-readable information: StateNames, ActionNames, and LocationNames.

    Map comes with functions that help you build the transition matrix (BuildGridWorld).
    The Map specification is not the map we do planning on. Planner takes the Map description and uses it to build the true MDP (where objects can be removed).
    """

    def __init__(self, Locations=[[], [], [], []], S=[], StateTypes=[], StateNames=[], A=[], diagonal=None, ActionNames=[], LocationNames=[], T=[]):
        """
        Create New map

        If no arguments are provided the structures are just initialized.

        ARGUMENTS:
        Locations[]      An array marking the locations of the targets.
                         There are four possible types of objects. Each entry
                         marks the locations of object 1, object 2, agent 1, and
                         agent 2, respectively.
        S                Set of states in the world.
        StateTypes[]     A set that matches in length the set of states and marks their
                         terrain type (As a discrete number).
        StateNames       A list containing names for each possible state type.
        A                Set of actions the world allows for
        diagonal         [boolean] determines if agents can travel diagonally.
        ActionNames      Names of the actions
        LocationNames    List containing names of the objects taht are placed on the map.
                         LocationNames[i] contains the names of objects in Locations[i]
        T                Transition matrix. T[so,a,sf] contains the probability of switching
                         to state sf when taking action a in state so.
        """
        self.diagonal = diagonal
        self.S = S
        self.A = A
        self.T = T
        self.ActionNames = ActionNames
        self.Locations = Locations
        self.LocationNames = LocationNames
        self.StateNames = StateNames
        self.StateTypes = StateTypes
        # Ensure rest of code breaks if BuildGridWorld wasn't called.
        self.x = -1
        self.y = -1

    def BuildGridWorld(self, x, y, diagonal=True):
        """
        Build a simple grid world with a noiseless transition matrix.
        This gives the basic structure that can then be used to build the MDPs real transition matrix.

        ARGUMENTS
        x [integer]     Map's length
        y [integer]     Map's height
        diagonal [boolean] Can agent move diagonally?
        """
        self.x = x
        self.y = y
        self.diagonal=diagonal
        WorldSize = x * y
        self.S = range(WorldSize)
        self.StateTypes = [0] * len(self.S)
        if diagonal:
            self.A = range(8)
            self.ActionNames = ["L", "R", "U", "D", "UL", "UR", "DL", "DR"]
        else:
            self.A = range(4)
            self.ActionNames = ["L", "R", "U", "D"]
        self.LocationNames = ["Object A", "Object B", "Agent A", "Agent B"]
        #From, With, To
        self.T = np.zeros((len(self.S), len(self.A), len(self.S)))
        # Make all states of the same type
        self.StateTypes = [0] * (len(self.S))
        for i in range(len(self.S)):
            # Moving left
            if (i % x == 0):
                self.T[i, 0, i] = 1
            else:
                self.T[i, 0, i - 1] = 1
            # Moving right
            if (i % x == x - 1):
                self.T[i, 1, i] = 1
            else:
                self.T[i, 1, i + 1] = 1
            # Moving up
            if (i < x):
                self.T[i, 2, i] = 1
            else:
                self.T[i, 2, i - x] = 1
            # Moving down
            if (i + x >= WorldSize):
                self.T[i, 3, i] = 1
            else:
                self.T[i, 3, i + x] = 1
            if diagonal:  # Add diagonal transitions.
	            if ((i % x == 0) or (i < x)):  # Left and top edges
	                self.T[i, 4, i] = 1
	            else:
	                self.T[i, 4, i - x - 1] = 1
	            if ((i < x) or (i % x == x - 1)):  # Top and right edges
	                self.T[i, 5, i] = 1
	            else:
	                self.T[i, 5, i - x + 1] = 1
	            if ((i % x == 0) or (i + x >= WorldSize)):  # Bottom and left edges
	                self.T[i, 6, i] = 1
	            else:
	                self.T[i, 6, i + x - 1] = 1
	            # Bottom and right edges
	            if ((i % x == x - 1) or (i + x >= WorldSize)):
	                self.T[i, 7, i] = 1
	            else:
	                self.T[i, 7, i + x + 1] = 1

    def InsertSquare(self, topleftx, toplefty, width, height, value):
        """
        InsertSquare(lowerleftx,lowerlefty,width,heigh,value)
        Replace a map square with the given value

        topleftx: x-value of the top left spot of the square, from left to right.
        toplefty: y-value of the top left spot of the square, from top to bottom.
        width: number of squares in width
        height: number of squares in height
        """
        if ((topleftx+width-1)>self.x) or ((toplefty+height-1)>self.y):
            print "ERROR: Square doesn't fit in map."
            return None
        TopLeftState=(toplefty-1)*self.x+(topleftx)-1
        for i in range(height):
            initial=TopLeftState+self.x*i
            end=TopLeftState+width+1
            self.StateTypes[initial:end] = [value] * width
        
    def GetActionList(self, Actions):
        """
        GetActionList(ActionList)
        Transform a list of action names into the corresponding action numbers in the Map.
        This function helps make inference code human-readable
        """
        ActionList = [0] * len(Actions)
        for i in range(len(Actions)):
            ActionList[i] = self.ActionNames.index(Actions[i])
        return ActionList

    def GetWorldSize(self):
        """
        GetWorldSize()
        returns number of states.
        """
        return len(self.S)

    def NumberOfActions(self):
        """
        NumberOfActions()
        returns number of actions.
        """
        return len(self.A)

    def GetActionNames(self, Actions):
        """
        GetActionNames(Actions)
        Receives a list of action numbers and returns the names for the actions.
        """
        ActionNames = [0] * len(Actions)
        for i in range(len(Actions)):
            ActionNames[i] = self.ActionNames[Actions[i]]
        return ActionNames

    def GetRawStateNumber(self, Coordinates):
        # Transform coordinates to raw state numbers.
        xval=Coordinates[0]
        yval=Coordinates[1]
        return (yval-1)*self.x+xval-1

    def GetCoordinates(self, State):
        yval = int(math.floor(State/self.x))+1
        xval = State - self.x*(yval-1)+1
        return [xval,yval]

    def InsertTargets(self, Locations):
        """
        InsertTargets(Locations)
        Adds objects to the map. Locations must be of the form [[],[],[],[]], with a total of two states.
        State numbers in the first list are objects of type 1. State numbers in the second list are objects of type 2.
        State numbers in the third and fourth lists are agents.

        Example:
        InsertTargets([0,1],[],[],[]) # Insert two objects of the same kind on states 0 and 1
        InsertTargets([0],[1],[],[]) # Insert two different objects on states 0 and 1
        InsertTargets([0],[],[1],[]) # Insert an object in state 0 and an agent who needs help in state 1
        InsertTargets([],[],[0,1],[]) # Insert two agents of the same kind on states 0 and 1. This means the algorithm will assume the motivation to save both agents is the same.
        InsertTargets([],[],[0],[1]) # Insert two different agents in states 0 and 1. This way, the agent might have different motivation for saving the different agents.
        """
        # Store the state position of the objects in the world.
        if sum(map(len, Locations)) > 2:
            print "Warning: More than two rewards on Map. Code will work, but this is a deviation from the experimental design."
        self.Locations = Locations

    def PullTargetStates(self, Coordinates=True):
        """
        PullTargetSTates(AddTerminalState=True)
        Returns a list of states that have an object in them.
        When Coordinates is set to false the function returns the raw state numbers
        """
        TargetStates = []
        for i in range(len(self.Locations)):
            discard = [TargetStates.append(j) for j in self.Locations[i]]
        if not Coordinates:
            return TargetStates
        else:
            return [self.GetCoordinates(item) for item in TargetStates]

    def AddStateNames(self, StateNames):
        """
        AddStateNames(StateNames) takes a list of the length of the terrain types giving them names.
        """
        self.StateNames = StateNames

    def PrintMap(self):
        """
        PrintMap()
        """
        sys.stdout.write("Possible actions: "+str(self.ActionNames)+"\n")
        sys.stdout.write("Diagonal travel: "+str(self.diagonal)+"\n")
        sys.stdout.write("Targets: ")
        sys.stdout.write(str(self.PullTargetStates(True))+"\n\n")
        print "Terrain types"
        for i in range(len(self.StateNames)):
            sys.stdout.write(self.StateNames[i]+": "+str(i)+"\n")
        sys.stdout.write("\n")
        for i in range(self.y):
            for j in range(self.x):
                sys.stdout.write(str(self.StateTypes[self.x*i+j]))
            sys.stdout.write("\n")

    def Display(self, Full=False):
        """
        Print class attributes.
        Display() prints the stored values.
        Display(False) prints the variable names only.
        """
        if Full:
            for (property, value) in vars(self).iteritems():
                print property, ': ', value
        else:
            for (property, value) in vars(self).iteritems():
                print property
