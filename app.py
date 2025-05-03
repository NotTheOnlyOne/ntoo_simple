from flask import Flask, render_template, request, redirect
import csv
import random
import requests
from bs4 import BeautifulSoup
import sqlite3

app = Flask(__name__, static_folder='static')


data = []
total_count = 0
choose_number_initial_items = 9
db_name = "database_ntoo.db"
table_name = "ntoo_item"

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

    # Try to convert search_query to integer
    try:
        search_id = int(search_query)
        is_int = True
    except ValueError:
        is_int = False

    if is_int:
        cursor.execute(f"""
            SELECT id, title, key_text, link
            FROM {table_name}
            WHERE id = ? OR LOWER(title) LIKE ? OR LOWER(key_text) LIKE ?
        """, (search_id, f'%{search_query.lower()}%', f'%{search_query.lower()}%'))
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


@app.route('/submit_url', methods=['GET', 'POST'])
def submit_url():
    if request.method == 'POST':
        url_to_submit = request.form['url_to_submit']
        
        # Get the title of the submitted URL
        title = get_url_title(url_to_submit)
        

        # Replace with appropriate entry IDs and form URL
        form_url = "https://docs.google.com/forms/d/e/1FAIpQLScqWMQsFNLQZ3sMQue8cG9zFF5gP-soiJcbPE9WNm0dmiLSHA/viewform"
        entry_ids = {
            "entry.759453538": title,
            "entry.1621102160": url_to_submit
        }

        # Constructing the query parameters for the redirect URL
        query_params = '&'.join([f'{key}={value}' for key, value in entry_ids.items()])
        
        # Constructing the final redirect URL with query parameters
        redirect_url = f'{form_url}?{query_params}'
        return redirect(redirect_url)
        
    
    return render_template('submit_url.html')

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

