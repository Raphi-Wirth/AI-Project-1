from real_human_team.state_utils import *
import math
import random

class Player:
    def __init__(self, player):
        # Init player
        self.player_type = player
        self.currentState = State.new([],[],ALL_HEXES,0,0)

    def action(self):
        # Determine the optimal move using minimax
        a = determineOptimalMove(self.currentState, 2, self.player_type[0], -math.inf, math.inf, True)
        return a[0][1]
    
    def update(self, opponent_action, player_action):
        # Get action in format that successor() can take
        action = (('u', player_action), ('l', opponent_action)) if self.player_type[0] == 'u' \
            else (('u', opponent_action), ('l', player_action))

        # Update state of board
        self.currentState = self.currentState.successor(action)


# Calculate evaluation function (moved outside of player class)
def calcStateHeuristic(state, player, opponent):
    evaluation = 0
    hexWeights = [((0,0), 40), ((0, -1), 40), ((0, 1), 40),
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
    if player == 'u':
        xs = [x for x, _s in state.upper_tokens]
        xs_occupied_hexes = set(xs)
        evaluation += (len(xs_occupied_hexes)-len(state.upper_tokens)) * 10.0
        for upperToken in state.upper_tokens:
            for h, weight in hexWeights:
                if upperToken.hex == h:
                    if upperToken.hex.r < -4+state.lower_throws and state.lower_throws < 9:
                        evaluation-=10
                    evaluation += weight
                    break
            for lowerToken in state.lower_tokens:
                if WHAT_BEATS[upperToken.symbol] == lowerToken.symbol:
                   # look up token in weights
                    for h, weight in hexWeights:
                        if lowerToken.hex == h:
                            evaluation -= weight
                            break
                    break
                if(BEATS_WHAT[upperToken.symbol]==lowerToken.symbol):
                    evaluation += 15 - Hex.dist(upperToken.hex,lowerToken.hex)
                if(BEATS_WHAT[lowerToken.symbol]==upperToken.symbol):
                    evaluation += Hex.dist(upperToken.hex,lowerToken.hex)
    if player == 'l':
        ys = [y for y, _s in state.lower_tokens]
        ys_occupied_hexes = set(ys) 
        evaluation += (len(ys_occupied_hexes)-len(state.lower_tokens)) * 10.0
        for lowerToken in state.lower_tokens:
            for h, weight in hexWeights:
                if lowerToken.hex == h:
                    evaluation += weight
                    if lowerToken.hex.r > 4-state.upper_throws:
                        evaluation-=10
                    break
            for upperToken in state.upper_tokens:
                if WHAT_BEATS[lowerToken.symbol] == upperToken.symbol:
                   # look up token in weights
                    for h, weight in hexWeights:
                        if upperToken.hex == h:
                            evaluation -= weight
                            break
                    break
                if(BEATS_WHAT[lowerToken.symbol]==upperToken.symbol):
                    evaluation += 15 - Hex.dist(upperToken.hex,lowerToken.hex)
                if(BEATS_WHAT[upperToken.symbol]==lowerToken.symbol):
                    evaluation += Hex.dist(upperToken.hex,lowerToken.hex)
    return evaluation * (-1 if opponent else 1)

    
#Code taken from https://www.youtube.com/watch?v=l-hh51ncgDI&ab_channel=SebastianLague
def determineOptimalMove(state, depth, player, alpha, beta, maximisingPlayer):
    if(player == 'u'):
        allActions = state.genUpActions()
    else:
        allActions = state.genLowerActions()
    random.shuffle(allActions)
    
    heuristics = []

    if depth == 0 or len(allActions) == 0:
        return ('do nothing', calcStateHeuristic(state, player, not maximisingPlayer))
    
    if maximisingPlayer:
        maxEval = -math.inf
        for action in allActions:
            transState = state.successor((action,)) 
            eval = determineOptimalMove(transState, depth-1, 'l' if player == 'u' else 'u', alpha, beta, False)
            if(eval[1] > maxEval):
                maxEval = eval[1]
                maxAction = action
            elif eval[1] == maxEval:
                if random.uniform(0,1) < 0.5:
                    maxAction = action
            alpha = max(alpha, eval[1])
            if(beta <= alpha):
                break
        return (maxAction, maxEval)    
    else:
        minEval = math.inf
        for action in allActions:
            transState = state.successor((action,)) 
            eval = determineOptimalMove(transState, depth-1, 'l' if player == 'u' else 'u', alpha, beta, True)
            if(eval[1]<minEval):
                minEval = eval[1]
                minAction = action
            elif eval[1] == minEval:
                if random.uniform(0,1) < 0.5:
                    minAction = action
            beta = min(beta, eval[1])
            if(beta <= alpha):
                break
        return (minAction, minEval)
    
        
if __name__ == "__main__":
    lower_tokens = []
    upper_tokens = []
    state = State.new(lower_tokens, upper_tokens, ALL_HEXES, 0, 0)
    for i in range(12):
        upperMove = determineOptimalMove(state, 2, 'u', -math.inf, math.inf, True)
        lowerMove = determineOptimalMove(state, 2, 'l', -math.inf, math.inf, True)
        print(upperMove[0])
        print(lowerMove[0])
        state = state.successor((upperMove[0],lowerMove[0]))
        state.print()
