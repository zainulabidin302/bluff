import random
import numpy as np
from lib.constants import ACTIONS, FACES, ACTIONS, VALUES, ROOT_LOGGER
from lib.Player import Player, Cards
from lib.Card import Card
from copy import deepcopy
import logging
import json
import time

logger = logging.getLogger(ROOT_LOGGER)


class BaseGame():
    def __init__(self):
        super().__init__()
        self.MAX_CARDS = 52
        self.FACES = len(FACES)
        self.VALUES = len(VALUES)


class Game(BaseGame):
    def __init__(self, n_players=2):
        super().__init__()
        self._n_players = n_players
        self._archived = Cards()

        self._dealt = Cards()  # actual cards on the table.
        self._called = Cards()  # calls from the user.

        self._last_n_called = Cards()
        self._last_n_dealt = Cards()

        self._move_by_histroy = []
        self._action_history = []

        # action prob: bluff, pass, play
        self._model = np.random.dirichlet((np.arange(1, 4)))
        # when play, each player bluff with different prob
        self._bluf_model = np.random.dirichlet(
            np.random.uniform(10, size=self._n_players+1))
        self._players = []

    def __str__(self):
        s = f'Dealt=' + " ".join([c.__str__() for c in self._dealt])
        s += f'Called=' + " ".join([c.__str__() for c in self._called])
        return "\n".join([p.__str__() for p in self._players]) + "\n" + s

    def add_player(self, name, id, bluf_prob):
        assert (isinstance(cards, Cards),
                "cards should be cards not" + str(type(cards)))
        if len(self._players) < self._n_players:
            self._players.append(Player(
                name=name,
                id=id,
                cards=cards,
                bluf_prob=bluf_prob))
        else:
            raise Exception(
                f"{len(self._players)} players  should be less then total = {self._n_players}")

    def join_game(self, player):
        self.add_player(player.name, player.id, 0.5)

    def start_game(self):
        cards = Cards.init_deck()
        for id, card_set in enumerate(cards.split(n=self._n_players)):
            self._players[id].set_cards(card_set)

    def game_over(self):
        return all([not p.empty() for p in self._players])

    def first_move_of_round(self):
        return len(self._dealt) == 0

    def _pass_move(self, p, o):
        return

    def _call_bluf_move(self, player, ):
        bluf = any([self._dealt[i] == self._called[i]
                    for i in range(len(self._dealt) - len(self._last_n_dealt), len(self._dealt))])
        if bluf:
            player.cards.extend(self._dealt)
        else:
            opponent.cards.extend(self._dealt)

        self._dealt.make_empty()
        self._called.make_empty()
        self._last_n_called.make_empty()
        self._last_n_dealt.make_empty()
        return bluf

    def _pick_random_move(self, player):
        called, dealt = player.cards.random_sample()
        self._set_state_after_play_move(dealt, called)

    def _pick_true_move(self, player):
        cards = player.cards.true_sample(replace=False)
        self._set_state_after_play_move(cards, cards)

    def _set_state_after_play_move(self, dealt, called):
        self._dealt.extend(dealt)
        self._called.extend(called)
        self._last_n_dealt = dealt
        self._last_n_called = called

    def _play_move(self, player):
        assert len(
            player.cards) > 1, 'player can only play with more then 1 cards.'

        moves = player.cards.moves()

        if len(moves.keys()) > 0:
            if player.bluffing():
                cards = self._pick_random_move(player)  # may or may not bluf
                self._last_action = '_pick_random_move'
            else:
                cards = self._pick_true_move(player)
                self._last_action = '_pick_true_move'
        else:
            cards = self._pick_random_move(player)  # can only bluf
            self._last_action = '_pick_random_move'

    def action(self, model):
        model = np.array(model)
        model /= model.sum()
        action = np.random.choice(3, 1, p=model)[0]
        if action == 0:
            self._a
            return self._call_bluf_move
        elif action == 1:
            self._last_action = '_pass_move'
            return self._pass_move
        elif action == 2:
            self._last_action = '_play_move'
            return self._play_move

    def _auto_select_move(self, player):
        model = deepcopy(self._model)
        # bluf, play, pass
        if self.first_move_of_round():
            model[0] = 0  # you can not debunk bluf
        if player.has_one_card():
            model[2] = 0  # you can not play with single card
        action = self.action(model)
        return action(player)

    def test_game_is_valid(self):
        cards = Cards(cards=[])
        for p in self._players:
            cards.extend(p.cards)
        cards.extend(self._dealt)
        cards.extend(self._archived)
        assert len(cards) == self.MAX_CARDS
        return cards.test_full_valid_deck()

    def run_episode(self):
        player_id = 0
        while not self.game_over():
            assert self.test_game_is_valid(), 'Test the game state is in valid position'
            for p in self._players:
                self._move_by_histroy.push(p)
                self._auto_select_move(p)
                assert self.test_game_is_valid(), 'Test the game state is in valid position'
                if self.game_over():
                    break
        losser = list(filter(lambda x: not x.empty(), self._players))[0]
        logger.info(f'episde ends: {losser.name} lost')

        with open(f'gameplay/{time.time()}', 'w+') as f:
            json.dump(history, f)
