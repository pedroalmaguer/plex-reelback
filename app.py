from flask import Flask, render_template, request, session, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import json
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
app.secret_key = "your-secret-key-here"

# Disable CSRF protection globally
app.config['WTF_CSRF_ENABLED'] = False

#Define the database path
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "taut.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define ORM models
class SessionHistory(db.Model):
    __tablename__ = 'session_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    started = db.Column(db.Integer, nullable=False)  # Unix timestamp
    stopped = db.Column(db.Integer, nullable=False)  # Unix timestamp
    parent_rating_key = db.Column(db.Integer, nullable=True)
    media_type = db.Column(db.Integer, nullable=False)
    rating_key = db.Column(db.Integer, nullable=True)

class SessionHistoryMetadata(db.Model):
    __tablename__ = 'session_history_metadata'
    rating_key = db.Column(db.Integer, primary_key=True)
    full_title = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    grandparent_title = db.Column(db.String, nullable=False)
    studio = db.Column(db.String, nullable=True)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)

######################################################################
######################################################################
 # Load excluded users from JSON
try:
    with open('excluded_users.json') as f:
        excluded_data = json.load(f)
        excluded_user_ids = excluded_data.get("excluded_user_ids", [])
        excluded_usernames = excluded_data.get("excluded_usernames", [])
except FileNotFoundError:
    excluded_user_ids = []
    excluded_usernames = []
    print("excluded_users.json not found.")
    



######################################################################
######################################################################
# Route for index
@app.route('/')
def index():
    users = User.query.filter(~User.user_id.in_(excluded_user_ids), ~User.username.in_(excluded_usernames)).all()
   # users = User.query.all()
   # name = request.args.get('name')
   # return render_template('index.html', users=users, name=name) url example
    return render_template('index.html', users=users)

# Route to set user
@app.route('/set_user', methods=['POST'])

def set_user():
    user_id = request.form.get('user_id')
    session['user_id'] = user_id
    return jsonify({'success': True})

# Route for stats overview
@app.route('/stats_overview', methods=['POST'])
def stats_overview():
    """
    Gathers and displays an overview of a user's statistics, including:
    - Total sessions
    - Total minutes watched
    - Number of unique titles watched

    Query Logic:
    - Fetch total number of viewing sessions for the user.
    - Calculate total minutes watched by summing the duration of all sessions.
    - Count the number of unique titles (movies/shows) the user has watched.
    """
    user_id = session.get('user_id')
    if not user_id:
        app.logger.error("No user selected.")
        return "<p>No user selected. Please select a user first.</p>"

    try:
        total_sessions = SessionHistory.query.filter_by(user_id=user_id).count()
        total_minutes_watched = db.session.query(
            db.func.sum((SessionHistory.stopped - SessionHistory.started) / 60)
        ).filter(SessionHistory.user_id == user_id).scalar()

        unique_titles_watched = db.session.query(
            db.func.count(db.distinct(SessionHistory.parent_rating_key))
        ).filter(SessionHistory.user_id == user_id).scalar()

        stats = {
            'total_sessions': total_sessions,
            'total_minutes_watched': total_minutes_watched or 0,
            'unique_titles_watched': unique_titles_watched or 0
        }
        app.logger.debug(f"Stats: {stats}")
        username = User.query.filter_by(user_id=user_id).first().username
        return render_template('stats_overview.html', stats=stats, username=username)
    except Exception as e:
        app.logger.error(f"Error in stats_overview: {e}")
        return f"Error occurred: {e}", 500



