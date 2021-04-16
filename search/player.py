'''
Defines Player module that will be used to play
the game.
'''

class Player:
    tokens_thrown = 0
    def __init__(self, player):
        self.player_type = player
    
    def action(self):
        pass

    def update(self, opponent_action, player_action):
        pass