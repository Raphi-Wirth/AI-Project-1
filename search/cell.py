class Cell:
    def __init__(self, pos, parent, moveType):
        self.pos = pos
        self.pathCost = 0
        self.parent = parent
        self.totalCost = 0
        self.moveType = moveType