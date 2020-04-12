from flask import Flask
import json
import os
app = Flask(__name__)

path = './../gameplay/'


@app.route('/game/<game_id>')
def game_data(game_id):
    print(f'filename {os.path.join(path, game_id)}')
    with open(os.path.join(path, game_id), 'r') as f:
        output = json.dumps(json.load(f))
    print(f'game_id : {game_id}')
    return output


@app.route('/game_list')
def game_list():
    return {"games": os.listdir(os.path.join(path))}
