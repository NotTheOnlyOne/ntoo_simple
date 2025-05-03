import sqlite3
import pandas as pd

# Load TSV file
tsv_file_path = "database_ntoo.tsv"
df = pd.read_csv(tsv_file_path, sep="\t", on_bad_lines='skip')

# Rename columns if necessary (adjust to match actual column names)
# Assumes the file has at least these columns: "title", "text", "url"
# If column names differ, adjust them below
title_col = df.columns[1]
text_col = df.columns[2]

# Apply filtering logic
def filter_rows(df):
    def should_keep(row):
        title = str(row[title_col]).strip()
        text = str(row[text_col]).strip()

        if title in ("Snapshot", "Link", "Link 1", "Link 2"):
            return False
        if title.startswith("http") and text == "":
            return False
        if title.startswith("Post | LinkedIn") and text == "":
            return False
        if any(title.startswith(prefix) for prefix in ("Link (", "Link 1 (", "Link 2 (")):
            return False
        return True

    return df[df.apply(should_keep, axis=1)]

df = filter_rows(df)

# Database setup
db_name = "database_ntoo.db"
table_name = "ntoo_item"

# Connect to SQLite
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Build CREATE TABLE statement with auto-increment ID
columns = df.columns
col_defs = ", ".join([f'"{col}" TEXT' for col in columns])
create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    {col_defs}
);
"""

# Create table
cursor.execute(create_table_sql)

# Insert data
df.to_sql(table_name, conn, if_exists='append', index=False)

# Finalise
conn.commit()
conn.close()

print(f"Filtered data inserted into {db_name}, table '{table_name}' with auto-incrementing ID.")

