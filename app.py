from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DB_PATH = 'taut.db'
logging.basicConfig(level=logging.DEBUG)

def query_db(query, params=()):
    """Helper function to query the SQLite database."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row  # Enables dict-like access
    cursor = connection.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    connection.close()
    return [dict(row) for row in results]

def get_users():
    """Fetch all users for the dropdown."""
    query = "SELECT id, username AS friendly_name FROM users ORDER BY username ASC"
    return query_db(query)

@app.route('/')
def index():
    """Render the home page."""
    users = get_users()
    return render_template('index.html', users=users)

@app.route('/set_user', methods=['POST'])
def set_user():
    """Set a user in the session."""
    user_id = request.form.get('user_id')
    if user_id:
        session['user_id'] = int(user_id)
    return redirect('/')

@app.route('/auth_plex')
def auth_plex():
    """Redirect to Plex.tv OAuth login (placeholder)."""
    # Replace this with actual OAuth implementation
    return redirect('https://plex.tv/auth')

@app.route('/user_stats')
def user_stats():
    """Show stats for the selected user."""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')
    # Fetch stats from the database (placeholder)
    user_stats = [
        {"title": "Breaking Bad", "type": "Show", "watch_count": 42},
        {"title": "Inception", "type": "Movie", "watch_count": 15},
    ]
    return render_template('user_stats.html', stats=user_stats)


@app.route('/movies_2024', methods=['POST'])
def movies_2024():
    """Display movies watched by the selected user in 2024."""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')  # Redirect to home if no user is selected

    query = """
        SELECT 
            sh.rating_key,
            sh.parent_rating_key,
            shm.full_title AS movie_title,
            MIN(datetime(sh.started, 'unixepoch')) AS first_watch_time,
            COUNT(sh.rating_key) AS watch_count,
            SUM((sh.stopped - sh.started) / 60) AS total_minutes_watched
        FROM 
            session_history AS sh
        JOIN 
            session_history_metadata AS shm
        ON 
            sh.rating_key = shm.rating_key
        WHERE 
            sh.user_id = ?
            AND sh.media_type = 'movie'
            AND datetime(sh.started, 'unixepoch') >= '2024-01-01'
        GROUP BY 
            sh.rating_key, shm.full_title
        ORDER BY 
            first_watch_time DESC
        LIMIT 100;
    """
    movies = query_db(query, (user_id,))
    return render_template('movies_2024.html', movies=movies)

@app.route('/stats_overview', methods=['POST'])
def stats_overview():
    """Display overall stats for the selected user."""
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/')  # Redirect to home if no user is selected

    query = """
        SELECT 
            COUNT(*) AS total_sessions,
            COALESCE(SUM((stopped - started) / 60), 0) AS total_minutes_watched,
            COUNT(DISTINCT parent_rating_key) AS unique_titles_watched,
            COUNT(DISTINCT grandparent_rating_key) AS unique_series_watched
        FROM 
            session_history
        WHERE 
            user_id = ?
            AND datetime(started, 'unixepoch') >= datetime('now', '-1 year');
    """
    stats = query_db(query, (user_id,))
    logging.debug(f"Query results for user_id {user_id}: {stats}")
    if not stats or stats[0]['total_minutes_watched'] is None:
        stats = [{
            "total_sessions": 0,
            "total_minutes_watched": 0,
            "unique_titles_watched": 0,
            "unique_series_watched": 0,
        }]
    return render_template('stats_overview.html', stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
