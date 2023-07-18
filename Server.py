from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
import json
import tempfile

app = Flask(__name__, template_folder='templates')
DATABASE_FILE = 'avatars.db'

# Function to create the Avatars table if it doesn't exist
def create_table():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''DROP TABLE IF EXISTS Avatars''')
    cursor.execute('''CREATE TABLE Avatars
                      (id TEXT PRIMARY KEY,
                       name TEXT,
                       author TEXT)''')
    conn.commit()
    conn.close()

# Function to search avatars by name or ID
def search_avatars(search_term, limit=5000):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    if search_term:
        query = "SELECT * FROM Avatars WHERE name LIKE ? OR id = ? LIMIT ?"
        cursor.execute(query, (f'%{search_term}%', search_term, limit))
    else:
        query = "SELECT * FROM Avatars LIMIT ?"
        cursor.execute(query, (limit,))

    results = cursor.fetchall()
    conn.close()
    return results
    
# Function to import avatars from a JSON file
def import_avatars_from_json(avatar_data):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    if isinstance(avatar_data, dict):
        avatar_id = avatar_data.get('id')
        avatar_name = avatar_data.get('name')
        avatar_author = avatar_data.get('authorName')
        avatar_image_url = avatar_data.get('imageUrl')

        if avatar_id:
            # Check if avatar with the same ID already exists
            query = "SELECT id FROM Avatars WHERE id = ?"
            cursor.execute(query, (avatar_id,))
            existing_avatar = cursor.fetchone()

            if existing_avatar:
                # Overwrite the existing avatar record
                query = "UPDATE Avatars SET name = ?, author = ?, image_url = ? WHERE id = ?"
                cursor.execute(query, (avatar_name, avatar_author, avatar_image_url, avatar_id))
            else:
                # Insert the new avatar record
                query = "INSERT INTO Avatars (id, name, author, image_url) VALUES (?, ?, ?, ?)"
                cursor.execute(query, (avatar_id, avatar_name, avatar_author, avatar_image_url))

    conn.commit()
    conn.close()


# Route for file upload
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            avatar_data = json.load(file)
            import_avatars_from_json(avatar_data)
            return redirect(url_for('home'))
    return render_template('upload.html')

@app.route('/json', methods=['GET'])
def json_output():
    search_term = request.args.get('search')
    n = request.args.get('n', type=int, default=5000)

    results = search_avatars(search_term, limit=n)

    avatars = []
    for row in results:
        avatar = {
            'id': row[0],
            'name': row[1],
            'author': row[2]
        }
        avatars.append(avatar)

    return jsonify(avatars)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        search_term = request.form['search']
        results = search_avatars(search_term)
        if len(results) == 0:
            message = "No avatars found matching the search criteria."
        else:
            message = None
        return render_template('index.html', results=results, message=message)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists(DATABASE_FILE):
        create_table()

    app.run()
