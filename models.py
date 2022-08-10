from app import db
from datetime import datetime

genre_artist_table = db.Table(
    "genre_artist_table",
    db.Column("genre", db.Integer, db.ForeignKey("Genre.id"), primary_key=True),
    db.Column("artist", db.Integer, db.ForeignKey("Artist.id"), primary_key=True),
)

genre_venue_table = db.Table(
    "genre_venue_table",
    db.Column("genre", db.Integer, db.ForeignKey("Genre.id"), primary_key=True),
    db.Column("venue", db.Integer, db.ForeignKey("Venue.id"), primary_key=True),
)


class Genre(db.Model):
    __tablename__ = "Genre"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __repr__(self):
        return f"<Genre id: {self.id} name: {self.name}>"


class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)

    artist = db.relationship(
        "Artist",
        foreign_keys=[artist_id],
    )
    venue = db.relationship(
        "Venue",
        foreign_keys=[venue_id],
    )

    def __repr__(self):
        return f"<Show id: {self.id} artist_id: {self.artist_id} venue_id: {self.venue_id}>"


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    genres = db.relationship(
        "Genre", secondary=genre_venue_table, backref=db.backref("venues")
    )
    venue_shows = db.relationship("Show", backref=db.backref("venue_shows"), lazy=True)

    def __repr__(self):
        return f"<Venue id: {self.id} name: {self.name}>"


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    looking_for_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))

    genres = db.relationship(
        "Genre", secondary=genre_artist_table, backref=db.backref("artist")
    )
    artist_shows = db.relationship(
        "Show", backref=db.backref("artist_artist"), lazy=True
    )

    def __repr__(self):
        return f"<Artist id: {self.id} name: {self.name}>"
