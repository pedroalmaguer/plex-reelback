# app.py
from flask import Flask, render_template
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# Configure these
TAUTULLI_URL = "http://localhost:8181"
TAUTULLI_API_KEY = "your_api_key"

def get_tautulli_data(cmd, **params):
    params.update({
        'apikey': TAUTULLI_API_KEY,
        'cmd': cmd
    })
    response = requests.get(f"{TAUTULLI_URL}/api/v2", params=params)
    return response.json()

@app.route('/')
def index():
    # Get watch statistics for last 30 days
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Get watch history
    history = get_tautulli_data('get_history', length=1000, start_date=thirty_days_ago)
    
    # Get user stats
    user_stats = get_tautulli_data('get_user_watch_time_stats', query_days=30)
    
    # Get most watched TV shows
    tv_stats = get_tautulli_data('get_home_stats', stat_id='top_tv')
    
    return render_template('index.html',
                         history=history.get('response', {}).get('data', []),
                         user_stats=user_stats.get('response', {}).get('data', []),
                         tv_stats=tv_stats.get('response', {}).get('data', []))

if __name__ == '__main__':
    app.run(debug=True)
