import sqlite3
import pandas as pd

# Load TSV file
tsv_file_path = "test.tsv"
tsv_file_path = "database_ntoo.tsv"
df = pd.read_csv(tsv_file_path, sep="\t", on_bad_lines='skip')

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

print(f"Data inserted into {db_name}, table '{table_name}' with auto-incrementing ID.")

