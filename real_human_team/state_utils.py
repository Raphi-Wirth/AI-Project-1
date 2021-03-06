import json
import typing
import itertools
import collections

from real_human_team.util import print_board

class State:
    # Note: By subclassing namedtuple, we get efficient, immutable instances
    # and we automatically get sensible definitions for __eq__ and __hash__.

    # This class stores the game state in the format of two lists:
    # One holding the positions and symbols of all upper tokens:
    upper_tokens: tuple
    # And one for all the lower tokens:
    lower_tokens: tuple
    # There is also a set of valid hexes (all of those not blocked by
    # block tokens):
    all_hexes:    frozenset
    # Hold information about how many times each player has thrown
    upper_throws: int
    lower_throws: int
    
    # When subclassing namedtuple, we should control creation of instances
    # using a separate classmethod, rather than overriding __init__.
    @classmethod
    def new(cls, upper_tokens, lower_tokens, all_hexes, upper_throws, lower_throws):
        return cls(
                # TODO: Instead of sorted tuples, implement a frozen bag?
                upper_tokens=tuple(sorted(upper_tokens)),
                lower_tokens=tuple(sorted(lower_tokens)),
                all_hexes=all_hexes,
                upper_throws = upper_throws,
                lower_throws = lower_throws,
            )

    # Following the alternative constructor idiom, we'll create a separate
    # classmethod to allow creating our first state from the data dictionary.
    @classmethod
    def from_json(cls, file):
        data = json.load(file)
        upper_tokens = (Token(Hex(r, q), s) for s, r, q in data["upper"])
        lower_tokens = (Token(Hex(r, q), s) for s, r, q in data["lower"])
        all_hexes = ALL_HEXES
        return cls.new(upper_tokens, lower_tokens, all_hexes, 0, 0)
    
    def __init__(self,upper_tokens, lower_tokens, all_hexes, upper_throws, lower_throws):
        self.upper_tokens = upper_tokens
        self.lower_tokens = lower_tokens
        self.all_hexes = all_hexes
        self.upper_throws = upper_throws
        self.lower_throws = lower_throws

    # The core functionality of the state is to compute its available
    # actions and their corresponding successor states.
    def actions_successors(self):
        for action in self.actions():
            yield action, self.successor(action)

    # Generate list of upper actions
    def genUpActions(self):
        # Get upper tokens 
        xs = [x for x, _s in self.upper_tokens]
        xs_occupied_hexes = set(xs)

        # Get adjacent hexes
        def _adjacent(x):
            return self.all_hexes & {x + y for y in HEX_STEPS}

        # Generate throws
        def _upper_throw_actions():
            if self.upper_throws >= 9:
                return
            for row in range(self.upper_throws+1):
                if 4-row >= 0:
                    col_range = range(-4, row+1)
                else:
                    col_range = range(-8+row, 4+1)
                for col in col_range:
                    for symbol in ['r','p','s']:
                        yield 'u', ('THROW', symbol, Hex(4-row, col))

        # Generate slides and swings
        def _upper_token_actions(x):
            adjacent_x = _adjacent(x)
            for y in adjacent_x:
                yield 'u', ("SLIDE", x, y)
                if y in xs_occupied_hexes:
                    opposite_y = _adjacent(y) - adjacent_x - {x}
                    for z in opposite_y:
                        yield 'u', ("SWING", x, z)
            adjacent_y = _adjacent(x)
        
        # Return upper actions
        upper_maps = map(_upper_token_actions,xs)
        upper_moves = list(_upper_throw_actions())
        for gen in upper_maps:
            upper_moves += [*gen]
        return upper_moves

    # Generate list of lower actions
    def genLowerActions(self):
        # Get lower tokens and occupied hexes
        ys = [y for y, _s in self.lower_tokens]
        ys_occupied_hexes = set(ys) 
        
        # Get adjacent hexes
        def _adjacent(x):
            return self.all_hexes & {x + y for y in HEX_STEPS}

        # Generate THROW actions
        def _lower_throw_actions():
            if self.lower_throws >= 9:
                return
            for row in range(self.lower_throws+1):
                if -4+row <= 0:
                    col_range = range(-row, 4+1)
                else:
                    col_range = range(-4, 8-row+1)
                for col in col_range:
                    for symbol in ['r','p','s']:
                        yield 'l', ('THROW', symbol, Hex(-4+row, col))

        # Generate SLIDE, SWING actions
        def _lower_token_actions(x):
            adjacent_y = _adjacent(x)
            for y in adjacent_y:
                yield 'l', ("SLIDE", x, y)
                if y in ys_occupied_hexes:
                    opposite_y = _adjacent(y) - adjacent_y - {x}
                    for z in opposite_y:
                        yield 'l', ("SWING", x, z)
            adjacent_y = _adjacent(x)
        
        # Return list of lower actions
        lower_maps = map(_lower_token_actions, ys)
        lower_moves = list(_lower_throw_actions())
        for gen in lower_maps:
            lower_moves += [*gen]
        return lower_moves
    
    def successor(self, action):
        # move upper and lower tokens
        new_upper_tokens = list(self.upper_tokens)
        new_lower_tokens = list(self.lower_tokens)
        new_upper_throws = self.upper_throws
        new_lower_throws = self.lower_throws
        for p, (_a, x, y) in action:
            # lookup the symbol (any token on this hex will do, since all
            # tokens here will have the same symbol since the last battle)
            if p == 'u':
                # Add new token if thrown
                if _a == 'THROW':
                    new_upper_tokens.append(Token(y, x))
                    new_upper_throws += 1
                    continue
                # Lookup symbol if SLIDE or SWING
                for t in range(len(new_upper_tokens)):
                    if new_upper_tokens[t].hex == x:
                        s = new_upper_tokens[t].symbol
                        new_upper_tokens.pop(t)
                        break
                #s = [t.symbol for t in self.upper_tokens if t.hex == x][0]
                new_upper_tokens.append(Token(y, s))
            
            if p == 'l':
                # Add new token if thrown
                if _a == 'THROW':
                    new_lower_tokens.append(Token(y, x))
                    new_lower_throws += 1
                    continue
                for t in range(len(new_lower_tokens)):
                    if new_lower_tokens[t].hex == x:
                        s = new_lower_tokens[t].symbol
                        new_lower_tokens.pop(t)
                        break
                new_lower_tokens.append(Token(y, s)) 

        # where tokens clash, do battle
        # TODO: only necessary to check this at destinations of actions
        # (but then will have to find another way to fill the lists)
        safe_upper_tokens = []
        safe_lower_tokens = []
        for x in self.all_hexes:
            ups_at_x = [t for t in new_upper_tokens  if t.hex == x]
            los_at_x = [t for t in new_lower_tokens if t.hex == x]
            symbols = {t.symbol for t in ups_at_x + los_at_x}
            if len(symbols) > 1:
                for s in symbols:
                    p = BEATS_WHAT[s.lower()]
                    ups_at_x = [t for t in ups_at_x if t.symbol != p]
                    los_at_x = [t for t in los_at_x if t.symbol != p]
            safe_upper_tokens.extend(ups_at_x)
            safe_lower_tokens.extend(los_at_x)
        return self.new(safe_upper_tokens, safe_lower_tokens, self.all_hexes, 
                        new_upper_throws, new_lower_throws)

    # For easier debugging, a helper method to print the current state.
    def print(self, message="", **kwargs):
        board = collections.defaultdict(str)
        for t in self.upper_tokens:
            board[t.hex] += t.symbol.upper()
        for t in self.lower_tokens:
            board[t.hex] += t.symbol.lower()
        for x, s in board.items():
            board[x] = f"({s})"
        print_board(board, message, **kwargs)
    
    def generate_string(self):
        board_string = ''
        for t in self.upper_tokens:
            board_string += str(t)
        for t in self.lower_tokens:
            board_string += str(t)
        return board_string


