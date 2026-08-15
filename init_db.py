import sqlite3

def init_db():
    conn = sqlite3.connect("flood_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            flow_rate REAL NOT NULL,
            water_level REAL NOT NULL,
            rain_level REAL NOT NULL,
            risk TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Initialized flood_data.db successfully.")

if __name__ == "__main__":
    init_db()
