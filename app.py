"""Flask app for managing activities with caching and database integration."""

import os
import json
import logging
import pyodbc
from flask import Flask, request, jsonify, abort, render_template, g
from flask_caching import Cache

# Define the cache directory path
CACHE_DIR = os.path.join(os.getenv('HOME', '.'), 'cache_directory')

def create_cache_dir():
    """Create cache directory if it doesn't exist."""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'filesystem'
app.config['CACHE_DIR'] = CACHE_DIR
app.config['CACHE_DEFAULT_TIMEOUT'] = 1_728_000  # 20 days
app.config['CACHE_THRESHOLD'] = 1000

cache = Cache(app)

API_KEY = os.getenv('API_KEY_UPDATE')

# Set up basic logging
logging.basicConfig(level=logging.INFO)

def get_db():
    """Get database connection from the global context or create a new one."""
    if 'db' not in g:
        connection_string = os.getenv('SQLAZURECONNSTR_SQL_activity')
        try:
            g.db = pyodbc.connect(connection_string)
        except pyodbc.InterfaceError as error:
            logging.error("Database connection failed: %s", error)
            raise error
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    """Close database connection on app context teardown and log exceptions if any."""
    if exception:
        logging.error("An exception occurred: %s", exception)
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/', methods=['GET'])
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/activities', methods=['GET'])
def get_all_activities():
    """Get all activities, using cached data if available."""
    cached_data = cache.get('activities')
    if cached_data:
        return jsonify(cached_data)

    with open('example_activities_response.json', 'r', encoding='utf-8') as file:
        file_data = json.load(file)
    return jsonify(file_data)

@app.route('/api/activities/<int:activity_id>', methods=['GET'])
def get_activity(activity_id):
    """Get a specific activity by ID, using cached data if available."""
    cached_data = cache.get(f'activity_{activity_id}')
    if cached_data:
        return jsonify(cached_data)

    with open('example_activities_response.json', 'r', encoding='utf-8') as file:
        activities = json.load(file)

    for activity in activities:
        if activity['ActivityID'] == activity_id:
            return jsonify(activity)

    return jsonify({"error": "Activity not found"}), 404

@app.route('/db/updatecache', methods=['POST'])
def update_activities_cache():
    """Update activities cache from the database."""
    api_key = request.headers.get('X-API-KEY')
    if api_key != API_KEY:
        abort(401)  # Unauthorized access

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Activities")
    rows = cursor.fetchall()
    activities = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    cache.set('activities', activities)

    for activity in activities:
        cache_key = f'activity_{activity["ActivityID"]}'
        cache.set(cache_key, activity)

    return jsonify({"message": "Cache updated successfully"})

if __name__ == '__main__':
    create_cache_dir()
    app.run(debug=False)
