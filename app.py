# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import sys
import json
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    abort,
    jsonify,
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

from models import *

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    error = False
    data = []

    venues = Venue.query.all()

    locations = set()
    for venue in venues:
        locations.add((venue.state, venue.city))

    unique_locations = list(locations)

    current_date = datetime.now()

    for location in locations:
        venue_list = []

        for venue in venues:
            if (venue.state == location[0]) and (venue.city == location[1]):
                shows = Show.query.filter(
                    Show.venue_id == venue.id, Show.start_time > current_date
                ).all()

                venue_list.append(
                    {
                        "id": venue.id,
                        "name": venue.name,
                        "num_upcoming_shows": len(shows),
                    }
                )

        data.append({"city": location[1], "state": location[0], "venues": venue_list})

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    data = []
    search_term = request.form.get("search_term", "")
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term.lower()}%")).all()
    current_date = datetime.now()

    for venue in venues:
        shows = Show.query.filter(
            Show.venue_id == venue.id, Show.start_time > current_date
        ).all()

        data.append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(shows),
            }
        )

    response = {
        "count": len(data),
        "data": data,
    }

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=search_term,
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)

    if venue:
        now = datetime.now()
        genres = []
        past_shows = []
        upcoming_shows = []

        for genre in venue.genres:
            genres.append(genre.name)

        upcoming_shows_list = Show.query.filter(
            Show.venue_id == venue_id, Show.start_time > now
        ).all()
        past_shows_list = Show.query.filter(
            Show.venue_id == venue_id, Show.start_time < now
        ).all()

        for show in upcoming_shows_list:
            upcoming_shows.append(
                {
                    "artist_id": show.artist.id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": format_datetime(
                        show.start_time,
                    ),
                }
            )

        for show in past_shows_list:
            past_shows.append(
                {
                    "artist_id": show.artist.id,
                    "artist_name": show.artist.name,
                    "artist_image_link": show.artist.image_link,
                    "start_time": format_datetime(show.start_time),
                }
            )

        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website_link,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.looking_for_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": len(upcoming_shows),
        }

        return render_template("pages/show_venue.html", venue=data)
    else:
        return redirect(url_for("index"))


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    form = VenueForm(request.form)

    if form.validate():
        error = False

        try:
            venue_genres = []

            for genre in form.genres.data:
                existing_genre = Genre.query.filter_by(name=genre).one_or_none()
                if not existing_genre:
                    new_genre = Genre(name=genre)
                    venue_genres.append(new_genre)
                    db.session.add(new_genre)
                else:
                    venue_genres.append(existing_genre)

            venue = Venue(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                address=form.address.data,
                phone=form.phone.data,
                genres=venue_genres,
                looking_for_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
                image_link=form.image_link.data,
                website_link=form.website_link.data,
                facebook_link=form.facebook_link.data,
            )

            db.session.add(venue)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            flash(f"An error occurred. Venue {form.name.data} could not be listed.")
            abort(500)
        else:
            flash(f"Venue {form.name.data} was successfully listed!")
            return redirect(url_for("venues"))
    else:
        flash(form.errors)
        return redirect(url_for("create_venue_submission"))


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)

    if venue:
        error = False
        name = venue.name

        try:
            db.session.delete(venue)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            flash(f"An error occurred deleting venue {name}.")
            abort(500)
        else:
            flash(f"Venue {name} was successfully deleted!")
            return jsonify({"deleted": True})

    else:
        return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    artists = Artist.query.all()
    data = [{"id": artist.id, "name": artist.name} for artist in artists]

    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    data = []
    search_term = request.form.get("search_term", "")
    artists = Artist.query.filter(Artist.name.ilike(f"%{search_term.lower()}%")).all()
    current_date = datetime.now()

    for artist in artists:
        shows = Show.query.filter(
            Show.artist_id == artist.id, Show.start_time > current_date
        ).all()

        data.append(
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": len(shows),
            }
        )

    response = {
        "count": len(data),
        "data": data,
    }

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=search_term,
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)

    if artist:
        now = datetime.now()
        genres = []
        past_shows = []
        upcoming_shows = []

        for genre in artist.genres:
            genres.append(genre.name)

        upcoming_shows_list = Show.query.filter(
            Show.artist_id == artist.id, Show.start_time > now
        ).all()
        past_shows_list = Show.query.filter(
            Show.artist_id == artist.id, Show.start_time < now
        ).all()

        for show in upcoming_shows_list:
            upcoming_shows.append(
                {
                    "venue_id": show.venue.id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": format_datetime(show.start_time),
                }
            )

        for show in past_shows_list:
            past_shows.append(
                {
                    "venue_id": show.venue.id,
                    "venue_name": show.venue.name,
                    "venue_image_link": show.venue.image_link,
                    "start_time": format_datetime(show.start_time),
                }
            )

        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.looking_for_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows": upcoming_shows,
            "upcoming_shows_count": len(upcoming_shows),
        }
        return render_template("pages/show_artist.html", artist=data)
    else:
        return redirect(url_for("index"))


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)

    if artist:
        genres = []

        for genre in artist.genres:
            genres.append(genre.name)

        form = ArtistForm(obj=artist)
        return render_template("forms/edit_artist.html", form=form, artist=artist)
    else:
        return redirect(url_for("index"))


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)

    if not artist:
        return redirect(url_for("index"))

    form = ArtistForm(request.form)

    if form.validate():
        error = False

        try:
            artist_genres = []

            for genre in form.genres.data:
                existing_genre = Genre.query.filter_by(name=genre).one_or_none()
                if not existing_genre:
                    new_genre = Genre(name=genre)
                    artist_genres.append(new_genre)
                    db.session.add(new_genre)
                else:
                    artist_genres.append(existing_genre)

            artist.name = form.name.data
            artist.city = form.city.data
            artist.state = form.state.data
            artist.phone = form.phone.data
            artist.genres = artist_genres
            artist.looking_for_venue = form.seeking_venue.data
            artist.seeking_description = form.seeking_description.data
            artist.image_link = form.image_link.data
            artist.website_link = form.website_link.data
            artist.facebook_link = form.facebook_link.data

            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            flash(f"An error occurred. Artist {form.name.data} could not be edited.")
            abort(500)
        else:
            flash(f"Artist {form.name.data} was successfully edited!")
            return redirect(url_for("show_artist", artist_id=artist_id))
    else:
        flash(form.errors)
        return redirect(url_for("edit_artist_submission"))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)

    if venue:
        genres = []

        for genre in venue.genres:
            genres.append(genre.name)

        form = VenueForm(obj=venue)
        return render_template("forms/edit_venue.html", form=form, venue=venue)
    else:
        return redirect(url_for("index"))


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)

    if not venue:
        return redirect(url_for("index"))

    form = VenueForm(request.form)

    if form.validate():
        error = False

        try:
            venue_genres = []

            for genre in form.genres.data:
                existing_genre = Genre.query.filter_by(name=genre).one_or_none()
                if not existing_genre:
                    new_genre = Genre(name=genre)
                    venue_genres.append(new_genre)
                    db.session.add(new_genre)
                else:
                    venue_genres.append(existing_genre)

            venue.name = form.name.data
            venue.city = form.city.data
            venue.state = form.state.data
            venue.address = form.address.data
            venue.phone = form.phone.data
            venue.genres = venue_genres
            venue.looking_for_talent = form.seeking_talent.data
            venue.seeking_description = form.seeking_description.data
            venue.image_link = form.image_link.data
            venue.website_link = form.website_link.data
            venue.facebook_link = form.facebook_link.data

            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            flash(f"An error occurred. Venue {form.name.data} could not be edited.")
            abort(500)
        else:
            flash(f"Venue {form.name.data} was successfully edited!")
            return redirect(url_for("show_venue", venue_id=venue_id))
    else:
        flash(form.errors)
        return redirect(url_for("edit_venue_submission"))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    form = ArtistForm(request.form)

    if form.validate():
        error = False

        try:
            artis_genres = []

            for genre in form.genres.data:
                existing_genre = Genre.query.filter_by(name=genre).one_or_none()
                if not existing_genre:
                    new_genre = Genre(name=genre)
                    artis_genres.append(new_genre)
                    db.session.add(new_genre)
                else:
                    artis_genres.append(existing_genre)

            artist = Artist(
                name=form.name.data,
                city=form.city.data,
                state=form.state.data,
                phone=form.phone.data,
                genres=artis_genres,
                looking_for_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data,
                image_link=form.image_link.data,
                website_link=form.website_link.data,
                facebook_link=form.facebook_link.data,
            )

            db.session.add(artist)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            flash(f"An error occurred. Artist {form.name.data} could not be listed.")
            abort(500)
        else:
            flash(f"Artist {form.name.data} was successfully listed!")
            return redirect(url_for("artists"))
    else:
        flash(form.errors)
        return redirect(url_for("create_artist_submission"))


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    shows = Show.query.all()
    data = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": format_datetime(str(show.start_time)),
        }
        for show in shows
    ]

    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    form = ShowForm(request.form)

    if form.validate():
        error = False

        try:
            venue = Venue.query.get(form.venue_id.data or 0)
            if not venue:
                flash(f"No venue with that ID exists!")
                return redirect(url_for("create_show_submission"))

            artist = Artist.query.get(form.artist_id.data or 0)
            if not artist:
                flash(f"No artist with that ID exists!")
                return redirect(url_for("create_show_submission"))

            show = Show(
                venue=venue,
                artist=artist,
                start_time=form.start_time.data,
            )

            db.session.add(show)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            flash(f"An error occurred. Show could not be listed.")
            abort(500)
        else:
            flash(f"Show was successfully listed!")
            return redirect(url_for("shows"))
    else:
        flash(form.errors)
        return redirect(url_for("create_show_submission"))


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