# Route for movies watched in 2024
@app.route('/movies_2024', methods=['POST'])
def movies_2024():
    """
    Gathers and displays data on movies watched in 2024 by the selected user, including:
    - Title of the movie
    - Total number of views for each movie
    - Total time spent watching each movie

    Query Logic:
    - Join `SessionHistory` and `SessionHistoryMetadata` to fetch metadata for each movie session.
    - Filter sessions by `media_type = 'movie'` and user ID.
    - Group data by movie title (`full_title`) to calculate watch counts and total viewing time.
    """
    user_id = session.get('user_id')
    if not user_id:
        app.logger.error("No user selected.")
        return "<p>No user selected. Please select a user first.</p>"

    try:
        movies = db.session.query(
            SessionHistoryMetadata.full_title.label('title'),
            db.func.count(SessionHistory.rating_key).label('watch_count'),
            db.func.sum((SessionHistory.stopped - SessionHistory.started) / 60).label('total_time')
        ).join(SessionHistory, SessionHistory.rating_key == SessionHistoryMetadata.rating_key)\
        .filter(SessionHistory.user_id == user_id)\
        .filter(SessionHistory.media_type == 'movie')\
        .group_by(SessionHistoryMetadata.full_title)\
        .order_by(db.func.count(SessionHistory.rating_key).desc())\
        .limit(10)\
        .all()

        app.logger.debug(f"Fetched movies: {movies}")
        username = User.query.filter_by(user_id=user_id).first().username
        return render_template('movies_2024.html', movies=movies, username=username)
    except Exception as e:
        app.logger.error(f"Error in movies_2024: {e}")
        return f"Error occurred: {e}", 500

# Route for Last watched
@app.route('/last_watched', methods=['POST'])
def last_watched():
    """
    Gathers and displays the most recently watched items for the selected user, including:
    - Title of the item
    - When the item was last watched (formatted as a readable timestamp)
    - Type of the item (movie or episode)

    Query Logic:
    - Join `SessionHistory` and `SessionHistoryMetadata` to fetch metadata for each session.
    - Filter sessions by `media_type` to include movies and episodes.
    - Order results by `stopped` timestamp in descending order to fetch the latest items.
    - Limit results to the 10 most recent items.
    """
    user_id = session.get('user_id')
    if not user_id:
        app.logger.error("No user selected.")
        return "<p>No user selected. Please select a user first.</p>"

    try:
        last_watched_items = db.session.query(
            SessionHistoryMetadata.full_title.label('title'),
            db.func.strftime('%Y-%m-%d %H:%M:%S', db.func.datetime(SessionHistory.stopped, 'unixepoch')).label('watch_time'),
            SessionHistory.media_type
        ).join(SessionHistory, SessionHistory.rating_key == SessionHistoryMetadata.rating_key)\
        .filter(SessionHistory.user_id == user_id)\
        .filter(SessionHistory.media_type.in_(['movie', 'episode']))\
        .order_by(SessionHistory.stopped.desc())\
        .limit(10)\
        .all()

        app.logger.debug(f"Fetched last watched items: {last_watched_items}")
        username = User.query.filter_by(user_id=user_id).first().username
        return render_template('last_watched.html', items=last_watched_items, username=username)
    except Exception as e:
        app.logger.error(f"Error in last_watched: {e}")
        return f"Error occurred: {e}", 500
    
# Route for most popular items
@app.route('/most_popular', methods=['POST'])
def most_popular():
    """
    Gathers and displays the most popular movies and TV shows for 2024, including:
    - Title of the media
    - Total number of views
    - Media type (movie or show)

    Query Logic:
    - Movies:
        - Join `SessionHistory` and `SessionHistoryMetadata` to fetch metadata for each session.
        - Filter by `media_type = 'movie'`.
        - Group by movie title (`full_title`) to calculate total views.
    - TV Shows:
        - Similar to movies but uses `media_type = 'episode`.
        - Aggregates episodes into shows using `parent_rating_key` and `grandparent_title`.
    - Results for movies and shows are combined and passed to the template.
    """
    try:
        # Query for most popular movies
        most_popular_movies = db.session.query(
            SessionHistoryMetadata.full_title.label('title'),
            db.func.count(SessionHistory.rating_key).label('watch_count'),
            db.literal('movie').label('type')
        ).join(
            SessionHistory,
            SessionHistory.rating_key == SessionHistoryMetadata.rating_key
        ).filter(
            SessionHistory.media_type == 'movie',
            SessionHistory.started >= db.func.strftime('%s', '2024-01-01'),
            SessionHistory.stopped <= db.func.strftime('%s', '2024-12-31'),
            ~SessionHistory.user_id.in_(excluded_user_ids)
        ).group_by(
            SessionHistoryMetadata.full_title
        ).order_by(
            db.func.count(SessionHistory.rating_key).desc()
        ).limit(10).all()

        # Format movies as dictionaries
        most_popular_movies = [
            {'title': title, 'watch_count': watch_count, 'type': type_}
            for title, watch_count, type_ in most_popular_movies
        ]

        # Query for most popular TV shows
        most_popular_shows = db.session.query(
            SessionHistory.parent_rating_key.label('show_id'),
            SessionHistoryMetadata.grandparent_title.label('title'),
            db.func.count(SessionHistory.rating_key).label('watch_count')
        ).join(
            SessionHistoryMetadata,
            SessionHistory.rating_key == SessionHistoryMetadata.rating_key
        ).filter(
            SessionHistory.media_type == 'episode',
            SessionHistory.started >= db.func.strftime('%s', '2024-01-01'),
            SessionHistory.stopped <= db.func.strftime('%s', '2024-12-31'),
            ~SessionHistory.user_id.in_(excluded_user_ids)
        ).group_by(
            SessionHistory.parent_rating_key,
            SessionHistoryMetadata.grandparent_title
        ).order_by(
            db.func.count(SessionHistory.rating_key).desc()
        ).limit(10).all()

        # Format shows as dictionaries
        most_popular_shows = [
            {'title': title, 'watch_count': watch_count, 'type': 'show'}
            for _, title, watch_count in most_popular_shows
        ]

        # Combine results
        most_popular_items = most_popular_movies + most_popular_shows

        return render_template('most_popular.html', items=most_popular_items)

    except Exception as e:
        app.logger.error(f"Error in most_popular route: {e}")
        return f"Error occurred: {e}", 500

