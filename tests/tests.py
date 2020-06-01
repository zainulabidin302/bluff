from lib.Game import Game, MOVE_TYPE
from lib.Player import Cards
from lib.constants import MAX_CARDS


def get_n_player_running_game(n):
    g = Game(n_players=n)
    for i in range(n):
        g.add_player("Hello" + str(i), i)
    g.start_game()
    return g


def test_game_start_end():
    g = Game(n_players=2)
    assert g._end == g._start == False, "Game should not be running."
    assert(len(g._players) == 0), "Player should be zero"
    g.add_player("Hello", 1001)
    assert(len(g._players) == 1), "Player should be one"
    try:
        g.add_player("Hello", 1001)
        assert False, "Should throw when duplicate player joins."
    except Exception as e:
        pass

    try:
        g.start_game()
        assert False, "Game should thrwo game can not start without players completed."
    except Exception as e:
        pass

    g.add_player("Hello", 1002)
    assert(len(g._players) == 2), "Player should be two"

    g.start_game()
    g._start == True, "Game should be running."

    try:
        g.start_game()
        assert False, "Should throw when running a game running or ended."
    except Exception as e:
        pass

    try:
        g.add_player("HI", 111)
        assert False, "Should throw when adding to running or ended game."
    except Exception as e:
        pass

    g.end_game()
    g._start == True, "Game should be ened."


def test_2_player_game_play():
    g = get_n_player_running_game(2)
    player, _ = g.move_by()

    claim = Cards.from_tuple([(1, 2), (1, 2), (1, 2)])
    cards = Cards.from_cards(
        [player.cards[0], player.cards[1], player.cards[2]])
    g.move(MOVE_TYPE.PLAY, cards, claim, player)

    assert len(g._dealt) == 3, "Three dealt cards should be availabe."
    assert len(g._called) == 3, "Three called cards should be availabe."

    claim = Cards.from_tuple([(1, 2), (1, 2), (1, 2)])
    cards = Cards.from_cards(
        [player.cards[0], player.cards[1], player.cards[2]])
    try:
        g.move(MOVE_TYPE.BLUFF, cards, claim, player)
        assert False, "Wrong player is moving, should throw exception"
    except:
        pass

    assert len(g._dealt) == 3, "Three dealt cards should still be availabe."
    assert len(g._called) == 3, "Three called cards should still be availabe."

    player, _ = g.move_by()
    g.move(MOVE_TYPE.BLUFF, None, None, player)

    g._dealt.empty() == True, "After calling bluff, dealt should be clean."
    g._called.empty() == True, "After calling bluff, called should be clean."


def test_4_player_game_play():
    g = get_n_player_running_game(4)
    player, _ = g.move_by()

    claim = Cards.from_tuple([(1, 2), (1, 2), (1, 2)])
    cards = Cards.from_cards(
        [player.cards[0], player.cards[1], player.cards[2]])
    g.move(MOVE_TYPE.PLAY, cards, claim, player)

    assert len(g._dealt) == 3, "Three dealt cards should be availabe."
    assert len(g._called) == 3, "Three called cards should be availabe."

    claim = Cards.from_tuple([(1, 2), (1, 2), (1, 2)])
    cards = Cards.from_cards(
        [player.cards[0], player.cards[1], player.cards[2]])
    try:
        g.move(MOVE_TYPE.BLUFF, cards, claim, player)
        assert False, "Wrong player is moving, should throw exception"
    except:
        pass

    assert len(g._dealt) == 3, "Three dealt cards should still be availabe."
    assert len(g._called) == 3, "Three called cards should still be availabe."

    player, _ = g.move_by()
    g.move(MOVE_TYPE.BLUFF, None, None, player)

    g._dealt.empty() == True, "After calling bluff, dealt should be clean."
    g._called.empty() == True, "After calling bluff, called should be clean."
    test_game_is_valid_and_running(g)


