from flask import Flask, render_template, request, redirect
import csv
import random
import requests
from bs4 import BeautifulSoup

app = Flask(__name__, static_folder='static')


data = []
total_count = 0
choose_number_initial_items = 9

# Load the data from the TSV file
def load_data():
    no_title = 0
    snapshot = 0
    global data
    global total_count
    with open('database_ntoo.tsv', 'r', encoding='utf-8') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader)  # Skip the header
        for row in reader:
            skip_data = False
            title = row[1]
            text = row[2]
            url = row[3]

            if title == "" and text =="":
                no_title = no_title + 1
                skip_data = True
            if title == "Snapshot":
                snapshot = snapshot + 1

            if not skip_data:
                data.append((title.lower(), title, text.lower(), text, url))

    total_count = len(data)

def choose_random_rows(data,choose_number_initial_items):
    extra_random_rows_to_filter = 10
    extra_random_rows = random.sample(data, choose_number_initial_items*extra_random_rows_to_filter)

    random_rows  = []
    for row in extra_random_rows:
        title_lower, title, text_lower, text, url = row
        if title == "Snapshot" or title == "Link":
            continue
        else:
            random_rows.append(row)

        if len(random_rows) == choose_number_initial_items:
            break

    return random_rows


load_data()  # Call load_data() to initialize the data at the start

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search_query'].lower()
        results = []
        for row in data:
            title_lower, title, text_lower, text, url = row
            if search_query in title_lower or search_query in text_lower:
                results.append((title, text, url))
        return render_template('index.html', results=results,total_count=total_count,search_query=search_query)
    else:
        if 'search_query' in request.args:
            search_query = request.args['search_query'].lower()
            results = []
            for row in data:
                title_lower, title, text_lower, text, url = row
                if search_query in title_lower or search_query in text_lower:
                    results.append((title, text, url))
            return render_template('index.html', results=results,total_count=total_count,search_query=search_query)
        else:

            random_rows = choose_random_rows(data,choose_number_initial_items)
            results = []
            for random_row in random_rows:
                title_lower, title, text_lower, text, url = random_row
                results.append((title, text, url))
            return render_template('index.html',results=results,total_count=total_count)


@app.route('/submit_url', methods=['GET', 'POST'])
def submit_url():
    if request.method == 'POST':
        url_to_submit = request.form['url_to_submit']
        
        # Get the title of the submitted URL
        title = get_url_title(url_to_submit)
        
        print(title)


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
        print(redirect_url) 
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

