# Bluf
:Card Game Bluff:

Game starts by distributing the cards equally to all candidates.
We write here for two players only for bravity.
(We hope it will be easy to extended to n-players later on).

** For a single deck, this game is not too hard to play. It would be more intereasting to play with n decks. **
## The Game
Arbitrary player starts the game by taking one of the three possible moves.
1. A user can **Bluf** or **Call** Pairs (Two Cards), Traids (Three Cards) or Quads (Four Cards).
2. A user can **Debunk Bluf** and check the last moves' cards.
3. A user can **Pass** the move i.e do not play anything.
The goal of each user is to **eliminate all cards from his hand**.

If both players passes on a single move, then the cards played are archived and no longer in play.

### Heuristics (Basic player)
Following are some simple heuristics a human player will follows.

1. Don't Bluf on cards that user don't have or opponent is certain about.
2. Debunk Bluf when you are **certain** (you have the cards or they are delt) that opponent is Bluffing.

### Heuristics (Expert player)
3. Take cards when more of your cards are exposed. 
4. Stretegically Bluf.

### Special Cases in rules

1. The first move of round can not Debunk Bluf.
2. If a user has single card left, he can not play bluf or call.

## Gym Environment
@TODO 

## MCTS
@TODO

## Details of DQN
@TODO

### State Space
1. We make an array of 52 items which describe the feature vector of the game. Each cell contains
 -1 = player 1 has the card
  0 = delt
  1 = player 2 has the card

2. We make another array of 52 items which describe the values called by the player at that moment.
  