def test_3_player_game_play():
    g = get_n_player_running_game(3)
    player, _ = g.move_by()
    test_game_is_valid_and_running(g)

    claim = Cards.from_tuple([(1, 2), (1, 2), (1, 2)])
    cards = Cards.from_cards(
        [player.cards[0], player.cards[1], player.cards[2]])
    g.move(MOVE_TYPE.PLAY, cards, claim, player)
    test_game_is_valid_and_running(g)

    assert len(g._dealt) == 3, "Three dealt cards should be availabe."
    assert len(g._called) == 3, "Three called cards should be availabe."

    claim = Cards.from_tuple([(1, 2), (1, 2), (1, 2)])
    cards = Cards.from_cards(
        [player.cards[0], player.cards[1], player.cards[2]])
    try:
        g.move(MOVE_TYPE.BLUFF, cards, claim, player)
        assert False, "Wrong player is moving, should throw exception"
    except:
        pass

    assert len(g._dealt) == 3, "Three dealt cards should still be availabe."
    assert len(g._called) == 3, "Three called cards should still be availabe."
    test_game_is_valid_and_running(g)

    player, _ = g.move_by()
    g.move(MOVE_TYPE.BLUFF, None, None, player)

    g._dealt.empty() == True, "After calling bluff, dealt should be clean."
    g._called.empty() == True, "After calling bluff, called should be clean."
    test_game_is_valid_and_running(g)


def test_4_player_game_play():
    g = get_n_player_running_game(4)
    test_game_is_valid_and_running(g)
    player, _ = g.move_by()

    claim = Cards.from_tuple([(1, 2), (1, 2), (1, 2)])
    cards = Cards.from_cards(
        [player.cards[0], player.cards[1], player.cards[2]])
    g.move(MOVE_TYPE.PLAY, cards, claim, player)
    test_game_is_valid_and_running(g)
    assert len(g._dealt) == 3, "Three dealt cards should be availabe."
    assert len(g._called) == 3, "Three called cards should be availabe."

    claim = Cards.from_tuple([(1, 2), (1, 2), (1, 2)])
    cards = Cards.from_cards(
        [player.cards[0], player.cards[1], player.cards[2]])
    try:
        g.move(MOVE_TYPE.BLUFF, cards, claim, player)
        assert False, "Wrong player is moving, should throw exception"
    except:
        pass

    assert len(g._dealt) == 3, "Three dealt cards should still be availabe."
    assert len(g._called) == 3, "Three called cards should still be availabe."

    player, _ = g.move_by()
    g.move(MOVE_TYPE.BLUFF, None, None, player)

    g._dealt.empty() == True, "After calling bluff, dealt should be clean."
    g._called.empty() == True, "After calling bluff, called should be clean."
    test_game_is_valid_and_running(g)


def test_game_is_valid_and_running(g):
    assert g._start == True, "Game should be start"
    assert g._n_players == len(
        g._players), "All player must have joined before starting."
    cards = Cards(cards=[])
    for p in g._players:
        cards.extend(p.cards)

    cards.extend(g._dealt)
    cards.extend(g._archived)

    assert len(
        cards) == MAX_CARDS, f"{len(cards)} should be equal MAX_CARDS={MAX_CARDS}"
    return cards.test_full_valid_deck()


def test_to_dict_from_dict():
    g = get_n_player_running_game(4)
    test_game_is_valid_and_running(g)
    player, _ = g.move_by()

    claim = Cards.from_tuple([(1, 2), (1, 2), (1, 2)])
    cards = Cards.from_cards(
        [player.cards[0], player.cards[1], player.cards[2]])
    g.move(MOVE_TYPE.PLAY, cards, claim, player)
    test_game_is_valid_and_running(g)
    assert len(g._dealt) == 3, "Three dealt cards should be availabe."
    assert len(g._called) == 3, "Three called cards should be availabe."

    claim = Cards.from_tuple([(1, 2), (1, 2), (1, 2)])
    cards = Cards.from_cards(
        [player.cards[0], player.cards[1], player.cards[2]])
    try:
        g.move(MOVE_TYPE.BLUFF, cards, claim, player)
        assert False, "Wrong player is moving, should throw exception"
    except:
        pass

    assert len(g._dealt) == 3, "Three dealt cards should still be availabe."
    assert len(g._called) == 3, "Three called cards should still be availabe."

    player, _ = g.move_by()
    g.move(MOVE_TYPE.BLUFF, None, None, player)

    g._dealt.empty() == True, "After calling bluff, dealt should be clean."
    g._called.empty() == True, "After calling bluff, called should be clean."
    test_game_is_valid_and_running(g)

    d = g.to_dict()
    n_game = Game.from_dict(d)
    assert n_game._dealt == Cards.from_dict(d["_dealt"])
    assert n_game._n_players == d["_n_players"]

    # assert deepequal