# (Some classes and constants supporting the implementation above)

class Hex(typing.NamedTuple):
    """
    Hexagonal axial coordinates with basic operations and hexagonal
    manhatten distance.
    Thanks to https://www.redblobgames.com/grids/hexagons/ for some
    of the ideas implemented here.
    """
    r: int
    q: int

    @staticmethod
    def dist(x, y):
        """
        Hexagonal manhattan distance between two hex coordinates.
        """
        z_r = x.r - y.r
        z_q = x.q - y.q
        return (abs(z_r) + abs(z_q) + abs(z_r + z_q)) // 2

    def __add__(self, other):
        # this special method is called when two Hex objects are added with +
        return Hex(self.r + other[0], self.q + other[1])

HEX_RANGE = range(-4, +4+1)
ALL_HEXES = frozenset(
        Hex(r, q) for r in HEX_RANGE for q in HEX_RANGE if -r-q in HEX_RANGE
    )
HEX_STEPS = [Hex(r, q) for r, q in [(1,-1),(1,0),(0,1),(-1,1),(-1,0),(0,-1)]]

BEATS_WHAT = {'r': 's', 'p': 'r', 's': 'p'}
WHAT_BEATS = {'r': 'p', 'p': 's', 's': 'r'}

class Token(typing.NamedTuple):
    hex:    Hex
    symbol: str