from token import Token

MAX_X = 4

# Calculate the manhattan distance between two points
def calcDistance(p1,p2):
    return (abs(p2[0]-p1[0]) + abs(p2[1]-p1[1]))

# Calculates distance to the closest target for a token
# as a 2-tuple (distance, target)
def calcClosestTarget(token, lowers):
    minimum = 9999
    target = None
    for lowerToken in lowers:
        if(whoWins(token.type, lowerToken.type)==1):
            distance = calcDistance((token.x,token.y),(lowerToken.x,lowerToken.y))
            if(distance<minimum):
                minimum = distance
                target = lowerToken
    return (minimum,target)

# Takes two token types, and returns the winner
def whoWins(type1, type2):
    if type1 == 'r':
        if type2 == 's':
            return 1
        if type2 == 'p':
            return -1
    if type1 == 's':
        if type2 == 'p':
            return 1
        if type2 == 'r':
            return -1
    if type1 == 'p':
        if type2 == 'r':
            return 1
        if type2 == 's':
            return -1
    return 0

def calcStates(token, uppers, lowers, blocks, isSwing):
    # States holds an array of (x, y, moveType)
    states = []
    for i in [(-1,1),(0,1),(-1,0),(1,0),(0,-1),(1,-1)]:
        blocked = False
        swing = False
        defeat = 0
        
        # Don't generate a state that is off the board
        if abs(token.x+i[0]) > MAX_X or abs(token.y+i[1]) > MAX_X:
            continue

        # Don't generate a state where a block token is
        for block in blocks:
            if ((token.x + i[0], token.y + i[1]) == (block.x,block.y)):
                blocked = True
                break
        
        # Don't generate a state where an opposing lower token is
        for lowToken in lowers:
            if ((token.x + i[0], token.y + i[1]) == (lowToken.x,lowToken.y)):
                if (whoWins(token.type,lowToken.type) == -1):
                    defeat = 1
                    break
        
        # Don't move into a position an opposing upper token is moving to
        for upper in uppers:
            if (upper.x,upper.y) == (token.x,token.y):
                continue
            if((token.x + i[0], token.y + i[1]) == upper.nextPosition):
                if (whoWins(token.type,upper.type) == -1 or whoWins(token.type,upper.type) == 1):
                    defeat = 1
                    break
        
        # Generate swing states if not already swinging
        if(isSwing == 0):
            for swingToken in uppers:
                if (token.x + i[0], token.y + i[1]) == (swingToken.x, swingToken.y):
                    swing = True
                    savedSwing = swingToken
                    break
        
        # Don't generate a state where the token may be defeated
        if(defeat == 1):
            continue

        # Don't generate a state where a block token is
        if(blocked == True):
            continue  

        # Generate swing states here
        if(swing == True):
            for element in calcStates(savedSwing,uppers,lowers,blocks,1):
                if((element[0],element[1]) == (token.x,token.y)):
                    continue
                states.append((element[0],element[1],"SWING"))
        else:
            states.append((token.x+i[0],token.y+i[1],"SLIDE"))  
    
    # Remove duplicates, putting priority on slides over swings
    temp = []
    for (x,y,moveType) in states:
        if moveType == "SLIDE":
            temp.append((x,y,moveType))
        elif not ((x,y,"SLIDE") in states):
            temp.append((x,y,moveType))
    return temp
