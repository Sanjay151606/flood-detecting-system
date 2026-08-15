# 🌊 IoT Flood Early Warning & Emergency Alert Dispatch System

> Hydrological telemetry monitoring station analyzing water levels, rainfall, and flow rate in real time to trigger automated Twilio SMS emergency alerts.

[![Python](https://img.shields.io/badge/Language-Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Backend](https://img.shields.io/badge/Framework-Flask-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Twilio](https://img.shields.io/badge/Alerts-Twilio_SMS_API-F22F46?style=flat-square&logo=twilio&logoColor=white)](https://twilio.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)

---

## 📌 Overview & Problem Statement
Communities in flood-prone river basins frequently suffer severe property damage and casualties due to delayed disaster notices. Centralized warning systems often fail to reach residents immediately via universal mobile channels.

This system ingests live environmental sensor telemetry (flow rate, water level, precipitation) and calculates a real-time risk index (`SAFE`, `MODERATE`, `CRITICAL`). Upon hazard threshold breach, it automatically dispatches emergency SMS alerts via Twilio.

---

## ✨ Key Features
- **Real-Time Telemetry Ingestion:** Ingests sensor payloads representing water level, precipitation, and flow velocity.
- **Multi-Factor Risk Engine:** Algorithmic evaluation classifying risk levels and detecting rapid water surges.
- **Automated Emergency SMS Dispatch:** Broadcasts automated SMS alerts to registered citizens and municipal authorities when risk hits `HIGH` or `CRITICAL`.
- **Live Telemetry Console:** Web dashboard displaying current sensor metrics and historical risk trends.
- **Resident Subscription Portal:** Form allowing citizens to register mobile numbers for automated alerts.

---

## 🏗️ System Architecture

```
[ IoT Sensor Network / Telemetry Stream ]
                   │
                   ▼ (HTTP POST / Sensor Readings)
     [ Flask API Backend (app.py) ]
     ├── Ingestion & Data Validation
     ├── Multi-Factor Risk Classifier Engine
     └── Telemetry Logger
         │                      │
         ▼                      ▼
 [ SQLite Database ]    [ Twilio REST API Client ]
 (Historical Readings)          │ (Automated SMS)
                                ▼
                       [ Citizen Mobile Devices 📱 ]
```

---

## 🛠️ Tech Stack
- **Backend:** Python 3.10+, Flask
- **Database:** SQLite 3
- **External Services:** Twilio REST Python SDK (`twilio`)
- **Frontend:** HTML5, CSS3, Jinja2 Templates

---

## 🚀 Getting Started Locally

### 1. Prerequisites
- Python 3.9+
- Twilio Account (Account SID, Auth Token, Twilio Phone Number)

### 2. Clone & Setup
```bash
git clone https://github.com/Sanjay151606/flood-early-warning-system.git
cd flood-early-warning-system

# Create virtual environment
python -m venv venv
# Activate on Windows:
venv\Scriptsctivate
# Activate on Linux/macOS:
source venv/bin/activate

pip install flask twilio python-dotenv
```

### 3. Initialize Database
```bash
python init_db.py
```

### 4. Environment Variables
Create a `.env` file in the root directory (see `.env.example`):
```env
FLASK_APP=app.py
FLASK_ENV=development
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
ADMIN_ALERT_PHONE=your_destination_phone_number
```

### 5. Run Application
```bash
python app.py
```
Visit `http://localhost:5000` in your browser.

---

## 👤 Author
**Sanjay**  
- LinkedIn: [linkedin.com/in/sanjayselvamani/](https://www.linkedin.com/in/sanjayselvamani/)  
- Portfolio: [sanjay151606.github.io/new-portfolio/](https://sanjay151606.github.io/new-portfolio/)  
- Email: [ssanjay41571@gmail.com](mailto:ssanjay41571@gmail.com)
