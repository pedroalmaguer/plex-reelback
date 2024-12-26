from flask import Flask, render_template, request
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

@app.route('/', methods=['GET'])
def index():
    # Get duration from query parameters, default to 30 days
    days = request.args.get('days', '30')
    try:
        days = int(days)
    except ValueError:
        days = 30  # Default to 30 days if input is invalid

    # Calculate start date based on the selected duration
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')

    # Fetch data from Tautulli based on the selected duration
    history = get_tautulli_data('get_history', length=1000, start_date=start_date)
    user_stats = get_tautulli_data('get_user_watch_time_stats', query_days=days)
    tv_stats = get_tautulli_data('get_home_stats', stat_id='top_tv')

    # Extract the actual TV stats from the response
    tv_data = tv_stats.get('response', {}).get('data', {}).get('rows', [])

    # Render the template with the fetched data
    return render_template(
        'index.html',
        history=history.get('response', {}).get('data', []),
        user_stats=user_stats.get('response', {}).get('data', []),
        tv_stats=tv_data,
        selected_days=days
    )

if __name__ == '__main__':
    app.run(debug=True)