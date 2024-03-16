import os
import pyodbc
from flask import Flask, jsonify, render_template, g
import logging

# Initialize Flask app
app = Flask(__name__)

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Helper function to get database connection
def get_db():
    if 'db' not in g:
        # Retrieve the connection string from environment variables
        connection_string = os.getenv('SQLAZURECONNSTR_SQL_activity')
        logging.info(f"Connection String: {connection_string}")  # Log the connection string for debugging
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

# Define route for API to get data
@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM Activities")
        rows = cursor.fetchall()
        data = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
        return jsonify(data)
    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return jsonify({"error": "An error occurred while fetching data"}), 500


# Main entry point
if __name__ == '__main__':
    app.run(debug=True)
