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
        offensiveHeuristicValue =100 - offensiveHeuristicValue
        return (offensiveHeuristicValue + defensiveHeuristicValue)
    
def minmax(state):
    originalState = state
    allActions = list(state.actions())
    allHeuristics = []
    initialHeuristics = []
    player = Player('u')
    for i in allActions:
        testingState = state.successor(i)
        initialHeuristics.append(player.calcStateHeuristic(testingState.upper_tokens,testingState.lower_tokens))
    minHeuristic = min(initialHeuristics)
    maxHeuristic = max(initialHeuristics)
    print(minHeuristic, maxHeuristic)
    #count = 0
    for action in allActions:
        testingState = state.successor(action)
        if (player.calcStateHeuristic(testingState.upper_tokens, testingState.lower_tokens) >= 0.15*maxHeuristic
        or player.calcStateHeuristic(testingState.upper_tokens, testingState.lower_tokens) <= 0.15*minHeuristic):
            continue
        allNextActions = testingState.actions()
        currentHeuristics = []
        for secondAction in allNextActions:
            #count += 1
            secondTestingState = testingState.successor(secondAction)
            currentHeuristics.append((player.calcStateHeuristic(secondTestingState.upper_tokens, secondTestingState.lower_tokens), secondAction))
        currentHeuristics.sort(key = lambda tup: tup[0])
        allHeuristics.append((action,currentHeuristics[-1]))
    allHeuristics.sort(key = lambda tup : tup[1][0])
    print(allHeuristics[-1])
    state = state.successor(allHeuristics[-1][0])
    state.print()
    return state


def determineOptimalMove(state, turn, layers):
    player = Player(turn)
    allActions = list(state.actions())
    if(turn == 0):
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
    if(turn == 0): 
        if(layers == 0):
            for action in allUpActions:
                transState = state.successor((action,dummy)) 
                newState = State.new(transState.upper_tokens, state.lower_tokens, ALL_HEXES, transState.upper_throws, state.lower_throws)
                heuristics.append((action, player.calcStateHeuristic(newState.upper_tokens, newState.lower_tokens)))
            heuristics.sort(key = lambda tup : tup[1], reverse = True) 
            return heuristics[0]
        else:
            backTrackHeuristics = []
            for action in allUpActions:
                transState = state.successor((action, dummy))
                newState = State.new(transState.upper_tokens, state.lower_tokens, ALL_HEXES, transState.upper_throws, state.lower_throws)
                backTrackHeuristics.append(determineOptimalMove(newState, turn+1,layers-1))
            backTrackHeuristics.sort(key=lambda tup : tup[1], reverse = True)
            return backTrackHeuristics[0]
    if(turn == 1):
        if(layers == 0):
            for action in allLowerActions:
                transState = state.successor((dummy, action)) 
                newState = State.new(state.upper_tokens, transState.lower_tokens, ALL_HEXES, state.upper_throws, transState.lower_throws)
                heuristics.append((action, player.calcStateHeuristic(newState.lower_tokens, newState.upper_tokens)))
            heuristics.sort(key = lambda tup : tup[1], reverse = True) 
            return heuristics[0]
        backTrackHeuristics = []
        for action in allLowerActions:
            transState = state.successor((dummy,action))
            newState = State.new(state.upper_tokens, transState.lower_tokens, ALL_HEXES, state.upper_throws, transState.lower_throws)
            backTrackHeuristics.append(determineOptimalMove(newState, turn-1,layers-1))
        backTrackHeuristics.sort(key = lambda tup : tup[1], reverse = True)
        return backTrackHeuristics[0]

    
        
if __name__ == "__main__":
    lower_tokens = (Token(Hex(0,1), 'r'),)
    upper_tokens = (Token(Hex(2,1), 's'),)
    state = State.new(lower_tokens, upper_tokens, ALL_HEXES, 0, 0)
    for i in range(3):
        upperMove = determineOptimalMove(state, 0, 2)
        lowerMove = determineOptimalMove(state, 1, 2)
        state = state.successor((upperMove[0], lowerMove[0]))
        state.print()
    
    


