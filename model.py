from __future__ import division
# compatibility code. Python version < 3 handles division differently than
# you'd expect.
# Now, this was written in Python 3.4, which is not completely backwards-
# compatible, and it's been long enough since I used v2 that I don't know if
# this all will work in it anyway. I think it will.

""" MODEL NOTES """

import random
# import library named random.

### Helper functions
def pairs(sequence):
    """For a sequence (1, 2, 3, 4, ...), generate a new sequence:
(1, 2), (1, 3), (1, 4), ..., (2, 3), (2, 4), ..., (3, 4), ..."""
    first, *rest = sequence
    while rest:
        for r in rest:
            yield (first, r)
        first, *rest = rest
        

def reverse_value_sort(mapping):
    """Given a mapping between keys and values, sort the keys by values,
sorting in reverse order. (sort greatest value to least value)."""
    return sorted(mapping.keys(), # a sequence of keys
                  key=mapping.get, # get sort value for key
                  reverse=True) # sort in reverse order


### Actual useful code.
class StrengthVector(dict):
    """map items to their strengths"""

# dict is short for dictionary: a one-to-one map or associative list from each
# object to another. Python docs say a dictionary maps keys to values.
#
# Here, we're mapping that items under comparison to their respective strength
# values, also bundling some other useful code with it.

    def normalize(self):# self is this object, or its scope
        # this parameter gets silently bound to a new object when we
        # initialize that object
        "Normalize all strength values so the sum over all of them equals 1"
        # Why is this necessary. It's complicated. Having to do with
        # log-likeliehood and optimizations and convergence and I learned a
        # lot about logarithms that I'd forgotten but all you need to know is
        # "The sum of each items' strength values must be equal to one. If
        # it isn't, normalize it so it is."""
        # This isn't the only possible normalization function, it's just the
        # least buggy. I do have some ideas to improve it. This code is
        # modular enough that should be easyish.
        vector_sum = sum(self.values())
        # dict.values() returns a list of the dict's values
        for item, strength in self.items():
            self[item] = strength / vector_sum
            # dict[key] is the normal way to access a value for a key
            # dict[key] = x then sets the value of dict[key] to x

    def random_item(self):
        """return a random key from self"""
        try:
            return random.choice(list(self.keys()))
        except IndexError:
            return None
        
        # random.choice picks a random element from a sequence
        # self.keys() returns all the keys in the dictionary
        # then we have to convert it to a list for annoying reasons, namely
        # that random.choice expects it

        # if there is no data, return None (a null value)



class GameData(dict):
    """store game outcomes

store outcomes as (winner, loser) pairs mapped to record, where record is
the number of games played with that outcome"""

    def __missing__(self, key):
        # normally, if you try to access a key which is not in the dictionary
        # instead of a value, you raise an exception called KeyError, telling
        # you that the key is not in the dictionary.
        # What this bit of code does is, when you try to access a key
        # that's not in the dict, it will return the value 0
        return 0
        
    def add_outcome(self, winner, loser):
        """add the (win, lose) outcome to the dataset"""
        self[(winner, loser)] += 1
        # if (winner, loser) hasn't already been put in the data,
        # self[(winner, loser)] returns, 0, per self.__missing__
        # otherwise self[(winner, loser)] just returns whatever value is
        # stored. Regardless, we increment that value by 1

    def total_wins(self, winner):
        "return the total number of times winner has won across all games."
        total = 0
        for (w, _), record in self.items():
            # dict.items() returns a list of (key, value) pairs.
            # "for (w, _), record ... " uses some pattern matching constructs.
            # Don't know if Java has this kind of thing, so:
            #   a, b = 1, 2
            # is just the same as
            #   a = 1
            #   b = 2
            # and
            #   (a, b), c = (1, 2), 3
            # is just
            #   a, b = 1, 2
            #   c = 3
            # so (win, lose), record = ((winner, loser), strength) for each
            # pair in self ( _ is just a variable name for a value I don't
            # care about enough to really name, since I don't do anything
            # with it.)
            if winner == w:
                total += record
        return total

    def total_games(self, x, y):
        """return the total number of games played between x and y, ignoring
which won"""
        if x == y:
            return 0
            # this is convention; it doesn't make sense to have a game where
            # x vs. x, so the output is always 0
        else:
            return self[(x, y)] + self[(y, x)]


