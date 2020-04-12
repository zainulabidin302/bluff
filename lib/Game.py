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

        self.n_players = 2

        self._archived = Cards()  # cards no longer in play.
        self._dealt = Cards()  # actual cards on the table.
        self._called = Cards()  # calls from the user.
        self._n_last_cards = 0  # number of cards played by last player.
        self._last_player = ""
        self._players = []

        # action prob: bluff, pass, play
        self.model = np.random.dirichlet((np.arange(1, 4)))

        # when play, each player bluff with different prob
        self.bluf_model = np.random.dirichlet(
            np.random.uniform(10, size=self.n_players+1))

        # deal cards
        self._init_game()

    def __str__(self):
        s = f'Dealt=' + " ".join([c.__str__() for c in self._dealt])
        s += f'Called=' + " ".join([c.__str__() for c in self._called])

        return "\n".join([p.__str__() for p in self._players]) + "\n" + s

    def to_json(self):
        players = [{"cards": p.to_json()} for p in self._players]
        state = {
            "dealt": self._dealt.to_json(),
            "called": self._called.to_json(),
            "last_n_called": self._n_last_cards,
            "players": players
        }
        return state

    def _init_game(self):
        """
          Initialize the cards and deal it to the players.
        """
        cards = Cards.init_deck()
        for id, card_set in enumerate(cards.split(n=self.n_players)):
            name = "Player_" + str(id)
            self._players.append(Player(
                name=name,
                cards=card_set,
                bluf_prob=self.bluf_model[id]))

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
        bluf = any([self._dealt[i] == self._called[i]
                    for i in range(len(self._dealt) - self._n_last_cards, len(self._dealt))])

        if bluf:
            player.cards.extend(self._dealt)
        else:
            opponent.cards.extend(self._dealt)

        self._dealt.make_empty()
        self._called.make_empty()
        return bluf

    def _pick_random_move(self, player):
        called, dealt = player.cards.random_sample()
        self._dealt.extend(dealt)
        self._called.extend(called)
        self._n_last_cards = len(called)

    def _pick_true_move(self, player):
        cards = player.cards.true_sample(replace=False)
        self._dealt.extend(cards)
        self._called.extend(cards)
        self._n_last_cards = len(cards)

    def _play_move(self, player, opponent):
        assert len(
            player.cards) > 1, 'player can only play with more then 1 cards.'

        moves = player.cards.moves()

        if len(moves.keys()) > 0:
            if player.bluffing():
                cards = self._pick_random_move(player)  # may or may not bluf
                self._current_action = '_pick_random_move'
            else:
                cards = self._pick_true_move(player)
                self._current_action = '_pick_true_move'
        else:
            cards = self._pick_random_move(player)  # can only bluf
            self._current_action = '_pick_random_move'

    def action(self, model):
        model = np.array(model)
        model /= model.sum()
        action = np.random.choice(3, 1, p=model)[0]
        logger.info(f'{ACTIONS[action]}')

        if action == 0:
            self._current_action = '_call_bluf_move'
            return self._call_bluf_move
        elif action == 1:
            return self._pass_move
            self._current_action = '_pass_move'
        elif action == 2:
            return self._play_move

    def select_move(self, player, opponent):
        model = deepcopy(self.model)
        # bluf, play, pass
        if self.first_move_of_round():
            model[0] = 0  # you can not debunk bluf
        if player.has_one_card():
            model[2] = 0  # you can not play with single card

        action = self.action(model)
        return action(player, opponent)

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
        history = {
            "game_history": []
        }

        while not self.game_over():
            assert self.test_game_is_valid(), 'Test the game state is in valid position'
            player = self._players[player_id]
            opponent = self._players[(player_id - 1) % self.n_players]
            logger.info(f'{player.name}: ')
            logger.info(self)
            self.select_move(player, opponent)
            self._last_player = player.name
            history["game_history"].append(self.to_json())
            player_id = (player_id + 1) % self.n_players

        assert self.test_game_is_valid(), 'Test the game state is in valid position'
        losser = list(filter(lambda x: not x.empty(), self._players))[0]
        logger.info(f'episde ends: {losser.name} lost')

        with open(f'gameplay/{time.time()}', 'w+') as f:
            json.dump(history, f)
