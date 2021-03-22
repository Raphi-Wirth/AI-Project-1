"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
from search.util import print_board, print_slide, print_swing
from search.token import Token

# Generates a board dictionary in the format of the board printing
# function
def generate_board_dict(uppers,lowers,blocks):
    board_dict = {}
    for upper in uppers:
        board_dict[(upper.x,upper.y)] = f"{upper.type}, u"
    for lower in lowers:
        board_dict[(lower.x,lower.y)] = f"{lower.type}, l"
    for block in blocks:
        board_dict[(block.x,block.y)] = "block"
    return board_dict

def slide(current, uppers, lowers, blocks):
    for i in range(-1,2):
        if (i==0):
            continue
        for token in blocks:
            if ((uppers[current].x + i, uppers[current].y) == (token.x,token.y)):
                continue
            else:
                uppers[current].x = uppers[current].x + i
                return
    for i in range(-1,2):
        if (i==0):
            continue
        for token in blocks:
            if ((uppers[current].x, uppers[current].y + i) == (token.x,token.y)):
                continue
            else:
                uppers[current].y = uppers[current].y + i
                return
    for i in range(-1,2):
        if (i==0):
            continue
        for token in blocks:
            if ((uppers[current].x - i, uppers[current].y + i) == (token.x,token.y)):
                continue
            else:
                uppers[current].x = uppers[current].x - i
                uppers[current].y = uppers[current].y + i
                return
    
            
    
            


    
    """for token in dict:
        if(currentToken = token):
            continue
        else if(dict[token].x + dict[token].y + currentToken.x + currentToken.y is in [-1,0,1]):
            if(dict[token].type != 'block'):
                dict[currentToken] = token
                return"""


def main():
    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)

    # TODO:
    # Find and print a solution to the board configuration described
    # by `data`.
    # Why not start by trying to print this configuration out using the
    # `print_board` helper function? (See the `util.py` source code for
    # usage information).
    
    # Load in upper, lower and block tokens as seperate arrays (There
    # may be a more compact way to do this)
    upperTokens = []
    lowerTokens = []
    blockTokens = []
    for upperRaw in data['upper']:
        upper = Token(upperRaw[1], upperRaw[2], upperRaw[0])
        upperTokens.append(upper)
    for lowerRaw in data['lower']:
        lower = Token(lowerRaw[1], lowerRaw[2], lowerRaw[0])
        lowerTokens.append(lower)
    for blockRaw in data['block']:
        block = Token(blockRaw[1], blockRaw[2], "b")
        blockTokens.append(block)

    # Print board to show off function
    board = generate_board_dict(upperTokens,lowerTokens,blockTokens)
    print_board(board)
    slide(0,upperTokens,lowerTokens,blockTokens)
    board = generate_board_dict(upperTokens,lowerTokens,blockTokens)
    print_board(board)