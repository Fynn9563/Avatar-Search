from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
import sqlite3
import json
import os
import csv
from io import StringIO

app = Flask(__name__, template_folder='templates')
DATABASE_FILE = 'avatars.db'

class AvatarDatabase:
    def get_connection(self):
        return sqlite3.connect(DATABASE_FILE)

    def create_table(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''DROP TABLE IF EXISTS Avatars''')
            cursor.execute('''CREATE TABLE Avatars
                               (id TEXT PRIMARY KEY,
                                name TEXT,
                                author TEXT,
                                image_url TEXT)''')
            conn.commit()

    def search_avatars(self, search_term, limit=5000):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if search_term:
                query = "SELECT * FROM Avatars WHERE name LIKE ? OR id = ? LIMIT ?"
                cursor.execute(query, (f'%{search_term}%', search_term, limit))
            else:
                query = "SELECT * FROM Avatars LIMIT ?"
                cursor.execute(query, (limit,))
            return cursor.fetchall()

    def import_avatar(self, avatar_data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if isinstance(avatar_data, dict):
                avatar_id = avatar_data.get('id')
                avatar_name = avatar_data.get('name')
                avatar_author = avatar_data.get('authorName')
                avatar_image_url = avatar_data.get('imageUrl')

                if avatar_id:
                    query = "SELECT id FROM Avatars WHERE id = ?"
                    cursor.execute(query, (avatar_id,))
                    existing_avatar = cursor.fetchone()

                    if existing_avatar:
                        query = "UPDATE Avatars SET name = ?, author = ?, image_url = ? WHERE id = ?"
                        cursor.execute(query, (avatar_name, avatar_author, avatar_image_url, avatar_id))
                    else:
                        query = "INSERT INTO Avatars (id, name, author, image_url) VALUES (?, ?, ?, ?)"
                        cursor.execute(query, (avatar_id, avatar_name, avatar_author, avatar_image_url))
            conn.commit()

    def delete_avatar(self, avatar_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "DELETE FROM Avatars WHERE id = ?"
            cursor.execute(query, (avatar_id,))
            conn.commit()
            

db = AvatarDatabase()

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files = request.files.getlist('file')  # Changed to getlist to handle multiple files
        if not files:
            return redirect(url_for('home', message='No files provided'))

        for file in files:
            if file and file.filename != '':
                try:
                    avatar_data = json.load(file)
                    if isinstance(avatar_data, list):
                        for avatar in avatar_data:
                            db.import_avatar(avatar)
                    else:
                        db.import_avatar(avatar_data)
                except json.JSONDecodeError as e:
                    return redirect(url_for('home', message=f'Invalid JSON in file {file.filename}: {str(e)}'))
                except Exception as e:
                    return redirect(url_for('home', message=f'Error processing file {file.filename}: {str(e)}'))
        
        return redirect(url_for('home', message='Upload successful'))

    return render_template('upload.html')

@app.route('/json', methods=['GET'])
def json_output():
    search_term = request.args.get('search')
    n = request.args.get('n', type=int, default=5000)

    results = db.search_avatars(search_term, limit=n)

    avatars = [{'id': row[0], 'name': row[1], 'author': row[2]} for row in results]

    return jsonify(avatars)

@app.route('/export', methods=['GET'])
def export_data():
    results = db.search_avatars(None)
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Name', 'Author', 'Image URL'])
    for row in results:
        cw.writerow(row)
    output = si.getvalue()
    si.close()
    return Response(output, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=avatars.csv"})

@app.route('/delete/<avatar_id>', methods=['POST'])
def delete_avatar_route(avatar_id):
    db.delete_avatar(avatar_id)
    return redirect(url_for('home'))

@app.route('/', methods=['GET', 'POST'])
def home():
    message = request.args.get('message')  # Retrieve the message from query parameters
    if request.method == 'POST':
        search_term = request.form['search']
        results = db.search_avatars(search_term)
        if not results:
            message = message or "No avatars found matching the search criteria."
        return render_template('index.html', results=results, message=message)
    else:
        return render_template('index.html', message=message)

if __name__ == '__main__':
    if not os.path.exists(DATABASE_FILE):
        db.create_table()
    app.run()
