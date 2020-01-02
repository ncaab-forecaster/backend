# pylint: disable=E1101
# Needed because pylint is incompatible with SQL Alchemy for some reason...
from app import db


class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<id: {self.id} name: {self.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Game(db.Model):
    __tablename__ = 'game'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date(), nullable=False, primary_key=True)
    home = db.Column(db.Integer(), db.ForeignKey(
        "team.id"), nullable=False, primary_key=True)
    away = db.Column(db.Integer(), db.ForeignKey(
        "team.id"), nullable=False, primary_key=True)
    home_score = db.Column(db.Integer())
    away_score = db.Column(db.Integer())
    home_projection = db.Column(db.Float())
    away_projection = db.Column(db.Float())

    def __init__(self, date, home, away, home_score, away_score, home_projection, away_projection):
        self.date = date
        self.home = home
        self.away = away
        self.home_score = home_score
        self.away_score = away_score
        self.home_projection = home_projection
        self.away_projection = away_projection

    def __repr__(self):
        return f'<id: {self.id} date: {self.date} home: {self.home} away: {self.away}>'

    def serialize(self):
        return {
            'id': self.id,
            'date': self.date,
            'home': self.home,
            'away': self.away,
            'home_score': self.home_score,
            'away_score': self.away_score,
            'home_projection': self.home_projection,
            'away_projection': self.away_projection
        }
