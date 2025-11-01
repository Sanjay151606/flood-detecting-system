from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
from pathlib import Path
from twilio.rest import Client
import sqlite3
import threading

app = Flask(__name__)

# -------------------- Storage --------------------
DB_PATH = Path(__file__).with_name("flood_data.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
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

def insert_row(ts, flow, level, rain, risk):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO sensor_data (timestamp, flow_rate, water_level, rain_level, risk) VALUES (?, ?, ?, ?, ?)",
        (ts, flow, level, rain, risk)
    )
    conn.commit()
    conn.close()

def fetch_rows(limit=200):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT timestamp, flow_rate, water_level, rain_level, risk "
        "FROM sensor_data ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    # reverse to show oldest first for the time-series chart
    return list(reversed(rows))

# Initialize database at startup
init_db()

# -------------------- Twilio (hardcoded as requested) --------------------
ACCOUNT_SID  = "ACd0d8bc14aea854e2e677990ab1a100d0"
AUTH_TOKEN   = "ecccd7f5de919d6d97d18d1c7aef95bf"
TWILIO_PHONE = "+14789795491"
ALERT_PHONE  = "+919344557376"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Optional: cooldown to avoid SMS storms (one HIGH alert per 10 minutes)
_last_alert_lock = threading.Lock()
_last_alert_time = None
ALERT_COOLDOWN = timedelta(minutes=10)

def can_send_alert_now():
    global _last_alert_time
    with _last_alert_lock:
        now = datetime.utcnow()
        if _last_alert_time is None or (now - _last_alert_time) >= ALERT_COOLDOWN:
            _last_alert_time = now
            return True
        return False

# -------------------- Helpers --------------------
def to_float(x, default=None):
    try:
        return float(x)
    except Exception:
        return default

# -------------------- Routes --------------------
@app.route("/")
def dashboard():
    rows = fetch_rows(200)
    return render_template("dashboard.html", data=rows)

@app.route("/feed")
def feed():
    # Send recent rows and add anti-cache headers
    resp = jsonify(fetch_rows(200))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    return resp

@app.route("/update", methods=["POST"])
def update_data():
    """
    Accepts either JSON:
      {"river_distance": <cm>, "flow_rate": <L/min>, "rain_level": <0-100>, "water_level": <0-100>}
    or form-encoded with the same keys.
    """
    try:
        payload = request.get_json(silent=True)

        # Fallback to form data if JSON missing
        if not payload and request.form:
            payload = {
                "river_distance": request.form.get("river_distance"),
                "flow_rate": request.form.get("flow_rate"),
                "rain_level": request.form.get("rain_level"),
                "water_level": request.form.get("water_level"),
            }

        if not payload:
            ct = request.headers.get("Content-Type", "")
            raw = request.data.decode(errors="ignore")
            return jsonify({"error": "No/invalid body", "ct": ct, "raw": raw}), 400

        distance = to_float(payload.get("river_distance"), -1)
        flow     = to_float(payload.get("flow_rate"), 0)
        rain     = to_float(payload.get("rain_level"), 0)
        level    = to_float(payload.get("water_level"), 0)

        if any(v is None for v in [distance, flow, rain, level]):
            return jsonify({"error": "Non-numeric value", "payload": payload}), 400

        # Clamp invalid values
        if distance is None or distance < 0:
            distance = 0

        # Risk calculation
        if level > 80 or rain > 70:
            risk = "HIGH"
        elif level > 50 or rain > 40:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_row(timestamp, flow, level, rain, risk)

        # SMS alert for HIGH risk (with cooldown)
        if risk == "HIGH" and can_send_alert_now():
            try:
                client.messages.create(
                    body=f"⚠️ FLOOD ALERT! High risk detected!\nFlow: {flow}, Level: {level}, Rain: {rain}",
                    from_=TWILIO_PHONE,
                    to=ALERT_PHONE
                )
            except Exception as err:
                app.logger.warning(f"Twilio send failed: {err}")

        return jsonify({"status": "success", "risk": risk}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- Main --------------------
if __name__ == "__main__":
    # Expose on LAN so IoT devices can POST /update
    app.run(host="0.0.0.0", port=5000, debug=True)
