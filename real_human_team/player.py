from real_human_team.evaluation import *
from real_human_team.board_state import BoardState

class Player:
    thrown_tokens = 0
    tokens = []
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
        self.current_board_state = BoardState()

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
    
    def throw(self, pos, tokenType, board_state):
        move = 0
        if(self.thrown_tokens >= 9):
            return '9 Tokens already thrown. Limit reached'
        if(pos[0]<4-self.thrown_tokens):
            return 'Cannot throw to this position'
        else:
            for opossingToken in board_state["uppers"] + board_state["lowers"]:
                if((pos) == (opossingToken.x, opossingToken.y)):
                    move = whoWins(tokenType, opossingToken.type)

        if(move==1 or move == 0):
            tokens.append(Token(pos[0],pos[1],tokenType))
            self.thrown_tokens += 1
            return 'Successfully thrown to' + str(pos)

        if(move == -1):
            return 'This throw would result in defeat'

