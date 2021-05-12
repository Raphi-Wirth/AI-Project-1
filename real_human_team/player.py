# This player punishs=es for entering THROW zone
# Punishes overlapping tokens
# Punishes tokens that are beaten
# Uses archery-target like weights

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
    # Define hex weights
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

    # Specific weights we can tune
    OVERLAP_WEIGHT = 10.0
    THROW_ZONE_WEIGHT = 10.0

    # loop through upper and lower tokens  (upper tokens positive, lower negative)
    evaluation = 0
    if player == 'u':
        # Punish upper for overlapping tokens
        xs = [x for x, _s in state.upper_tokens]
        xs_occupied_hexes = set(xs)
        evaluation += (len(xs_occupied_hexes)-len(state.upper_tokens)) * OVERLAP_WEIGHT

        # Add up weights for all upper tokens
        for upper in state.upper_tokens:
            # look up token in weights
            for h, weight in hexWeights:
                if upper.hex == h:
                    # Punish tokens for going in opposing throw zone
                    if upper.hex.r < -4+state.lower_throws and state.lower_throws < 9:
                        evaluation -= THROW_ZONE_WEIGHT
                    evaluation += weight
                    break

        # Subtract weights if lower token beats upper token
        for lower in state.lower_tokens:
            for upper in state.upper_tokens:
                if WHAT_BEATS[upper.symbol] == lower.symbol:
                    # look up token in weights
                    for h, weight in hexWeights:
                        if lower.hex == h:
                            evaluation -= weight
                            break
                    break
            
    if player == 'l':
        # Punish lower for overlapping tokens
        ys = [y for y, _s in state.lower_tokens]
        ys_occupied_hexes = set(ys) 
        evaluation += (len(ys_occupied_hexes)-len(state.lower_tokens)) * OVERLAP_WEIGHT

        # Add up weights for all lower tokens
        for lower in state.lower_tokens:
            # look up token in weights
            for h, weight in hexWeights:
                if lower.hex == h:
                    evaluation += weight
                    # Punish tokens for going in opposing throw zone
                    if lower.hex.r > 4-state.upper_throws and state.upper_throws < 9:
                        evaluation -= THROW_ZONE_WEIGHT
                    break
        
        # Subtract weights if upper token beats lower token
        for upper in state.upper_tokens:
            for lower in state.lower_tokens:
                if WHAT_BEATS[lower.symbol] == upper.symbol:
                    # look up token in weights
                    for h, weight in hexWeights:
                        if upper.hex == h:
                            evaluation -= weight
                            break
                    break

    # Flip evaluation function if we are minimising (if we are an opponent)
    return evaluation * (-1 if opponent else 1)

def sort_actions_key(state, action, player, maximisingPlayer, cache):
    new_state = state.successor((action,))
    cache[action] = new_state
    #value = calcStateHeuristic(new_state, player, not maximisingPlayer) 
    if player == 'u':
        value = len(new_state.upper_tokens) - len(new_state.lower_tokens)
    else:
        value = len(new_state.lower_tokens) - len(new_state.upper_tokens)
    return value
    
#Code taken from https://www.youtube.com/watch?v=l-hh51ncgDI&ab_channel=SebastianLague
global_cache = {}
def determineOptimalMove(state, depth, player, alpha, beta, maximisingPlayer):
    # Get actions
    if(player == 'u'):
        allActions = state.genUpActions()
    else:
        allActions = state.genLowerActions()

    # Cache actions and their successors
    cache = {}

    random.shuffle(allActions)
    allActions.sort(
        key=lambda x: sort_actions_key(state, x, player, maximisingPlayer, cache), 
        reverse=False 
    )

    # Order actions
    # sortedActions = sorted(
    #     allActions, 
    #     key=lambda x: sort_actions_key(state, x, player, maximisingPlayer, cache), 
    #     reverse=True 
    # )
    #print([calcStateHeuristic(state.successor((action,)), player, not maximisingPlayer) for action in sortedActions])
    #sortedActions = allActions
    #random.shuffle(sortedActions)

    #random.shuffle(allActions)
    #allActions = sortedActions
    
    heuristics = []

    # for key, val in global_cache.items():
    #     print(key, val)

    if depth == 0 or len(allActions) == 0:
        if((state.generate_string(), depth) in global_cache):
            return global_cache[(state.generate_string(), depth)]
        global_cache[(state.generate_string(), depth)] = ('',calcStateHeuristic(state, player, not maximisingPlayer))
        return global_cache[(state.generate_string(), depth)]
    
    if maximisingPlayer:
        maxEval = -math.inf
        for action in allActions:
            #transState = state.successor((action,))
            transState = cache[action]
            if (transState.generate_string(), depth-1) in global_cache:
                eval = global_cache[(transState.generate_string(), depth-1)][1]
            else:
                eval = determineOptimalMove(transState, depth-1, 'l' if player == 'u' else 'u', alpha, beta, False)[1]
            if(eval > maxEval):
                maxEval = eval
                maxAction = action
            # elif eval == maxEval:
            #     if random.uniform(0,1) < 0.5:
            #         maxAction = action
            alpha = max(alpha, eval)
            if(beta <= alpha):
                break
        global_cache[(state.generate_string(), depth)] = (maxAction,maxEval)
        return (maxAction, maxEval)    
    else:
        minEval = math.inf
        for action in allActions:
            #transState = state.successor((action,))
            transState = cache[action]
            if (transState.generate_string(), depth-1) in global_cache:
                eval = global_cache[(transState.generate_string(), depth-1)][1]
            else:
                eval = determineOptimalMove(transState, depth-1, 'l' if player == 'u' else 'u', alpha, beta, True)[1]
            if(eval<minEval):
                minEval = eval
                minAction = action
            # elif eval == minEval:
            #     if random.uniform(0,1) < 0.5:
            #         minAction = action
            beta = min(beta, eval)
            if(beta <= alpha):
                break
        global_cache[(state.generate_string(), depth)] = (minAction,minEval)
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
