from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask import Flask
from datetime import datetime
from sqlalchemy.sql import exists

db = SQLAlchemy()

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String())
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'address': self.address,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'genres': self.genres.split(','),
                'seeking_talent': self.seeking_talent,
                'seeking_description': self.seeking_description,
                'website': self.website,
                'num_shows': self.get_num_shows() }
                
    # serializes the venue, plus adds all of the venue's show data
    @property
    def serialize_incl_shows(self):
        return {'id': self.id,
                'name': self.name,
                'city': self.city,
                'state': self.state,
                'phone': self.phone,
                'address': self.address,
                'image_link': self.image_link,
                'genres': self.genres.split(','),
                'facebook_link': self.facebook_link,
                'seeking_talent': self.seeking_talent,
                'seeking_description': self.seeking_description,
                'website': self.website,
                'num_shows': self.get_num_shows(), 
                'upcoming_shows': [show.serialize for show in self.get_upcoming_shows()],
                'past_shows': [show.serialize for show in self.get_past_shows()],
                'upcoming_shows_count': self.get_upcoming_shows_count(),
                'past_shows_count': self.get_past_shows_count()
                }
    
    @property
    def serialize_by_area(self):
        return {'city': self.city,
                'state': self.state,
                'venues': [venue.serialize for venue in self.get_venues()]
                }

    
    def __repr__(self):
        return '<Venue %r>' % self

    # determines if the venue to be added is already in the database, i.e
    # a venue with the same name, city and state is already present
    def isDuplicate(self):
        return db.session.query(exists().where(func.lower(Venue.name) == func.lower(
            self.name) and func.lower(Venue.city) == func.lower(self.city) and func.lower(
                Venue.state) == func.lower(self.state))).scalar()

    def get_venues(self):
        return Venue.query.filter(Venue.city == self.city, 
                Venue.state == self.state).all()

    def get_num_shows(self):
        return Show.query.filter(
                    Show.start_time > datetime.now(),
                    Show.venue_id == self.id) 

    def get_upcoming_shows(self):
        return Show.query.filter(
                    Show.start_time > datetime.now(),Show.venue_id == self.id).all()

    def get_past_shows(self):
        return Show.query.filter(
                    Show.start_time < datetime.now(),Show.venue_id == self.id).all()

    def get_upcoming_shows_count(self):
        return len(Show.query.filter(
            Show.start_time > datetime.now(),Show.venue_id == self.id).all())
    
    def get_past_shows_count(self):
        return len(Show.query.filter(
            Show.start_time < datetime.now(),Show.venue_id == self.id).all())


    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String())
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
        return '<Artist %r>' % self

    # determines if the artist to be added is already in the database
    def isDuplicate(self):
        return db.session.query(exists().where(func.lower(Artist.name) == func.lower(
            self.name))).scalar()

    @property
    def serialize(self):
        return {'id': self.id,
                'name': self.name,               
                'city': self.city,
                'state': self.state,
                'address': self.address,
                'phone': self.phone,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'genres': self.genres.split(','),
                'website': self.website,
                'seeking_venue': self.seeking_venue,
                'seeking_description': self.seeking_description                
                }

    # serializes the artist, plus adds all of the artist's show data
    @property
    def serialize_incl_shows(self):
        return {'id': self.id,
                'name': self.name,               
                'city': self.city,
                'state': self.state,
                'address': self.address,
                'phone': self.phone,
                'image_link': self.image_link,
                'facebook_link': self.facebook_link,
                'genres': self.genres.split(','),
                'website': self.website,
                'seeking_venue': self.seeking_venue,
                'seeking_description': self.seeking_description,               
                'upcoming_shows': [show.serialize for show in self.get_upcoming_shows()],
                'past_shows': [show.serialize for show in self.get_past_shows()],
                'upcoming_shows_count': self.get_upcoming_shows_count(),
                'past_shows_count': self.get_past_shows_count()}
    

    def get_upcoming_shows(self): 
        return Show.query.filter(Show.start_time > datetime.now(),Show.artist_id == self.id).all()
                
                
    def get_past_shows(self): 
        return Show.query.filter(
                    Show.start_time < datetime.now(),Show.artist_id == self.id).all()

    def get_upcoming_shows_count(self): 
        return len(Show.query.filter(
                    Show.start_time > datetime.now(),Show.artist_id == self.id).all())

    def get_past_shows_count(self): 
        return len(Show.query.filter(
                    Show.start_time < datetime.now(),Show.artist_id == self.id).all())

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    venue = db.relationship('Venue', backref=db.backref('shows', cascade='all, delete'))
    artist = db.relationship('Artist', backref=db.backref('shows', cascade='all, delete'))

    @property
    def serialize(self):
        return {'id': self.id,
                'venue_id': self.venue_id,               
                'artist_id': self.artist_id,
                'start_time': self.start_time.strftime("%m/%d/%Y, %H:%M:%S"),  
                'artist_image_link': self.get_artist_image(),
                'venue_image_link': self.get_venue_image(),
                'artist_name': self.get_artist_name(),
                'venue_name': self.get_venue_name()
                }
                
    def __repr__(self):
        return '<Show %r>' % self

    def isDuplicate(self):
        query = db.session.query(Show).filter(Show.artist_id == self.artist_id).filter(
            Show.venue_id == self.venue_id).filter(Show.start_time == self.start_time).all()
        return len(query) > 0 
    
    def get_artist_image(self):
        artist = Artist.query.get(self.artist_id)
        return artist.image_link

   
    def get_venue_image(self):
        venue = Venue.query.get(self.artist_id)
        return venue.image_link

    
    def get_venue_name(self):
        venue = Venue.query.get(self.artist_id)
        return venue.name

    
    def get_artist_name(self):
        artist = Artist.query.get(self.artist_id)
        return artist.name