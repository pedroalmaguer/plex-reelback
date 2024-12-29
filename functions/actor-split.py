import sqlite3

# Define the custom string-splitting function
def split_string(data, delimiter=";"):
    if data is None:
        return []
    return data.split(delimiter)

# Connect to the SQLite database
conn = sqlite3.connect("taut.db")

# Register the custom function with SQLite
conn.create_function("split_string", 2, split_string)
