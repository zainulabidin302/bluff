from lib.Game import Game
from tests.tests import test_to_dict_from_dict, test_game_start_end, test_2_player_game_play, test_4_player_game_play, test_3_player_game_play
import sys
import logging
import time


def main():
    test_game_start_end()
    test_2_player_game_play()
    test_4_player_game_play()
    test_3_player_game_play()
    test_to_dict_from_dict()
    # test_2_player_game_play_bluff_first_round()


if __name__ == "__main__":
    main()
