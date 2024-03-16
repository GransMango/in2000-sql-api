import os
import pyodbc
from flask import Flask, jsonify

connection_string = os.getenv('SQL_activity')

# Establish a new connection using the connection string
connection = pyodbc.connect(connection_string)

# Create a new cursor
cursor = connection.cursor()

app = Flask(__name__)

@app.route('/api/data', methods=['GET'])
def get_data():
    cursor.execute("SELECT * FROM Activities")  # replace 'your_table' with your actual table name
    rows = cursor.fetchall()
    data = [dict(zip([column[0] for column in cursor.description], row)) for row in rows]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)