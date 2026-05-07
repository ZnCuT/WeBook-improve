import sqlite3

conn = sqlite3.connect('instance/webook.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE products ADD COLUMN user_id INTEGER;")
    print("Successfully added user_id column")
except sqlite3.OperationalError as e:
    print(f"user_id column may already exist: {e}")

conn.commit()
conn.close()
print("Database update completed")
