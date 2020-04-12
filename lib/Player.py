import random
import numpy as np
from lib.constants import VALUES, FACES, MAX_CARDS
from lib.Card import Card
from copy import deepcopy
from json import dumps


class Cards:
    def __init__(self, cards=[]):
        super().__init__()
        self.cards = deepcopy(cards)
        self.cards.sort()

    def append(self, v):
        self.cards.append(v)
        self.cards.sort()

    def sort(self):
        self.cards.sort()

    def extend(self, v):
        l = v
        if isinstance(v, Cards):
            v = v.cards
        self.cards.extend(v)
        self.cards.sort()

    def __len__(self):
        return len(self.cards)

    def __iter__(self):
        return iter(self.cards)

    def __getitem__(self, index):
        return self.cards[index]

    def __setitem__(self, index, value):
        self.cards[index] = value

    def __delitem__(self, index):

        if isinstance(index, Card):
            for i, c in enumerate(self.cards):
                if c == index:
                    del self.cards[i]
                    return

        del self.cards[index]

    def __contains__(self, value):
        for c in self.cards:
            if c == value:
                return True
        return False

    def shuffle(self):
        random.shuffle(self.cards)

    def init_deck(shuffle=True):
        cards = []
        for fid, _ in enumerate(FACES):
            for vid, _ in enumerate(VALUES):
                cards.append(Card(face=fid, value=vid))

        assert len(
            cards) == MAX_CARDS, f'Cards must be {MAX_CARDS} at initiliation.'
        deck = Cards(cards=cards)
        if shuffle:
            deck.shuffle()
        return deck

    def split(self, n=2):
        if n % 2 == 0:
            n_cards = MAX_CARDS // n
            extra_cards = 0
        else:
            n_cards = self.MAX_CARDS // self.n_players
            extra_cards = (n_cards * self.n_players) - self.MAX_CARDS
        cards = []
        for p in range(n-1):
            cards.append(Cards(self.cards[p * n_cards: p * n_cards + n_cards]))
        cards.append(Cards(self.cards[(n - 1) * n_cards: (n - 1)
                                      * n_cards + n_cards + extra_cards]))
        return cards

    def unique(self):
        tmp = Cards()

        for c in self.cards:
            if c not in tmp:
                tmp.append(c)
        return tmp

    def counter_dict(self):
        count = {}
        tmp = self.unique()
        for vid, _ in enumerate(VALUES):
            for uniq_card in tmp:
                if uniq_card.value == vid:
                    a = count.get(vid, (0, uniq_card))
                    a = (a[0]+1, uniq_card)
                    count[vid] = a

        return count

    def make_empty(self):
        self.cards = []

    def moves(self):
        d = self.counter_dict()
        d = {k: v for k, v in d.items() if v[0] != 1}
        return d

    def get_cards_by_card(self, n, card, keep_in_deck=True):
        indices = []
        for i, c in enumerate(self.cards):
            if c.value_equal(card):
                indices.append(i)
        return self.get_cards_by_index(indices[:n], keep_in_deck=keep_in_deck)

    def get_cards_by_index(self, indices, keep_in_deck=True):
        cards = []
        indices.sort(reverse=True)
        for i in indices:
            cards.append(self.cards[i])
            if not keep_in_deck:
                del self.cards[i]
        return cards

    def true_sample(self, replace=True):
        moves = self.moves()
        move = moves[random.sample(moves.keys(), 1)[0]]  # pick a move card
        max_playable_cards = move[0]
        k_cards = random.randint(2, max_playable_cards)  # play k cards
        cards = self.get_cards_by_card(
            k_cards, move[1], keep_in_deck=replace)  # get from deck of player and remove it from player's deck
        return cards

    def random_sample(self, n=None):
        max_playable_cards = min(4, len(self.cards))

        if n is None:
            k_cards = random.randint(2, max_playable_cards)  # play k cards
        else:
            k_cards = n
        # indexes of cards
        dealt_indexes = [i[0] for i in random.sample(
            list(enumerate(self.cards)), k_cards)]
        called_indexes = [i[0] for i in random.sample(
            list(enumerate(self.cards)), k_cards)]

        called = self.get_cards_by_index(
            called_indexes, keep_in_deck=True)
        dealt = self.get_cards_by_index(
            dealt_indexes, keep_in_deck=False)

        return called, dealt

    def test_full_valid_deck(self):
        cards = Cards.init_deck()
        assert cards == self, "Valid deck of cards"
        return True

    def __eq__(self, other):
        if not isinstance(other, Cards):
            raise Exception(
                "Equality only defined for Cards to self, not ", type(other))
        l1 = sorted(self.cards, key=lambda x: x.value)
        l1 = sorted(l1, key=lambda x: x.face)
        l2 = sorted(self.cards, key=lambda x: x.value)
        l2 = sorted(l2, key=lambda x: x.face)
        for a, b in zip(l1, l2):
            if a != b:
                return False
        return True

    def to_json(self):
        return [c.to_json() for c in self.cards]


class Player():
    def __init__(self, name='default', cards=Cards(), bluf_prob=0.5):
        super().__init__()
        self.name = name
        if isinstance(cards, Cards):
            self.cards = cards
        else:
            self.cards = Cards(cards)
        self._bluf = bluf_prob

    def to_json(self):
        return self.cards.to_json()

    def __str__(self):
        return f'Name({self.name})=' + " ".join([c.__str__() for c in self.cards])

    def empty(self):
        return len(self.cards) == 0

    def has_one_card(self):
        return len(self.cards) == 1

    def bluffing(self):
        return random.random() < self._bluf
