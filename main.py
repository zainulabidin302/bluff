from lib.Game import Game
import sys
import logging
import time
from lib.constants import ROOT_LOGGER
logger = logging.getLogger(ROOT_LOGGER)
logger.setLevel(logging.ERROR)

# fh = logging.FileHandler(f'./gameplay/{time.time()}.txt')
# logger.addHandler(fh)


def main():
    n = 2
    logger.info("Game Started: N=2")
    g = Game(n_players=2)
    g.run_episode()


if __name__ == "__main__":
    main()
