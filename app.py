import sys

from bson.objectid import ObjectId
from flask import Flask, request
import json
import os
from lib.Game import Game, MOVE_TYPE
from lib.Card import Card
from lib.Player import Cards, Player
import time

import pymongo
app = Flask(__name__)


client = pymongo.MongoClient(
    "mongodb+srv://py_server_bluff:ncR2eH5jfjiXqfjV@cluster0-ilbat.mongodb.net/test?retryWrites=true&w=majority")
db = client.bluffdb


def get_player_by_id(id):
    return db.player.find_one({"_id": id})


# def update_game(id, game):
#     db.game.update(
#         {"_id": id}, {'$push': {'history': game}, '$set': {'current': game}})


@app.route('/game/<game_id>')
def route_get_by_id(game_id):
    return Game.from_dict(db.game.find_one({"_id": ObjectId(game_id)})).to_dict()


@app.route('/game/code/<game_id>')
def route_get_by_code(game_id):
    return Game.from_dict(db.game.find_one({"_join_code": int(game_id)})).to_dict()


@app.route('/game/start/<game_id>')
def route_start_game(game_id):
    g = db.game.find_one({"_id": ObjectId(game_id)})
    if g is None:
        return {"message": "Game not found"}, 404

    g = Game.from_dict(g)

    try:

        g.start_game()
        a = g.to_dict()
        del a["_id"]
        db.game.update({"_id": ObjectId(g._id)}, a)
        a['_id'] = g._id
        return a

        return Game.from_dict(g).to_dict()
    except Exception as e:
        print(e)
        return {"message": "Something went wrong"}, 500


@app.route('/game/end/<game_id>')
def route_end_game(game_id):
    try:
        g = Game.from_dict(db.game.find_one(
            {"_id": ObjectId(game_id)}
        ))
        g.end_game()
        a = g.to_dict()
        del a["_id"]
        db.game.update({"_id": ObjectId(g._id)}, a)
        a['_id'] = g._id
        return a
    except Exception as e:
        print(e)
        return {"message": "Something went wrong"}, 500


@app.route('/game/current/<player_id>')
def route_current_game(player_id):
    player = db.player.find_one({"_id": ObjectId(player_id)})
    if player is None:
        return {"message": "User not found"}, 404
    query = {"$or": [{"_start": True, }, {"_start": False}],
             "_end": False, "_players": {"$elemMatch": {"_id": player_id}}}
    g = db.game.find_one(query)

    if g is None:
        return {"message": "Game not found"}, 404

    print(g)
    return Game.from_dict(g).to_dict()


@app.route('/game/create/<n_players>/<player_id>')
def route_create_game(n_players, player_id):
    player = db.player.find_one({"_id": ObjectId(player_id)})
    if player is None:
        return {"message": "User not found"}, 404
    g = Game(n_players=n_players)
    p = Player.from_dict(player)
    g.add_player(p)
    a = g.to_dict()
    del a['_id']
    g._id = str(db.game.insert_one(a).inserted_id)
    print(g.to_dict())
    return g.to_dict()


@app.route('/game/join/<game_code>/<player_id>')
def route_create_join(game_code, player_id):
    player = db.player.find_one({"_id": ObjectId(player_id)})
    if player is None:
        return {"message": "User not found"}, 404
    g = db.game.find_one({"_join_code": game_code})
    if g is None:
        return {"message": "Game not found"}, 404

    try:
        p = Player.from_dict(player)
        g = Game.from_dict(g)
        g.add_player(p)
        print(g.to_dict())
        a = g.to_dict()
        del a["_id"]
        db.game.update({"_id": ObjectId(g._id)}, a)
        a['_id'] = g._id
        return a
    except Exception as e:
        print(e)
        return {"message": "Something went wrong"}, 500


@app.route('/game/leave/<game_id>/<player_id>')
def route_leave_join(game_id, player_id):

    player = db.player.find_one({"_id": ObjectId(player_id)})
    if player is None:
        return {"message": "User not found"}, 404

    g = db.game.find_one({"_id": ObjectId(game_id)})
    if g is None:
        return {"message": "Game not found"}, 404

    try:
        p = Player.from_dict(player)
        g = Game.from_dict(g)
        g.remove_player(p)
        print(g.to_dict())
        a = g.to_dict()
        del a["_id"]
        db.game.update({"_id": ObjectId(g._id)}, a)
        a['_id'] = g._id
        return a
    except Exception as e:
        print(e)
        return {"message": "Something went wrong"}, 500


@app.route('/player/create', methods=["POST"])
def route_create_player():
    data = request.get_json()
    print(data)
    p = Player(name=data["name"])
    a = p.to_dict()
    del a["_id"]
    id = db.player.insert_one(a).inserted_id
    p._id = str(id)
    return p.to_dict()


@app.route('/player/<player_id>', methods=["GET"])
def route_get_player(player_id):
    user = db.player.find_one({"_id": ObjectId(player_id)})
    if user is None:
        return {"message": "Player not found"}, 404
    return user


@app.route('/game/move/call/<game_id>/<user_id>', methods=['POST'])
def route_play_move(game_id, user_id):
    data = request.get_json()

    g = db.game.find_one({"_id": ObjectId(game_id)})
    if g is None:
        return {"message": "Game not found."}, 404

    g = Game.from_dict(g)
    player = g.get_player_by_id(user_id)
    if player is None:
        return {"message": "Plyaer not found."}, 404
    try:
        cards = Cards.from_dict(data["dealt"])
        cliam = Cards.from_dict(data["called"])
        g.move(MOVE_TYPE.PLAY, cards, cliam, player)
        a = g.to_dict()
        del a["_id"]
        db.game.update({"_id": ObjectId(g._id)}, a)
        a['_id'] = g._id
        return a
    except Exception as e:
        print(e)
        return {"message": "Something went wrong."}, 505


@app.route('/game/move/bluff/<game_id>/<user_id>')
def route_bluff_move(game_id, user_id):
    data = request.get_json()

    g = db.game.find_one({"_id": ObjectId(game_id)})
    if g is None:
        return {"message": "Game not found."}, 404

    g = Game.from_dict(g)
    player = g.get_player_by_id(user_id)
    if player is None:
        return {"message": "Player not found."}, 404

    try:
        g.move(MOVE_TYPE.BLUFF, None, None, player)
        a = g.to_dict()
        del a["_id"]
        db.game.update({"_id": ObjectId(g._id)}, a)
        a['_id'] = g._id
        return a
    except Exception as e:
        print(e)
        return {"message": "Something went wrong."}, 505

@app.route('/')
def index():

    return '<h1>ServerIsRunning</h1>'

@app.route('/game/move/pass/<game_id>/<user_id>')
def route_pass_move(game_id, user_id):
    data = request.get_json()

    g = db.game.find_one({"_id": ObjectId(game_id)})
    if g is None:
        return {"message": "Game not found."}, 404

    g = Game.from_dict(g)
    player = g.get_player_by_id(user_id)
    if player is None:
        return {"message": "Player not found."}, 404
    try:
        g.move(MOVE_TYPE.PASS, None, None, player)
        a = g.to_dict()
        del a["_id"]
        db.game.update({"_id": ObjectId(g._id)}, a)
        a['_id'] = g._id
        return a
    except Exception as e:
        print(e)
        return {"message": "Something went wrong."}, 505


if __name__ == "__main__":
    app.run(host='0.0.0.0')