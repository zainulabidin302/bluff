# Bluf
:Card Game Bluff:

Game starts by distributing the cards equally to all candidates.
We write here for two players only for bravity.
(We hope it will be easy to extended to n-players later on).

# The Game and Rules
* Arbitrary player starts the game by taking one of the three possible moves.

1. A user can play (Bluf or Call) Pairs (Two Cards), Traids (Three Cards) or Quads (Four Cards).
2. A user can "Debunk Bluf" and check the last users cards.
3. A user can pass the move i.e do not play anything.


* The goal of each user is to eliminate all cards from his hand.

The outcome of each action depends on situation of the game. Also, in some situation one or more moves are prohibbited.

Following are some simple heuristics a human player will follows.

1. Don't Play Bluff on cards that user don't have.
2. Don't Play Bluff on already exposed cards.
3. Take more cards when more cards are exposed.


## Game State

1. We make an array of 52 items which describe the feature vector of the game. Each cell contains
 -1 = player 1 has the card
  0 = delt
  1 = player 2 has the card

2. We make another array of 52 items which describe the values called by the player at that moment.
  
