from state_utils import *

class Player:
    thrown_tokens = 0
    tokens = []
    offensiveHueristicWeight = 1
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
                    defensiveHeuristicValue += Hex.dist(upperToken.hex, lowerToken.hex)*self.defensiveHueristicWeight
                elif (upperToken.symbol == BEATS_WHAT[lowerToken.symbol]):
                    offensiveHeuristicValue += Hex.dist(upperToken.hex, lowerToken.hex)*self.offensiveHueristicWeight
        return (offensiveHeuristicValue + defensiveHeuristicValue)
    
def minmax(state):
    originalState = state
    allActions = state.actions()
    allHeuristics = []
    player = Player('u')
    for action in allActions:
        testingState = state.successor(action)
        for upperToken in testingState.upper_tokens:
            print(upperToken)
        allHeuristics.append(player.calcStateHeuristic(testingState.upper_tokens, testingState.lower_tokens), action)
    allHeuristics.sort(key = lambda tup: tup[0])
    print(allHeuristics[0])
        
if __name__ == "__main__":
    lower_tokens = (Token(Hex(0,1), 'r'),)
    upper_tokens = (Token(Hex(2,1), 's'),)
    print(Hex.dist(upper_tokens[0].hex,lower_tokens[0].hex))
    state = State.new(upper_tokens, lower_tokens, ALL_HEXES, 0, 0)
    minmax(state)

