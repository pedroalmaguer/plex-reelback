from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taut.db'  # Path to your SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

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
    rating_key = db.Column(db.Integer, nullable=False)

class SessionHistoryMetadata(db.Model):
    __tablename__ = 'session_history_metadata'
    rating_key = db.Column(db.Integer, primary_key=True)
    full_title = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)

# Route for index
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

# Route to set user
@app.route('/set_user', methods=['POST'])
def set_user():
    user_id = request.form.get('user_id')
    if user_id:
        session['user_id'] = int(user_id)
    return redirect('/')

# Route for stats overview
@app.route('/stats_overview', methods=['POST'])
def stats_overview():
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
        .all()

        app.logger.debug(f"Fetched movies: {movies}")
        username = User.query.filter_by(user_id=user_id).first().username
        return render_template('movies_2024.html', movies=movies, username=username)
    except Exception as e:
        app.logger.error(f"Error in movies_2024: {e}")
        return f"Error occurred: {e}", 500


@app.route('/last_watched', methods=['POST'])
def last_watched():
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

# Debugging routes
@app.route('/test_users')
def test_users():
    try:
        users = User.query.all()
        return f"Users: {[user.username for user in users]}"
    except Exception as e:
        return f"Error fetching users: {e}"

if __name__ == '__main__':
    app.run(debug=True)
