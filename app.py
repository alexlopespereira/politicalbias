# coding=utf-8

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Sequence

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://test:test@localhost:5432/news'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Article(db.Model):
     __tablename__ = 'article'
     id = db.Column(db.Integer)
     website = db.Column(db.String)
     title = db.Column(db.String)
     section = db.Column(db.String)
     url = db.Column(db.String, primary_key=True)
     content = db.Column(db.String)
     author = db.Column(db.String)
     subtitle = db.Column(db.String)
     publish_date = db.Column(db.Date)
     publish_time = db.Column(db.Time)

     def __repr__(self):
        return "<User(website='%s', title='%s')>" % (
                             self.website, self.title)


