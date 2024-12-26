# app.py
from flask import Flask, render_template
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

TAUTULLI_URL = os.getenv('TAUTULLI_URL')
TAUTULLI_API_KEY = os.getenv('TAUTULLI_API_KEY')

def get_tautulli_data(cmd, **params):
    params.update({
        'apikey': TAUTULLI_API_KEY,
        'cmd': cmd
    })
    response = requests.get(f"{TAUTULLI_URL}/api/v2", params=params)
    data = response.json()
    logging.debug(f"API Response for {cmd}: {data}")
    return data

@app.route('/')
def index():
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    history = get_tautulli_data('get_history', length=1000, start_date=thirty_days_ago)
    user_stats = get_tautulli_data('get_user_watch_time_stats', query_days=30)
    tv_stats = get_tautulli_data('get_home_stats', stat_id='top_tv')
    
    # Extract the actual TV stats from the response
    tv_data = tv_stats.get('response', {}).get('data', {}).get('rows', [])
    
    return render_template('index.html',
                         history=history.get('response', {}).get('data', []),
                         user_stats=user_stats.get('response', {}).get('data', []),
                         tv_stats=tv_data)

if __name__ == '__main__':
    app.run(debug=True)
