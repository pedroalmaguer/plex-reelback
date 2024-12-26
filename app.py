from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Path to the Tautulli SQLite database
DB_PATH = 'taut.db'


def query_db(query, params=()):
    """Helper function to query the SQLite database."""
    try:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row  # Enables dict-like access
        cursor = connection.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        connection.close()
        return results
    except sqlite3.Error as e:
        logging.error(f"SQLite error: {e}")
        return []


@app.route('/', methods=['GET'])
def index():
    # Get duration from query parameters, default to 30 days
    days = request.args.get('days', '30')
    try:
        days = int(days)
    except ValueError:
        days = 30  # Default to 30 days if invalid input

    # Calculate start date based on the duration
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')

    # Query: Fetch viewing history
    history_query = """
        SELECT * FROM session_history
        WHERE started >= ?
        ORDER BY started DESC
    """
    history = query_db(history_query, (start_date,))

    # Query: Fetch user watch stats
    user_stats_query = """
        SELECT user, COUNT(*) AS total_plays, SUM(duration) AS total_time
        FROM session_history
        WHERE started >= ?
        GROUP BY user
        ORDER BY total_time DESC
    """
    user_stats = query_db(user_stats_query, (start_date,))

    # Query: Fetch top TV shows
    tv_stats_query = """
        SELECT grandparent_title AS title, COUNT(*) AS total_plays, COUNT(DISTINCT user) AS users_watched
        FROM session_history
        WHERE media_type = 'episode' AND started >= ?
        GROUP BY grandparent_title
        ORDER BY total_plays DESC
        LIMIT 10
    """
    tv_stats = query_db(tv_stats_query, (start_date,))

    # Convert data to lists of dictionaries for rendering
    tv_stats = [dict(row) for row in tv_stats]
    user_stats = [dict(row) for row in user_stats]
    history = [dict(row) for row in history]

    # Render the index page
    return render_template(
        'index.html',
        history=history,
        user_stats=user_stats,
        tv_stats=tv_stats,
        selected_days=days
    )


if __name__ == '__main__':
    app.run(debug=True)