# Here's where it get's complicated.
class Model(object):
    # constants
    START_STRENGTH = 0.5
    
    def __init__(self, items, preserve_order=True):
    # __init__ inititializes or constructs an object. Normal subclass
    # inheritance rules; not necessary in the classes above because
    # dict.__init__ already does what I need
        strength_data = self.strength_data = StrengthVector()
        game_data = self.game_data = GameData()
        # if this looks odd, think of it this way
        # x = y sets a variable local to this scope
        # self.x = y sets a variable global to the object's scope
        # x = self.x = y does both; you get a attribute "x" you can
        # anywhere with object.x, but it saves me from typing self.x
        # while I'm in this method definition.

        if preserve_order is True:
            for item in items:
                strength_data[item] = self.START_STRENGTH
            for winner, loser in pairs(items):
                game_data.add_outcome(winner, loser)
        else:
            # We don't care about the initial state of our input data,
            # so seed the model with random information and let it work
            # itself out.
            for item in items:
                strength_data[item] = self.START_STRENGTH
            for _ in (1, 2): # do this a couple times:
                for x, y in pairs(items):
                    if random.getrandbits(1): # get a random bit
                        # 1 is boolean True
                        game_data.add_outcome(x, y)
                    else:
                        # 0 is boolean False
                        game_data.add_outcome(y, x)
        self.update_strengths()

        
    def win_probability(self, x, y):
        """Caluculate the probability that x beats y."""
        x_strength = self.strength_data[x]
        try:
            return x_strength / (x_strength + self.strength_data[y])
        except ZeroDivisionError:
            return 0.5
            # x has strength of 0 and y has a strength of 0
            # the outcome of a game is 50/50; unpredictable

            # Fun fact! I don't think I ever use this code. Seems like it
            # should go here though.


    def update_strengths(self):
        strengths = self.strength_data # WHY did I name that attribute
        # strength_data. Jesus that's so hard to type. Nevermind that it's
        # you know, semantically, whatever, easy to remember, strengh_datd
        # is... nevermind seld.strnght_stad.
        # But then, this is a little Python optimization tricl too.
        # when you do self.attribute, Python's interpreter has to search the
        # object's namespace (which can get very expensive) each time.
        # sometimes you want that, but usually it's quicker to bind to
        # a more local namspace and save yrself some typing too.
        strengths.normalize()
        games = self.game_data
        new_strengths = dict()

        # MAGIC CODE
        # got this algorithm from
        
        # http://projecteuclid.org/euclid.aos/1079120141

        # Formula 3, according to my notes.
        # Basically, iterating over all the items and their strengths and
        # updating them based on game data. It's hard to explain why I think
        # it makes sense but it seems to work so...
        for x, x_strength in strengths.items():
            summation = 0
            x_wins = games.total_wins(x)
            for y, y_strength in strengths.items():
                if x != y:
                    total_games = games.total_games(x, y)
                    denominator = x_strength + y_strength
                    if denominator:
                        summation += total_games / denominator
                else:
                    pass
            new_strengths[x] = x_wins * (1 / summation)

        strengths.update(new_strengths)

    def rank1(self):
        """Rank items by reverse-sorting them on their strength values."""
        # also not the best ranking, but good for diagnostics.
        return reverse_value_sort(self.strength_data)

    def rank2(self):
        """Another, more complex rank sorting algorithm.

The idea is this: given strength values for every item, if you pit item x
against every other item, what proportion of those matches do you expect
x will win? Then, sort items by that ratio."""
        # seems to do the trick.
        data = dict()
        strengths = self.strength_data
        for item in strengths:
            data[item] = 0

        x, *ys = strengths
        while ys: # recognize this algorithm? Hint: pairs
            x_strength = strengths[x]
            for y in ys:
                y_strength = strengths[y]

                win_prob = x_strength / (x_strength + y_strength)
                lose_prob = y_strength / (x_strength + y_strength)

                if win_prob > lose_prob:
                    data[x] += 1
                else:
                    data[y] += 1

            x, *ys = ys

        return reverse_value_sort(data)

    def __contains__(self, item):
        """Is item in model?"""
        return item in self.strength_data



class Interface(object):
    # This code is just to give you an idea how to interact with the model
    # Try:
    #   I = Interface(items)
    #   I.loop()
    # to run interactive shell. Warning: it's very simple and fragile, but
    # it does work.
    def __init__(self, items, preserve_order=True):
        self.model = Model(items, preserve_order)
        self.already_ranked = set()
        self.get_random_item = self.model.strength_data.random_item

    # memory code
    def hash_pair(self, first, second):
        return hash(first) ^ hash(second)

    def know(self, first, second):
        return self.hash_pair(first, second) in self.already_ranked

    def remember(self, first, second):
        self.already_ranked.add(self.hash_pair)

    # game code
    def add_item(self, item):
        # You can add an item, but you cannot add an item to the dataset
        # unless you rate it against an item that's already in the data set.
        if item not in self.model:
            while 1:
                other = self.get_random_item()
                outcome = present_game(item, other)
                if outcome:
                    self.remember(*outcome)
                    self.model.game_data.add_outcome(*outcome)
                    self.model.strength_data[item] = self.model.START_STRENGTH
                    break

    def game(self):
        first = self.get_random_item()
        while 1:
            second = self.get_random_item()
            if first == second:
                continue
            elif self.know(first, second):
                continue
            else:
                return self.present_game(first, second)
                

    def present_game(self, first, second):
        print("Which one is better?")
        print("\tA:", first)
        print("\tB:", second)
        while 1:
            IN = input(">? ").strip()
            if IN in 'Aa':
                return (first, second)
            elif IN in 'Bb':
                return (second, first)
            elif IN in ('?', 'pass'):
                return False
            else:
                print("Type A or B to choose, or type pass or ? for a tie.")
        
    def play_rounds(self, N=10):
        for _ in range(N):
            outcome = self.game()
            if outcome:
                self.remember(*outcome)
                self.model.game_data.add_outcome(*outcome)
        self.model.update_strengths()

    def loop(self, rounds=10):
        #  do a read, input, output loop
        print("Hi! Type 'start' to start, or 'help' for more information.")
        while 1:
            IN = input("?> ").strip()
            if IN == 'start':
                print("How many rounds? (10 by default.)")
                IN = input(" please type a number greater than 0 >? ").strip()
                if IN:
                    self.play_rounds(int(IN))
                else:
                    self.play_rounds(10)
            elif IN == 'help':
                print("""start        start games
help        print this help
quit        end session and exit
list        print a ranked list of items
""")
            
            elif IN == 'quit':
                print("Goodbye!")
                break
            elif IN == 'list':
                print("Rank\tItem")
                for rank, item in enumerate(self.model.rank2()):
                    print("#{}\t{}".format(rank+1, item))
            else:
                print("Invalid command: {}".format(IN))
                print("Type help for a list of commands.")
