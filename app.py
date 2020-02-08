# pylint: disable=E1101
# Needed because pylint is incompatible with SQL Alchemy for some reason...

import os
import requests
import json
from datetime import datetime as dt
from datetime import timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from sportsreference.ncaab.teams import Teams
from sportsreference.ncaab.boxscore import Boxscores
from sportsreference.ncaab.rankings import Rankings

app = Flask(__name__)
CORS(app)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# pep8 moves this line to the top, but we need db to be declared first
from models import Game, Team  # nopep8


@app.cli.command("test")
def test():
    # teams = list(Teams(2019))
    # teams.sort(key=lambda x: x.name)
    # for team in teams:
    #     print(f'{team.name} = {team.simple_rating_system}')
    today = dt.today()
    start = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(1)
    print(start, end)

# Create "flask seed" command which seeds the database with all teams and games.
@app.cli.command("seed")
def seed_database():
    print("Adding seed data to the database.")
    teams = list(Teams(2019))
    teams.sort(key=lambda x: x.name)
    for team in teams:
        new_team = Team(id=team.abbreviation, name=team.name)
        db.session.add(new_team)
    try:
        db.session.commit()
    except:
        db.session.rollback()


@app.route("/")
def hello():
    return "I'm alive!"


@app.route("/projections/")
def projections():
    home = request.args.get('home')
    away = request.args.get('away')

    if home is None and away is None:
        today = dt.today()
        today_start = today.replace(
            hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(1)

        games = db.session.query(Game).filter(
            Game.date > today_start, Game.date < today_end).all()

        all_games = db.session.query(Game).all()

        if len(all_games) > 9500:
            db.session.query(Game).delete()
            db.session.commit()

        # If today's games have not been retrieved yet then do so from sports
        # And get the projected score from the data science API
        if len(games) == 0:
            games_today = Boxscores(dt.today())
            games_today = games_today.games

            rankings = Rankings()
            rankings = rankings.current

            for date in games_today.keys():
                for game in games_today[date]:
                    home_team = db.session.query(Team).filter(
                        Team.name == game["home_name"]).first()
                    away_team = db.session.query(Team).filter(
                        Team.name == game["away_name"]).first()

                    if home_team is None:
                        home_team = Team(
                            id=game["home_abbr"], name=game["home_name"])
                        db.session.add(home_team)
                        try:
                            db.session.commit()
                            home_team = db.session.query(Team).filter(
                                Team.name == game["home_name"]).first()
                        except:
                            db.session.rollback()

                    elif away_team is None:
                        away_team = Team(
                            id=game["away_abbr"], name=game["away_name"])
                        db.session.add(away_team)

                        try:
                            db.session.commit()
                            away_team = db.session.query(Team).filter(
                                Team.name == game["away_name"]).first()
                        except:
                            db.session.rollback()
                    
                    print("000ooof")
                    data = {
                        "year": dt.today().year,
                        "month": dt.today().month,
                        "day": dt.today().day,
                        "home_name": home_team.name,
                        "home_rank": float(rankings.get(home_team.id.lower(), 0)),
                        "away_name": away_team.name,
                        "away_rank": float(rankings.get(away_team.id.lower(), 0))
                    }

                    res = requests.post(
                        "http://ncaab.herokuapp.com/", data=json.dumps(data))
                    res = res.json()

                    home_projection = res["home_score"]
                    away_projection = res["away_score"]

                    new_game = Game(
                        date=date, home=home_team.id, away=away_team.id, home_projection=home_projection, away_projection=away_projection)
                    db.session.add(new_game)
                    games.append(new_game)

            # TODO: Test this out...
            # Update yesterday's games with the scores
            # yesterday_start = today_start - timedelta(1)
            # games_yesterday = Boxscores(yesterday_start, today_start)
            # games_yesterday = games_yesterday.games

            # for date in games_yesterday.keys():
            #     for game in games_yesterday[date]:
            #         home_team = db.session.query(Team).filter(
            #             Team.name == game["home_name"]).first()
            #         away_team = db.session.query(Team).filter(
            #             Team.name == game["away_name"]).first()
            #         print(home_team, away_team)
            #         applicable_game = db.session.query(Game).filter(
            #             Game.date > yesterday_start, Game.date < today_start, Game.home == home_team.id, Game.away == away_team.id).first()
            #         print(applicable_game)
            #         applicable_game.home_score = game["home_score"]
            #         applicable_game.away_score = game["away_score"]

            try:
                db.session.commit()
            except:
                db.session.rollback()
        games_without_names = [g.serialize() for g in games]
        games_with_names = []
        for game in games_without_names:
            home_team = db.session.query(Team).filter(
                Team.id == game["home_id"]).first()
            away_team = db.session.query(Team).filter(
                Team.id == game["away_id"]).first()
            print("oof")
            game["home_name"] = home_team.name
            game["away_name"] = away_team.name
            games_with_names.append(game)
        return jsonify(games_with_names)

    elif home is None or away is None:
        return ("'home' and 'away' are necessary query parameters when not using the 'all' query parameter")
    else:
        rankings = Rankings()
        rankings = rankings.current
        print(home)
        print(away)

        home_team = db.session.query(Team).filter(
            Team.id == home).first()
        away_team = db.session.query(Team).filter(
            Team.id == away).first()
        print("ooooof")
        data = {
            "year": dt.today().year,
            "month": dt.today().month,
            "day": dt.today().day,
            "home_name": home_team.name,
            "home_rank": float(rankings.get(home_team.id.lower(), 0)),
            "away_name": away_team.name,
            "away_rank": float(rankings.get(away_team.id.lower(), 0))
        }

        res = requests.post(
            "http://ncaab.herokuapp.com/", data=json.dumps(data))
        res = res.json()

        home_projection = res["home_score"]
        away_projection = res["away_score"]

        print("ummmmm")
        return jsonify({
            'home_id': home_team.id,
            'away_id': away_team.id,
            'home_name': home_team.name,
            'away_name': away_team.name,
            'home_projection': home_projection,
            'away_projection': away_projection
        })


@app.route("/teams/")
def teams():
    try:
        teams = Team.query.all()
        return jsonify([t.serialize() for t in teams])
    except Exception as e:
        return(str(e))


if __name__ == '__main__':
    app.run()
