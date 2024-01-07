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
    global data
    global total_count
    with open('database_ntoo.tsv', 'r', encoding='utf-8') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader)  # Skip the header
        for row in reader:
            title = row[1]
            text = row[2]
            url = row[3]
            data.append((title.lower(), title, text.lower(), text, url))

    total_count = len(data)


def choose_random_rows(data,choose_number_initial_items):
    random_rows = random.sample(data, choose_number_initial_items)
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
        form_url = "https://docs.google.com/forms/d/e/1FAIpQLScqWMQsFNLQZ3sMQue8cG9zFF5gP-soiJcbPE9WNm0dmiLSHA/formResponse"
        entry_ids = {
            "entry.123456789": title,
            "entry.987654321": url_to_submit,
            "entry.246813579": "..."
        }
        
        submit_form(form_url, entry_ids)
        return render_template('submit_url.html')
    
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

def submit_form(form_url, data):
    # Submitting the form using requests
    try:
        response = requests.post(form_url, data=data)
        # You can handle the response here
        print("Form submitted successfully")
    except requests.RequestException as e:
        print("Error submitting form:", e)


if __name__ == '__main__':
    app.run(port=5001)

