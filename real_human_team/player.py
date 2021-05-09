from state_utils import *
import math
import random

class Player:
    thrown_tokens = 0
    tokens = []
    offensiveHeuristicWeight = 1
    defensiveHeuristicWeight = 1


    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        # put your code here
        self.player_type = player
        self.currentState = state.new([],[],state.all_hexes,0,0)

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        # put your code here


# Calculate evaluation function (moved outside of player class)
def calcStateHeuristic(state, player):
    # define hex weights
    hexWeights = [((0,0), 50), ((0, -1), 40), ((0, 1), 40),
                    ((0, 2), 30), ((0, -2), 30),
                    ((0, 3), 25), ((0, -3), 25), ((0, 4), 20),
                    ((0, -4), 20), ((-1, 0), 40), ((-1, 1), 40),
                    ((-1, -1), 30), ((-1, -2), 25), ((-1, 2), 30),
                    ((-1, 3), 25), ((-1, -3), 20),
                    ((-1, 4), 10), ((-2, 0), 30), ((-2, 1), 30),
                    ((-2, 2), 30), ((-2, -1), 25), ((-2, 3), 25),
                    ((-2, -2), 20), ((-2, 4), 25), ((-3, 0), 25),
                    ((-3, 1), 25), ((-3, 2), 25), ((-3, 3), 25),
                    ((-3, -1), 20), ((-3, 4), 20), ((-4, 0), 20),
                    ((-4, 1), 20), ((-4, 2), 20), ((-4, 3), 20), 
                    ((-4, 4), 20), ((1, -1), 40), ((1, 0), 40),
                    ((1, -2), 30), ((1, 1), 30), ((1, -3), 25),
                    ((1, 2), 25), ((1, 4), -20), ((1, 3), 20),
                    ((2, 0), 30), ((2, -1), 30), ((2, -2), 30),
                    ((2, -3), 25), ((2, 1), 25), ((2, -4), 20),
                    ((2, 2), 20), ((3, 0), 25), ((3, -1), 25),
                    ((3, -2), 25), ((3, -3), 25), ((3, -4), 20),
                    ((3, 1), 20), ((4, 0), 20), ((4, -1), 20),
                    ((4, -2), 20), ((4, -3), 20), ((4, -4), 20)]

    # loop through upper and lower tokens  (upper tokens positive, lower negative)
    evaluation = 0
    for upper in state.upper_tokens:
        # look up token in weights
        for h, weight in hexWeights:
            if upper.hex == h:
                evaluation += weight
    for lower in state.lower_tokens:
        for h, weight in hexWeights:
            if lower.hex == h:
                evaluation -= weight
    return evaluation * (1 if player == 0 else -1)
    
#Code taken from https://www.youtube.com/watch?v=l-hh51ncgDI&ab_channel=SebastianLague

def determineOptimalMove(state, depth, player, alpha, beta, maximisingPlayer):
    allActions = list(state.actions())
    if(player == 0):
        allUpActions = state.genUpActions()
        dummy = allUpActions[0]
    else:
        allLowerActions = state.genLowerActions()
        dummy = allLowerActions[0]
    
    heuristics = []

    if depth == 0:
        return (dummy, calcStateHeuristic(state, player))
    
    if maximisingPlayer:
        maxEval = -math.inf
        if(player == 0):
            for action in allUpActions:
                transState = state.successor((action,)) 
                eval = determineOptimalMove(transState, depth-1, player+1, alpha, beta, False)
                if(eval[1] > maxEval):
                    maxEval = eval[1]
                    maxAction = action
                alpha = max(alpha, eval[1])
                if(beta <= alpha):
                    break
            #print("Max")
            #print(action, maxEval)
            return (maxAction, maxEval)
        else:
            for action in allLowerActions:
                transState = state.successor((action,)) 
                eval = determineOptimalMove(transState, depth-1, player-1, alpha, beta, False)
                if(eval[1]>maxEval):
                    maxEval = eval[1]
                    maxAction = action
                alpha = max(alpha, eval[1])
                if(beta <= alpha):
                    break
            #print("Max")
            #print(action, maxEval)
            return (maxAction, maxEval)
    
    else:
        minEval = math.inf
        if(player == 0):
            for action in allUpActions:
                transState = state.successor((action,)) 
                eval = determineOptimalMove(transState, depth-1, player+1, alpha, beta, True)
                if(eval[1]<minEval):
                    minEval = eval[1]
                    minAction = action
                beta = min(beta, eval[1])
                if(beta <= alpha):
                    break
            #print("Min")
            #print(action, minEval)
            return (minAction, minEval)
        if(player == 1):
            for action in allLowerActions:
                transState = state.successor((action,)) 
                eval = determineOptimalMove(transState, depth-1, player-1, alpha, beta, True)
                if(eval[1]<minEval):
                    minEval = eval[1]
                    minAction = action
                beta = min(beta, eval[1])
                if(beta <= alpha):
                    break
            #print("Min")
            #print(action, minEval)
            return (minAction, minEval)
    
    
        
if __name__ == "__main__":
    lower_tokens = []
    upper_tokens = []
    state = State.new(lower_tokens, upper_tokens, ALL_HEXES, 0, 0)
    for i in range(8):
        upperMove = determineOptimalMove(state, 3, 0, -math.inf, math.inf, True)
        lowerMove = determineOptimalMove(state, 3, 1, -math.inf, math.inf, True)
        print(upperMove[0])
        print(lowerMove[0])
        state = state.successor((upperMove[0],lowerMove[0]))
        state.print()

    


