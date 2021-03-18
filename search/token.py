class Token:

    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.isAlive = True

    def placement(self):
        return (self.x,self.y)
    
    def isAlive(self):
        return (self.isAlive)

    def kill(self):
        self.isAlive = False
    
    def move(self,x,y):
        self.x = x
        self.y = y
    





