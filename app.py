from flask import Flask, render_template, request, redirect, send_file
import csv
import random
import requests
from bs4 import BeautifulSoup
import sqlite3
import os
app = Flask(__name__, static_folder='static')


data = []
total_count = 0
choose_number_initial_items = 9
db_name = "database_ntoo.db"
table_name = "ntoo_item"

def get_total_count():
    
    # Connect to the database and read rows
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Fetch total rows count to avoid exceeding it during random sampling
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_count = cursor.fetchone()[0]
    return total_count


def choose_random_rows(choose_number_initial_items):

    total_to_fetch = choose_number_initial_items

    # Connect to the database and read rows
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Fetch total rows count to avoid exceeding it during random sampling
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    total_rows = cursor.fetchone()[0]

    if total_rows < total_to_fetch:
        total_to_fetch = total_rows

    # Get all row IDs, sample them randomly
    cursor.execute(f"SELECT id FROM {table_name}")
    all_ids = [row[0] for row in cursor.fetchall()]
    sampled_ids = random.sample(all_ids, total_to_fetch)

    # Fetch sampled rows
    placeholders = ",".join("?" for _ in sampled_ids)
    cursor.execute(f"SELECT id, LOWER(title) AS title_lower, title, LOWER(key_text) AS text_lower,key_text, link FROM {table_name} WHERE id IN ({placeholders})", sampled_ids)
    random_rows = cursor.fetchall()

    conn.close()
    return random_rows

def find_items(search_query):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    search_id = None
    is_id_only = False
    is_int = False

    if search_query.startswith('#'):
        # Search only by ID
        try:
            search_id = int(search_query[1:])
            is_id_only = True
        except ValueError:
            search_id = None  # Invalid ID format
    else:
        try:
            search_id = int(search_query)
            is_int = True
        except ValueError:
            pass  # Not an integer

    if is_id_only and search_id is not None:
        cursor.execute(f"""
            SELECT id, title, key_text, link
            FROM {table_name}
            WHERE id = ?
        """, (search_id,))
    elif is_int:
        cursor.execute(f"""
            SELECT id, title, key_text, link
            FROM {table_name}
            WHERE id = ? OR LOWER(title) LIKE ? OR LOWER(key_text) LIKE ?
            ORDER BY (id = ?) DESC
        """, (search_id, f'%{search_query.lower()}%', f'%{search_query.lower()}%', search_id))
    else:
        cursor.execute(f"""
            SELECT id, title, key_text, link
            FROM {table_name}
            WHERE LOWER(title) LIKE ? OR LOWER(key_text) LIKE ?
        """, (f'%{search_query.lower()}%', f'%{search_query.lower()}%'))

    results = cursor.fetchall()
    conn.close()
    return results


@app.route('/', methods=['GET', 'POST'])
def index():
    total_count = get_total_count()
    if request.method == 'POST':
        search_query = request.form['search_query'].lower()
        results = find_items(search_query) 
        return render_template('index.html', results=results,total_count=total_count,search_query=search_query)
    else:
        if 'search_query' in request.args:
            search_query = request.args['search_query'].lower()
            results = find_items(search_query) 
            return render_template('index.html', results=results,total_count=total_count,search_query=search_query)
        else:

            random_rows = choose_random_rows(choose_number_initial_items)
            results = []
            for random_row in random_rows:
                id, title_lower, title, text_lower, text, url = random_row
                results.append((id, title, text, url))

            return render_template('index.html',results=results,total_count=total_count)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        title = request.form['title']
        link = request.form['link']
        key_text = request.form['key_text']
        
        # Insert into the SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO {table_name} (title, key_text, link)
            VALUES (?, ?, ?)
        """, (title, key_text, link))
        conn.commit()
        conn.close()

        return redirect('/')
    
    # Handle GET: use query parameters to pre-fill
    preset_title = request.args.get('title', '')
    preset_link = request.args.get('link', '')
    return render_template('add_item.html', preset_title=preset_title, preset_link=preset_link)


@app.route("/download_database")
def serve_database_file():
    db_path = os.path.join(app.root_path, "database_ntoo.db")
    return send_file(db_path, as_attachment=True)


def get_url_title(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string
        return title
    except Exception as e:
        print(f"Error fetching URL title: {e}")
        return "Title Not Found"

if __name__ == '__main__':
    app.run(port=5001)
    