@app.route('/top_studios', methods=['POST'])
def top_studios():
    """
    Retrieves the top 5 movie studios watched by the selected user.
    """
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'No user selected. Please select a user first.'}), 400

    try:
        # Query top 5 studios
        top_studios = db.session.query(
            SessionHistoryMetadata.studio.label('studio'),
            db.func.count(SessionHistory.rating_key).label('watch_count'),
            db.func.sum((SessionHistory.stopped - SessionHistory.started) / 60).label('total_time')
        ).join(
            SessionHistory, SessionHistory.rating_key == SessionHistoryMetadata.rating_key
        ).filter(
            SessionHistory.user_id == user_id,
            SessionHistory.media_type == 'movie'
        ).group_by(
            SessionHistoryMetadata.studio
        ).order_by(
            db.func.count(SessionHistory.rating_key).desc()
        ).limit(5).all()

        # Format data for the template
        studios = [
            {
                'studio': studio if studio else 'Unknown Studio',
                'watch_count': watch_count,
                'total_time': round(total_time, 2) if total_time else 0
            }
            for studio, watch_count, total_time in top_studios
        ]

        return render_template('top_studios.html', studios=studios)
    except Exception as e:
        app.logger.error(f"Error in top_studios: {e}")
        return f"Error occurred: {e}", 500



# Debugging routes
# @app.route('/test_users')
# def test_users():
#     try:
#         users = User.query.all()
#         return f"Users: {[user.username for user in users]}"
#     except Exception as e:
#         return f"Error fetching users: {e}"

@app.route('/test_db')
def test_db():
    try:
        users = User.query.all()
        return jsonify({'success': True, 'user_count': len(users)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def format_duration(minutes):
    """Convert minutes to human readable duration."""
    if not minutes:
        return "0 minutes"
        
    # Round up to nearest minute
    minutes = round(minutes)
    
    days = minutes // (24 * 60)
    remaining_minutes = minutes % (24 * 60)
    
    hours = remaining_minutes // 60
    final_minutes = remaining_minutes % 60
    
    parts = []
    if days > 0:
        parts.append(f"{days} {'day' if days == 1 else 'days'}")
    if hours > 0:
        parts.append(f"{hours} {'hour' if hours == 1 else 'hours'}")
    if final_minutes > 0:
        parts.append(f"{final_minutes} {'minute' if final_minutes == 1 else 'minutes'}")
    
    return ", ".join(parts)

# In your route, use it like this:
@app.route('/overview', methods=['POST'])
def overview():
    total_minutes = 999197.37  # Your actual value here
    formatted_duration = format_duration(total_minutes)
    return render_template('partials/overview.html', watch_time=formatted_duration)

if __name__ == '__main__':
    app.run(debug=True)
