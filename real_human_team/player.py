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
    
    def calcStateHeuristic(self, upperTokens, lowerTokens):
        offensiveHeuristicValue = 0
        defensiveHeuristicValue = 0
        for upperToken in upperTokens:
            for lowerToken in lowerTokens:
                if (lowerToken.symbol == BEATS_WHAT[upperToken.symbol]):
                    defensiveHeuristicValue += Hex.dist(upperToken.hex, lowerToken.hex)*self.defensiveHeuristicWeight
                elif (upperToken.symbol == BEATS_WHAT[lowerToken.symbol]):
                    offensiveHeuristicValue += Hex.dist(upperToken.hex, lowerToken.hex)*self.offensiveHeuristicWeight
        if defensiveHeuristicValue>100:
            defensiveHeuristicValue = 100
        offensiveHeuristicValue = 8*len(lower_tokens) - offensiveHeuristicValue
        return (offensiveHeuristicValue + defensiveHeuristicValue)
    
#Code taken from https://www.youtube.com/watch?v=l-hh51ncgDI&ab_channel=SebastianLague

def determineOptimalMove(state, depth, player, alpha, beta, maximisingPlayer):
    _player = Player('u')
    allActions = list(state.actions())
    if(player == 0):
        dummy = allActions[0][0]
    else:
        dummy = allActions[0][1]
    allUpActions = []
    allLowerActions = []
    for action in allActions:
        allUpActions.append(action[0])
        allLowerActions.append(action[1])
    allUpActions = list(dict.fromkeys(allUpActions))
    allLowerActions = list(dict.fromkeys(allLowerActions))
    heuristics = []
    
    

    if depth == 0:
        if(player==0):
            return (dummy, _player.calcStateHeuristic(state.upper_tokens, state.lower_tokens))
        if(player==1):
            return (dummy, _player.calcStateHeuristic(state.lower_tokens, state.upper_tokens))
    
    if maximisingPlayer:
        maxEval = -math.inf
        if(player == 0):
            for action in allUpActions:
                transState = state.successor((action,dummy)) 
                newState = State.new(transState.upper_tokens, state.lower_tokens, ALL_HEXES, transState.upper_throws, state.lower_throws)
                eval = determineOptimalMove(newState, depth-1, player+1, alpha, beta, False)
                if(eval[1] > maxEval):
                    maxEval = eval[1]
                    maxAction = action
            #print("Max")
            #print(action, maxEval)
            return (maxAction, maxEval)
        else:
            for action in allLowerActions:
                transState = state.successor((dummy, action)) 
                newState = State.new(state.upper_tokens, transState.lower_tokens, ALL_HEXES, state.upper_throws, transState.lower_throws)
                eval = determineOptimalMove(newState, depth-1, player-1, alpha, beta, False)
                if(eval[1]>maxEval):
                    maxEval = eval[1]
                    maxAction = action
            #print("Max")
            #print(action, maxEval)
            return (maxAction, maxEval)
    
    else:
        minEval = math.inf
        if(player == 0):
            for action in allUpActions:
                transState = state.successor((action,dummy)) 
                newState = State.new(transState.upper_tokens, state.lower_tokens, ALL_HEXES, transState.upper_throws, state.lower_throws)
                eval = determineOptimalMove(newState, depth-1, player+1, alpha, beta, True)
                if(eval[1]<minEval):
                    minEval = eval[1]
                    minAction = action
            #print("Min")
            #print(action, minEval)
            return (minAction, minEval)
        if(player == 1):
            for action in allLowerActions:
                transState = state.successor((dummy, action)) 
                newState = State.new(state.upper_tokens, transState.lower_tokens, ALL_HEXES, state.upper_throws, transState.lower_throws)
                eval = determineOptimalMove(newState, depth-1, player-1, alpha, beta, True)
                if(eval[1]<minEval):
                    minEval = eval[1]
                    minAction = action
            #print("Min")
            #print(action, minEval)
            return (minAction, minEval)
    
    
        
if __name__ == "__main__":
    lower_tokens = []
    upper_tokens = []
    state = State.new(lower_tokens, upper_tokens, ALL_HEXES, 0, 0)
    for i in range(2):
        upperMove = determineOptimalMove(state, 4, 0, True)
        lowerMove = determineOptimalMove(state, 4, 1, True)
        print(upperMove[0])
        print(lowerMove[0])
        state = state.successor((upperMove[0],lowerMove[0]))
        state.print()

    


