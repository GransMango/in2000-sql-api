import os
import pyodbc
from flask import Flask, request, jsonify, abort, render_template, g
from flask_caching import Cache
import logging

# Initialize Flask app
app = Flask(__name__)

API_KEY = os.getenv('api_key_update')

# Configure cache
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

# Set up basic logging
logging.basicConfig(level=logging.INFO)


# Helper function to get database connection
def get_db():
    if 'db' not in g:
        # Retrieve the connection string from environment variables
        connection_string = os.getenv('SQLAZURECONNSTR_SQL_activity')
        try:
            # Establish a new connection using the connection string
            g.db = pyodbc.connect(connection_string)
        except pyodbc.InterfaceError as e:
            logging.error(f"Database connection failed: {e}")
            raise e
    return g.db


# Helper function to close database connection
@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# Define route for the main page
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/api/activities', methods=['GET'])
def get_all_activities():
    cached_data = cache.get('activities')
    if cached_data:
        return jsonify(cached_data)
    else:
        return jsonify([])  # Return an empty list if cache is empty


@app.route('/api/activities/<int:activity_id>', methods=['GET'])
def get_activity(activity_id):
    cached_data = cache.get(f'activity_{activity_id}')
    if cached_data:
        return jsonify(cached_data)
    else:
        return jsonify({"error": "Activity not found"}), 404


@app.route('/db/updatecache', methods=['POST'])
def update_activities_cache():
    api_key = request.headers.get('X-API-KEY')
    if api_key != API_KEY:
        abort(401)  # Unauthorized access

    # Fetch and update all activities
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Activities")
    rows = cursor.fetchall()
    activities = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    cache.set('activities', activities)  # Cache without expiration

    # Update cache for individual activities
    for activity in activities:
        cache_key = f'activity_{activity["ActivityID"]}'  # Adjust based on your actual ID field
        cache.set(cache_key, activity)  # Cache without expiration

    return jsonify({"message": "Cache updated successfully"})


# Main entry point
if __name__ == '__main__':
    app.run(debug=False)
