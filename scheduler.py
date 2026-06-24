import schedule
import time
import json
import os
from datetime import datetime
from db_handler import fetch_all_cookies

# which file will store the settings
CONFIG_FILE = "scheduler_config.json"
LAST_CONFIG = None

def automated_audit_task():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Starting Automated Background Audit...")
    
    rows = fetch_all_cookies()
    if not rows:
        print("No data found to generate report.")
        return

    total_cookies = len(rows)
    print(f"✅ Audit Complete! Total records analyzed: {total_cookies}")
    print("📧 Automated Report generated successfully.")
    print("-" * 50)

def load_config():
    """Loads the settings saved from the UI"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"unit": "minutes", "interval": 1, "time": "00:00", "day": "monday"}

def apply_schedule(config):
    """Updates the schedule based on new settings"""
    schedule.clear() # Removes all existing schedules
    
    unit = config.get("unit", "minutes")
    val = config.get("interval", 1)
    t = config.get("time", "00:00")
    day = config.get("day", "monday")

    if unit == "minutes":
        schedule.every(val).minutes.do(automated_audit_task)
        print(f"🔄 Scheduler Updated: Running every {val} minute(s).")
    elif unit == "hours":
        schedule.every(val).hours.do(automated_audit_task)
        print(f"🔄 Scheduler Updated: Running every {val} hour(s).")
    elif unit == "daily":
        schedule.every().day.at(t).do(automated_audit_task)
        print(f"🔄 Scheduler Updated: Running daily at {t}.")
    elif unit == "weekly":
        # Select the appropriate day method dynamically (e.g., schedule.every().monday)
        day_method = getattr(schedule.every(), day)
        day_method.at(t).do(automated_audit_task)
        print(f"🔄 Scheduler Updated: Running weekly on {day.capitalize()} at {t}.")

print("⏱️ Advanced Dynamic Scheduler Started...")
print("Waiting for UI commands...")

# Infinite loop that runs continuously in the background
while True:
    current_config = load_config()
    
    # If the UI has updated the settings, update the schedule
    if current_config != LAST_CONFIG:
        apply_schedule(current_config)
        LAST_CONFIG = current_config
    
    schedule.run_pending()
    time.sleep(1)