from token import Token

def throw(pos, tokenType, uppers, lowers, player):
    move = 0
    if(player == 'upper'):
        if(upperTokensThrown >= 9):
            return '9 Tokens already thrown. Limit reached'
        if(pos[0]<4-upperTokensThrown):
            return 'Cannot throw to this position'
        else:
            for opossingToken in uppers + lowers:
                if((pos) == (opossingToken.x, opossingToken.y)):
                    move = whoWins(tokenType, opossingToken.type)
    if(player == 'lower'):
        if(lowerTokensThrown >= 9):
            return '9 Tokens already thrown. Limit reached'
        if(pos[0]>-4+lowerTokensThrown):
            return 'Cannot throw to this position'
        else:
            for opossingToken in uppers + lowers:
                if((pos) == (opossingToken.x, opossingToken.y)):
                    move = whoWins(tokenType, opossingToken.type)
    if(move==1 or move == 0 and player =='upper'):
        uppers.append(Token(pos[0],pos[1],tokenType))
        upperTokensThrown += 1
        return 'Successfully thrown to' + str(pos)
    if(move==1 or move == 0 and player =='lower'):
        lowers.append(Token(pos[0],pos[1],tokenType))
        lowerTokensThrown += 1
        return 'Successfully thrown to' + str(pos)
    if(move == -1):
        return 'This throw would result in defeat'

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

# Uses the A* pathfinding algorithm to find the shortest path
# and returns that path as an array of 3-tuples (x, y, moveType)
def findPath(token, uppers, lowers, blocks):
    # Keep track of open and closed cells
    # Open = search the cell for children
    # Closed = don't search that cell anymore
    openList = []
    closedList = []

    # Make cell for the first position
    start = Cell((token.x,token.y),None,"")
    openList.append(start)

    while len(openList) > 0:
        current = openList[0]
        
        # Remove from open and add to closed
        openList.pop(0)
        closedList.append(current)

        # If closest target has position 0 then path has been found
        closestDistance = calcClosestTarget(Token(current.pos[0],current.pos[1],token.type),lowers)[0]
        if closestDistance == 0:
            # Iterate through parent nodes and add to list
            path = []
            while current != None:
                path.append((current.pos[0],current.pos[1],current.moveType))
                current = current.parent
            return path[::-1]
        
        # Get children from calcStates
        childrenPositions = calcStates(Token(current.pos[0],current.pos[1],token.type),uppers,lowers,blocks,0)
        children = []
        for (x,y,moveType) in childrenPositions:
            children.append(Cell((x,y), current, moveType))
        
        for child in children:
            # If child position is in closed positions, continue
            cont = False
            for closed in closedList:
                if child.pos == closed.pos:
                    cont = True
            if cont:
                continue
            
            # Calculate path costs and heuristics for cell
            child.pathCost = current.pathCost + 1
            child.totalCost = child.pathCost + closestDistance

            # If this pathcost is more expensive than the same positions prev pathcost
            # then continue
            for op in openList:
                if op.pos == child.pos and child.pathCost > op.pathCost:
                    cont=True
            if cont:
                continue
            
            # Add child to list and sort the list
            openList.append(child)
        
        # Sort the open cells list by total cost
        sorted(openList, key=lambda op: op.totalCost)
    # Return empty path if no path found
    return []