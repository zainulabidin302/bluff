from collections import namedtuple
import random
import numpy as np
from time import sleep

FACES = ['❤', '♠', '◆', '♣']
VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
ACTIONS = ['BLUFF', 'PASS', 'PLAY']
assert len(FACES) == 4
assert len(VALUES) == 13


class Card(namedtuple('Card', ['face', 'value'])):
    __slots__ = ()

    def __init__(self, face=None, value=None):
        super().__init__()

    def __str__(self):
        return VALUES[self.value] + FACES[self.face]

    def __eq__(self, other):
        return self.face == other.face and self.value == other.value


class Player():
    def __init__(self, name='default', cards=[], bluf_prob=0.5):
        super().__init__()
        self.name = name
        self.cards = cards
        self._bluf = bluf_prob
        assert len(
            self.cards) > 0, f'Player must recieve a card when starting game.'

    def __str__(self):

        return f'Name({self.name})=' + " ".join([c.__str__() for c in self.cards])

    def empty(self):
        return len(self.cards) == 0

    def has_one_card(self):
        return len(self.cards) == 1

    def bluffing(self):
        return random.random() < self._bluf


class BaseGame():
    def __init__(self):
        super().__init__()

        self.MAX_CARDS = 52
        self.FACES = 4
        self.VALUES = 13


class Game(BaseGame):
    def __init__(self, n_players=2):
        super().__init__()

        self.n_players = 2

        self._dealt = []  # actual cards on the table
        self._called = []  # calls from the user
        self._n_last_cards = 0  # number of cards played by last player.

        self._players = []

        # action prob: bluff, pass, play
        self.model = np.random.dirichlet((np.arange(1, 4)))

        # when play, each player bluff with different prob
        self.bluf_model = np.random.dirichlet((np.arange(1, self.n_players+1)))

        # deal cards
        self._init_game()

    def _init_game(self):
        """
          Initialize the cards and deal it to the players.
        """
        cards = []
        for face in range(self.FACES):
            for value in range(self.VALUES):
                cards.append(Card(face=face, value=value))
        random.shuffle(cards)

        assert len(
            cards) == self.MAX_CARDS, f'Cards must be {self.MAX_CARDS} at initiliation.'

        if self.n_players % 2 == 0:
            n_cards = self.MAX_CARDS // self.n_players
            extra_cards = 0
        else:
            n_cards = self.MAX_CARDS // self.n_players
            # extra cards goes to last player for simplicity
            extra_cards = (n_cards * self.n_players) - self.MAX_CARDS

        for p in range(self.n_players-1):
            self._players.append(Player(
                name="Player_" + str(p),
                cards=cards[p * n_cards: p * n_cards + n_cards],
                bluf_prob=self.bluf_model[p]))

        self._players.append(Player(
            name="Player_" + str(self.n_players-1),
            cards=cards[(self.n_players - 1) * n_cards: (self.n_players - 1)
                        * n_cards + n_cards + extra_cards],
            bluf_prob=self.bluf_model[self.n_players-1]))

        assert (n_cards * self.n_players) + \
            extra_cards == self.MAX_CARDS, f'1. Cards must be {self.MAX_CARDS} after dealing.'
        assert (sum([len(p.cards) for p in self._players])
                ) == self.MAX_CARDS, f'2. Cards must be {self.MAX_CARDS} after dealing.'

    def __str__(self):
        s = f'Dealt=' + " ".join([c.__str__() for c in self._dealt])
        s += f'Called=' + " ".join([c.__str__() for c in self._called])

        return "\n".join([p.__str__() for p in self._players]) + "\n" + s

    def game_over(self):
        """
          Returns true when goas to one player.
        """
        return sum([int(p.empty()) for p in self._players]) == 1

    def first_move_of_round(self):
        return len(self._dealt) == 0

    def _pass_move(self, p, o):
        return

    def _call_bluf_move(self, player, opponent):
        bluf = any([self._delt[i] == self._called[i]
                    for i in range(len(self._dealt) - self._n_last_cards, len(self._dealt))])

        if bluf:
            player.cards.extend(self._dealt)
        else:
            opponent.cards.extend(self._dealt)

        self._dealt = []
        self._called = []

    def _play_move(self, player, opponent):

        if player.bluffing():
            # draw random two cards
            # draw random two cards again not the same

            how_many = np.random.randint(
                2, min(5, len(player.cards)))  # 2 3 or 4
            which = np.random.choice(
                range(len(player.cards)), how_many, replace=False)
            which_blufs = random.sample(range(len(player.cards)), 1)

            self._n_last_cards = how_many
            for w in which:
                self._dealt.append(player.cards[w])
                self._called.append(player.cards[which_blufs])
            for w in sorted(which.tolist(), reverse=True):
                del player.cards[w]

        else:
            how_many = np.random.randint(
                2, min(5, len(player.cards)))  # 2 3 or 4
            which = np.random.choice(
                range(len(player.cards)), how_many, replace=False)

            self._n_last_cards = how_many
            for w in which:
                self._dealt.append(player.cards[w])
                self._called.append(player.cards[w])
            for w in sorted(which.tolist(), reverse=True):
                del player.cards[w]

    def action(self, model):
        model = np.array(model)
        model /= model.sum()
        action = np.random.choice(3, 1, p=model)[0]
        print(f'playing {ACTIONS[action]}')

        if action == 0:
            return self._call_bluf_move
        elif action == 1:
            return self._pass_move
        elif action == 2:
            return self._play_move

    def play(self, player, opponent):
        if self.first_move_of_round():
            # because user can not play bluf in first round, prob of bluf is zero
            model = self.model
            model[0] = 0
            if player.has_one_card():
                # because user can't do anything.
                self._pass_move()  # pass to next user.
                return
            else:
                self.action(model)(player, opponent)
        else:
            if player.has_one_card():
                model = self.model
                model[2] = 0  # probability of playing is zero.

            self.action(self.model)(player, opponent)

    def run_episode(self):
        player_id = 0
        while not self.game_over():
            print(self)

            opponent = self._players[(player_id - 1) % self.n_players]
            player = self._players[player_id]
            print(f'Player {player.name}: ')
            self.play(player, opponent)

            player_id = (player_id + 1) % self.n_players

            a = input()
        losser = list(filter(lambda x: not x.empty(), self._players))

        print(f'episde ends: {losser.name} lost')
