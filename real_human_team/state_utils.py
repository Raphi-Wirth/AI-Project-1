import json
import typing
import itertools
import collections

from util import print_board

class State(typing.NamedTuple):
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
    
    # When subclassing namedtuple, we should control creation of instances
    # using a separate classmethod, rather than overriding __init__.
    @classmethod
    def new(cls, upper_tokens, lower_tokens, all_hexes):
        return cls(
                # TODO: Instead of sorted tuples, implement a frozen bag?
                upper_tokens=tuple(sorted(upper_tokens)),
                lower_tokens=tuple(sorted(lower_tokens)),
                all_hexes=all_hexes,
            )

    # Following the alternative constructor idiom, we'll create a separate
    # classmethod to allow creating our first state from the data dictionary.
    @classmethod
    def from_json(cls, file):
        data = json.load(file)
        upper_tokens = (Token(Hex(r, q), s) for s, r, q in data["upper"])
        lower_tokens = (Token(Hex(r, q), s) for s, r, q in data["lower"])
        all_hexes = ALL_HEXES
        return cls.new(upper_tokens, lower_tokens, all_hexes)

    # The core functionality of the state is to compute its available
    # actions and their corresponding successor states.
    def actions_successors(self):
        for action in self.actions():
            yield action, self.successor(action)

    def actions(self):
        """
        Generate all available 'actions' (each 'action' is actually a
        collection of actions, one for each upper token).
        """
        xs = [x for x, _s in self.upper_tokens]
        occupied_hexes = set(xs)
        def _adjacent(x):
            return self.all_hexes & {x + y for y in HEX_STEPS}
        def _token_actions(x):
            adjacent_x = _adjacent(x)
            for y in adjacent_x:
                yield "SLIDE", x, y
                if y in occupied_hexes:
                    opposite_y = _adjacent(y) - adjacent_x - {x}
                    for z in opposite_y:
                        yield "SWING", x, z
        return itertools.product(*map(_token_actions, xs))
    
    def successor(self, action):
        # move all upper tokens
        new_upper_tokens = []
        for _a, x, y in action:
            # lookup the symbol (any token on this hex will do, since all
            # tokens here will have the same symbol since the last battle)
            s = [t.symbol for t in self.upper_tokens if t.hex == x][0]
            new_upper_tokens.append(Token(y, s))

        # where tokens clash, do battle
        # TODO: only necessary to check this at destinations of actions
        # (but then will have to find another way to fill the lists)
        safe_upper_tokens = []
        safe_lower_tokens = []
        for x in self.all_hexes:
            ups_at_x = [t for t in new_upper_tokens  if t.hex == x]
            los_at_x = [t for t in self.lower_tokens if t.hex == x]
            symbols = {t.symbol for t in ups_at_x + los_at_x}
            if len(symbols) > 1:
                for s in symbols:
                    p = BEATS_WHAT[s]
                    ups_at_x = [t for t in ups_at_x if t.symbol != p]
                    los_at_x = [t for t in los_at_x if t.symbol != p]
            safe_upper_tokens.extend(ups_at_x)
            safe_lower_tokens.extend(los_at_x)
        return self.new(safe_upper_tokens, safe_lower_tokens, self.all_hexes)

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

if __name__ == "__main__":
    lower_tokens = (Token(Hex(0,1), 'r'),)
    upper_tokens = (Token(Hex(2,1), 'R'),)
    state = State.new(upper_tokens, lower_tokens, ALL_HEXES)
    state.print()