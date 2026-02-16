import sqlite3
import os

# Support persistent storage for deployment
if os.path.exists("/opt/render/project/src/data"):
    DB_PATH = "/opt/render/project/src/data/metadata.db"
else:
    DB_PATH = "metadata.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT UNIQUE,
    file_hash TEXT,
    version INTEGER DEFAULT 1
)
""")

cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_filename ON documents(filename)
""")

conn.commit()
