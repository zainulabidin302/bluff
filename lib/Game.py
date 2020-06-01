import random
import numpy as np
from lib.constants import ACTIONS, FACES, ACTIONS, VALUES, ROOT_LOGGER
from lib.Player import Player, Cards
from lib.Card import Card
from copy import deepcopy
import json
import time


class MOVE_TYPE:
    PASS = 0
    PLAY = 1
    BLUFF = 2

    def validate(t):
        assert (t in [0, 1, 2]), "Move must be valid. [0, 1, 2]"


class Game():
    def __init__(self, n_players=2):
        super().__init__()
        self._id = None
        self._n_players = int(n_players)

        self._archived = Cards.from_empty()
        self._dealt = Cards.from_empty()
        self._called = Cards.from_empty()
        self._last_n_called = Cards.from_empty()
        self._last_n_dealt = Cards.from_empty()
        self._move_by = []
        self._action_history = []
        self._players = []
        self._join_code = str(int(time.time()))[-5:]

        self._start = False
        self._end = False
        self._time = time.time()

    def to_dict(self):
        return {"_id": str(self._id),
                "_n_players": int(self._n_players),
                "_archived": self._archived.to_dict(),
                "_dealt": self._dealt.to_dict(),
                "_called": self._called.to_dict(),
                "_last_n_called": self._last_n_called.to_dict(),
                "_last_n_dealt": self._last_n_dealt.to_dict(),
                "_move_by": self._move_by,
                "_action_history": self._action_history,
                "_players": [p.to_dict() for p in self._players],
                "_start": self._start,
                "_end": self._end,
                "_time": self._time,
                "_join_code": self._join_code
                }

    def from_dict(d):
        g = Game(n_players=int(d["_n_players"]))
        g._id = str(d["_id"])
        g._archived = Cards.from_dict(d["_archived"])
        g._dealt = Cards.from_dict(d["_dealt"])
        g._called = Cards.from_dict(d["_called"])
        g._last_n_called = Cards.from_dict(d["_last_n_called"])
        g._last_n_dealt = Cards.from_dict(d["_last_n_dealt"])
        g._move_by = d["_move_by"]
        g._action_history = d["_action_history"]
        g._players = [Player.from_dict(p) for p in d["_players"]]
        g._start = d["_start"]
        g._end = d["_end"]
        g._time = d["_time"]
        g._join_code = d["_join_code"]
        return g

    def get_player_by_id(self, id):
        for p in self._players:
            if p._id == id:
                return p
        return None

    def remove_player(self, player):
        if self._start or self._end:
            raise Exception("Game already started or ended")

        assert isinstance(player, Player), "Player is player"

        if len(list(filter(lambda p: str(p._id) == str(player._id), self._players))) == 0:
            raise Exception(
                "Player not in game.")
        self._players = filter(
            lambda p: str(p._id) != str(player._id), self._players)

    def add_player(self, player):
        if self._start or self._end:
            raise Exception("Game already started or ended")

        assert isinstance(player, Player), "Player is player"
        if len(self._players) < self._n_players:
            if len(list(filter(lambda p: p._id == id, self._players))) > 0:
                raise Exception(
                    "Player duplicate (with same id) found. Not allowed.")
            self._players.append(player)
        else:
            raise Exception(
                f"{len(self._players)} players  should be less then total = {self._n_players}")

    def start_game(self):
        if self._start or self._end:
            raise Exception("Game already started or ended")
        if len(self._players) == int(self._n_players):
            cards = Cards.init_deck()
            for id, card_set in enumerate(cards.split(n=self._n_players)):
                self._players[id].set_cards(card_set)
            self._start = True
            self._move_by = [0]
        else:
            raise Exception(
                f"Can not start game. All player must have joined.")

    def end_game(self):
        assert self._start == True, "Game must be started to be ended."
        self._end = True

    def game_over(self):
        return not all([not p.cards.empty() for p in self._players])

    def first_move_of_round(self):
        return len(self._dealt) == 0

    def move_by(self):
        return self._players[self._move_by[-1]], self._move_by[-1]

    def move_by_validate(self, player):
        actual_player, _ = self.move_by()
        assert(player._id == actual_player._id and actual_player.name ==
               player.name), f"{actual_player._id} should play, not {player._id}"

    def claim_validate(self, claim):
        if claim is None:
            return
        for c in claim:
            if not (claim[0] == c):
                raise Exception("all cliams should be same.")

    def move(self, type, cards, claim, player):
        MOVE_TYPE.validate(type)
        self.move_by_validate(player)
        self.claim_validate(claim)

        if type == MOVE_TYPE.BLUFF:
            assert cards == None, "cards should be none when bluffing."
            assert claim == None, "cliam should be none when bluffing."
            if self._dealt.empty():
                raise Exception("To call bluff, dealt must have cards.")
            print('50'*50, self._last_n_dealt.to_dict(),
                  self._last_n_called.to_dict())

            if self._last_n_dealt == self._last_n_called:
                print('CARDS GO THE CALLER OF BLUFFFF')
                player, playerIndex = self.move_by()
                self._dealt.move_cards_to(self._dealt, player.cards)
                self.move_to_next_player(idx=playerIndex)
            else:
                print('CARDS GO THE DEALER OF BLUFFFF')
                if self.last_pass_index() == -1:
                    # there was no pass between last and current move.
                    playerIndex = self._move_by[-2]
                else:
                    playerIndex = self._move_by[self.last_pass_index()-1]

                self._dealt.move_cards_to(
                    self._dealt, self._players[playerIndex].cards)
                self.move_to_next_player(idx=playerIndex)

            self._called.make_empty()
            if self.game_over():
                self.end_game()

        if type == MOVE_TYPE.PLAY:
            assert isinstance(
                cards, Cards), f"cards must Cards, {type(cards)} given "
            assert isinstance(claim, Cards), "claim must Cards  "
            assert isinstance(
                player, Player), "player must Plyaer not " + type(player)
            if self.first_move_of_round():
                assert(len(cards) >= 2 and len(cards) <=
                       4), "2, 3 or 4 cards should be dealt"
            else:
                assert(len(cards) >= 1 and len(cards) <=
                       4), "2, 3 or 4 cards should be dealt"

            assert(len(cards) == len(claim)
                   ), "claim should be equal to deal"

            self._last_n_dealt = deepcopy(cards)
            self._last_n_called = deepcopy(claim)
            player.cards.move_cards_to(cards, self._dealt)
            self._called.extend(claim)
            self._action_history.append(MOVE_TYPE.PLAY)
            self.move_to_next_player()

        if type == MOVE_TYPE.PASS:
            assert cards == None, "cards should be none when passing."
            assert claim == None, "cliam should be none when passing."

            self._action_history.append(MOVE_TYPE.PASS)

            if self.n_passes() >= self._n_players:
                self._dealt.move_cards_to(self._dealt, self._archived)
                self._called.make_empty()
                # check after last pass
                if self.game_over():
                    self.end_game()
            self.move_to_next_player()
        print('40'*400, self.game_over())

    def move_to_next_player(self, idx=None):
        if idx == None:
            self._move_by.append((self._move_by[-1] + 1) % self._n_players)
        else:
            assert idx >= 0 and idx < self._n_players
            self._move_by.append(idx)

    def n_passes(self):
        if self.last_pass_index() == -1:
            return 0
        else:
            return len(self._action_history[self.last_pass_index():])

    def last_pass_index(self):
        if self._action_history[-1] != MOVE_TYPE.PASS:
            return -1

        last_pass_index = len(self._action_history) - 1
        action = self._action_history[last_pass_index]

        while (last_pass_index >= 0 and action == MOVE_TYPE.PASS):
            last_pass_index -= 1
            action = self._action_history[last_pass_index]
        return last_pass_index + 1
