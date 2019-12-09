#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import models
from models import Venue, Artist, Show
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# DONE: connect to a local postgresql database

db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#see models.py


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Venues
#----------------------------------------------------------------------------#

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues_by_areas = Venue.query.distinct(Venue.city, Venue.state).all()
  data=[venue.serialize_by_area for venue in venues_by_areas]
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  search_str = request.form.get('search_term', None)
  venues = Venue.query.filter(Venue.name.ilike("%{}%".format(search_str))).all()
  num_venues = len(venues)
  response={
    "count": num_venues,
    "data": [venue.serialize for venue in venues]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_str', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  if venue is None:
        flash('An error occurred. Venue does not exist!')
        return render_template('pages/home.html')
  data = venue.serialize_incl_shows
  return render_template('pages/show_venue.html', venue = data)

#  Create Venue
#----------------------------------------------------------------------------#

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  try:
    new_data = VenueForm(request.form)
    venue = Venue(name=new_data.name.data,
            address=new_data.address.data,
            city=new_data.city.data,
            state=new_data.state.data,
            phone=new_data.phone.data,            
            facebook_link=new_data.facebook_link.data,
            image_link=new_data.image_link.data,
            genres=','.join(new_data.genres.data))
    if not venue.isDuplicate():
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + new_data.name.data + ' was successfully listed!')
    else:
      flash('Venue ' + new_data.name.data + ' was not inserted since it is already listed!')
  except:
    db.session.rollback() 
    # DONE: on unsuccessful db insert, flash an error instead. 
    flash('An error occurred. Venue ' + new_data.name.data + ' could not be listed.')
  finally:
    db.session.close()
  
  return render_template('pages/home.html')

#  Update Venue
#----------------------------------------------------------------------------#
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # DONE: populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)
  if venue is None:
        flash('An error occurred. Venue does not exist!')
        return render_template('pages/home.html')
  venue = venue.serialize
  form=VenueForm(data=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue_form = VenueForm(request.form)
    venue = Venue.query.get(venue_id)
    venue.name = venue_form.name.data
    venue.address = venue_form.address.data
    venue.city = venue_form.city.data
    venue.state = venue_form.state.data
    venue.phone = venue_form.phone.data           
    venue.facebook_link = venue_form.facebook_link.data
    venue.image_link = venue_form.image_link.data
    venue.genres = ','.join(venue_form.genres.data)
    db.session.commit()
    # on successful db update, flash success
    flash('Venue ' + venue_form.name.data + ' was successfully updated!')
  except:
    db.session.rollback() 
    # DONE: on unsuccessful db update, flash an error instead. 
    flash('An error occurred. Venue ' + venue_form.name.data + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Delete Venue
#----------------------------------------------------------------------------#
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  try:
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
    flash('Venue number ' + venue_id + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue number' + venue_id + ' could not be deleted.')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
#  Artists
#----------------------------------------------------------------------------#
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  artists = Artist.query.all()
  data=[artist.serialize for artist in artists]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
    search_str = request.form.get('search_term', None)
    artists = Artist.query.filter(
        Artist.name.ilike("%{}%".format(search_str))).all()
    num_artists = len(artists)
    response = {
        "count": num_artists,
        "data": [artist.serialize for artist in artists]
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_str', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # DONE: replace with real artist data from the artists table, using artist_id
  artist = Artist.query.get(artist_id)
  if artist is None:
        flash('An error occurred. Artist does not exist!')
        return render_template('pages/home.html')
  data = artist.serialize_incl_shows
  return render_template('pages/show_artist.html', artist=data)

#  Create Artist
#----------------------------------------------------------------------------#

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Artist record in the db, instead
  # DONE: modify data to be the data object returned from db insertion

  try:
    new_data = ArtistForm(request.form)
    artist = Artist(name=new_data.name.data,
            city=new_data.city.data,
            state=new_data.state.data,
            phone=new_data.phone.data,            
            facebook_link=new_data.facebook_link.data,
            image_link=new_data.image_link.data,
            genres=','.join(new_data.genres.data))
    if not artist.isDuplicate():
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + new_data.name.data + ' was successfully listed!')
    else:
      flash('Artist ' + new_data.name.data + ' was not inserted since it is already listed!')
  except:
    db.session.rollback() 
    # DONE: on unsuccessful db insert, flash an error instead. 
    flash('An error occurred. Artist ' + new_data.name.data + ' could not be listed.')
  finally:
    db.session.close()
  return render_template('pages/home.html')

#  Update Artist
#----------------------------------------------------------------------------#
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # DONE: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  if artist is None:
        flash('An error occurred. Artist does not exist!')
        return render_template('pages/home.html')
  artist = artist.serialize
  form = ArtistForm(data=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist_form = ArtistForm(request.form)
    artist = Artist.query.get(artist_id)
    artist.name = artist_form.name.data
    artist.city = artist_form.city.data
    artist.state = artist_form.state.data
    artist.phone = artist_form.phone.data           
    artist.facebook_link = artist_form.facebook_link.data
    artist.image_link = artist_form.image_link.data
    artist.genres = ','.join(artist_form.genres.data)
    db.session.update(artist)
    db.session.commit()
    # on successful db update, flash success
    flash('Artst ' + artist_form.name.data + ' was successfully updated!')
  except:
    db.session.rollback() 
    # DONE: on unsuccessful db update, flash an error instead. 
    flash('An error occurred. Artist ' + artist_form.name.data + ' could not be updated.')
  finally:
    db.session.close()
  return redirect(url_for('show_artist', artist_id=artist_id))

#----------------------------------------------------------------------------#
#  Shows
#----------------------------------------------------------------------------#

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = db.session.query(Show).order_by(Show.start_time)
  data=[show.serialize for show in shows]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
  try:
    new_data = ShowForm(request.form)
    show = Show(
            artist_id=new_data.artist_id.data,
            venue_id=new_data.venue_id.data,
            start_time=new_data.start_time.data
        )
    if not show.isDuplicate():
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    else:
      flash('Show was not inserted since it is already listed!')
  except:
    db.session.rollback() 
    # DONE: on unsuccessful db insert, flash an error instead. 
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#----------------------------------------------------------------------------#
#Error Handlers
#----------------------------------------------------------------------------#
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
