# pylint: disable=E1101
# Needed because pylint is incompatible with SQL Alchemy for some reason...

import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# pep8 moves this line to the top, but we need db to be declared first
from models import Game, Team  # nopep8


@app.route("/")
def hello():
    return "I'm alive!"


@app.route("/projections/")
def projections():
    home = request.args.get('home')
    away = request.args.get('away')
    try:
        if home is None and away is None:
            # Todo: Return actual data from database
            # Right now it is empty, so we're returning dummy data

            # games = Game.query.filter_by(
            #     date=datetime.today())
            # return jsonify([g.serialize() for g in games])

            print(datetime.today())

            return jsonify([
                {
                    'id': 1,
                    'date': datetime.today(),
                    'home_id': 1,
                    'away_id': 2,
                    'home_name': 'Gonzaga',
                    'away_name': 'Duke',
                    'home_score': 89,
                    'away_score': 67,
                    'home_projection': 92,
                    'away_projection': 85
                },
                {
                    'id': 2,
                    'date': datetime.today(),
                    'home_id': 3,
                    'away_id': 4,
                    'home_name': 'Kansas',
                    'away_name': 'Oregon',
                    'home_score': 83,
                    'away_score': 62,
                    'home_projection': 91,
                    'away_projection': 62
                },
                {
                    'id': 2,
                    'date': datetime.today(),
                    'home_id': 5,
                    'away_id': 6,
                    'home_name': 'Ohio State',
                    'away_name': 'Baylor',
                    'home_score': 67,
                    'away_score': 49,
                    'home_projection': 59,
                    'away_projection': 51
                }
            ])

        elif home is None or away is None:
            return ("'home' and 'away' are necessary query parameters when not using the 'all' query parameter")
        else:
            # Todo: Compare two random teams without inserting the game into the database
            return jsonify({
                'home_id': 5,
                'away_id': 6,
                'home_name': 'Ohio State',
                'away_name': 'Baylor',
                'home_projection': 69,
                'away_projection': 55
            })
    except Exception as e:
        return(str(e))


@app.route("/teams/")
def teams():
    try:
        teams = Team.query.all()
        # Todo: Return actual data from database
        # Right now it is empty, so we're returning dummy data
        # return jsonify([t.serialize() for t in teams])
        return jsonify([{"id": 1, "name": "Gonazaga"}, {"id": 2, "name": "Duke"}, {"id": 3, "name": "Kansas"}, {"id": 4, "name": "Oregon"}, {"id": 5, "name": "Ohio State"}, {"id": 6, "name": "Baylor"}])
    except Exception as e:
        return(str(e))


if __name__ == '__main__':
    app.run()
