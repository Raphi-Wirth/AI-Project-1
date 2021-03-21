class Token:
    def __init__(self,x,y,type):
        self.x = x
        self.y = y
        self.isAlive = True
        self.type = type

    def placement(self):
        return (self.x,self.y)
    
    def isAlive(self):
        return (self.isAlive)

    def kill(self):
        self.isAlive = False
    
    def move(self,x,y):
        self.x = x
        self.y = y

    def __str__(self):
        return f'Token is at ({self.x},{self.y}) and is of type "{self.type}"'
    





