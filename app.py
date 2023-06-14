from flask import Flask, render_template, request
import csv
import random

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

if __name__ == '__main__':
    app.run(port=5000)

