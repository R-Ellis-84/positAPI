from flask import Flask, jsonify
import sqlite3

app = Flask(__name__)

#DATABASE = '/Users/lindseybaucum/nav_data.db'
DATABASE = 'nav_data.db'

def query_db(query, args=(), one=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # enables dict-like access
    cur = conn.cursor()
    cur.execute(query, args)
    rows = cur.fetchall()
    conn.close()
    return (dict(row) for row in rows) if not one else dict(rows[0]) if rows else None

@app.route('/')
def index():
    return "API is running.  Try /nav."


@app.route('/nav', methods=['GET'])
def get_nav():
    query = """
        SELECT * FROM nav
        ORDER BY timestamp DESC
    """
    results = list(query_db(query))
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5150)
