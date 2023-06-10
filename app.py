from flask import Flask, render_template, request
import csv

app = Flask(__name__)
data = []

# Load the data from the TSV file
def load_data():
    global data
    with open('database_ntoo.tsv', 'r', encoding='utf-8') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader)  # Skip the header
        for row in reader:
            title = row[1]
            text = row[2]
            url = row[3]
            data.append((title.lower(), title, text.lower(), text, url))

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
        return render_template('index.html', results=results)
    return render_template('index.html')

if __name__ == '__main__':
    app.run()

