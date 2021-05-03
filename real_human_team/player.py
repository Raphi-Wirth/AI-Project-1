from state_utils import *

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
        return (offensiveHeuristicValue + defensiveHeuristicValue)
    
def minmax(state):
    originalState = state
    allActions = state.actions()
    allHeuristics = []
    player = Player('u')
    for action in allActions:
        testingState = state.successor(action)
        allNextActions = testingState.actions()
        currentHeuristics = []
        for secondAction in allNextActions:
            secondTestingState = testingState.successor(secondAction)
            currentHeuristics.append((player.calcStateHeuristic(secondTestingState.upper_tokens, secondTestingState.lower_tokens), secondAction))
        currentHeuristics.sort(key = lambda tup: tup[0])
        allHeuristics.append((action,currentHeuristics[-1]))
    allHeuristics.sort(key = lambda tup : tup[1][0])
    #state.successor(allHeuristics[-1][0])
    print(allHeuristics[-1][0])
    print(allHeuristics[-1][1][1])
    #state.successor(allHeuristics[-1][1][1])
    print_board(state)
    
        
if __name__ == "__main__":
    lower_tokens = (Token(Hex(0,1), 'r'),)
    upper_tokens = (Token(Hex(2,1), 's'),)
    state = State.new(upper_tokens, lower_tokens, ALL_HEXES, 0, 0)
    minmax(state)

