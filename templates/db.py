import sqlite3, time, os, sys, random
from datetime import datetime, timedelta

DB_PATH = r"C:\Users\priya\OneDrive\Desktop\24H\flood_data.db"  # change if needed
TABLE = "sensor_data"
COLUMNS = ["timestamp", "flow_rate", "water_level", "rain_level", "risk"]  # exclude id
TIME_BUDGET_SEC = 3.0
BATCH_SIZE = 2000  # tune 1000–5000

# Ranges you can tweak for your domain
FLOW_MIN, FLOW_MAX = 0.0, 500.0          # m^3/s
WLEVEL_MIN, WLEVEL_MAX = 0.0, 10.0       # meters
RAIN_MIN, RAIN_MAX = 0.0, 200.0          # mm/hr

def make_row(t0, i):
    # Increment timestamp by i seconds; format as ISO 8601 string
    ts = (t0 + timedelta(seconds=i)).strftime("%Y-%m-%d %H:%M:%S")
    flow = round(random.uniform(FLOW_MIN, FLOW_MAX), 2)
    wlev = round(random.uniform(WLEVEL_MIN, WLEVEL_MAX), 2)
    rain = round(random.uniform(RAIN_MIN, RAIN_MAX), 2)
    # Simple risk model: low/medium/high based on combined normalized score
    score = (flow/ FLOW_MAX)*0.4 + (wlev/ WLEVEL_MAX)*0.4 + (rain/ RAIN_MAX)*0.2
    if score < 0.33:
        risk = "low"
    elif score < 0.66:
        risk = "medium"
    else:
        risk = "high"
    return (ts, flow, wlev, rain, risk)

def main():
    if not os.path.exists(DB_PATH):
        print("DB not found:", DB_PATH); sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Speed-focused PRAGMAs (ok for synthetic loads; reduces durability during the run)
    cur.execute("PRAGMA journal_mode=OFF;")
    cur.execute("PRAGMA synchronous=OFF;")
    cur.execute("PRAGMA temp_store=MEMORY;")
    cur.execute("PRAGMA cache_size=100000;")

    placeholders = ",".join(["?"] * len(COLUMNS))
    sql = f"INSERT INTO {TABLE} ({', '.join(COLUMNS)}) VALUES ({placeholders})"

    # Start from current time or latest row’s timestamp if present
    cur.execute(f"SELECT MAX(timestamp) FROM {TABLE}")
    row = cur.fetchone()
    try:
        t0 = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S") if row and row[0] else datetime.now()
    except Exception:
        # If timestamp is stored differently, fall back to now
        t0 = datetime.now()

    start = time.time()
    inserted = 0
    seq = 0

    cur.execute("BEGIN;")
    try:
        while True:
            batch = [make_row(t0, seq + i) for i in range(BATCH_SIZE)]
            cur.executemany(sql, batch)
            inserted += len(batch)
            seq += len(batch)
            if time.time() - start >= TIME_BUDGET_SEC:
                break
        cur.execute("COMMIT;")
    except Exception:
        cur.execute("ROLLBACK;")
        raise
    finally:
        conn.close()

    print(f"Inserted {inserted} rows in {time.time() - start:.2f}s into {TABLE}")

if __name__ == "__main__":
    main()
