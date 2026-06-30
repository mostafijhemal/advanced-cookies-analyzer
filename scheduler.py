import schedule
import time
import json
import os
from datetime import datetime
from db_handler import init_db, insert_cookie
from cookie_collector import get_cookies_from_site

# যে ফাইলে সেটিংস সেভ থাকবে
CONFIG_FILE = "scheduler_config.json"
LAST_CONFIG = None

def automated_audit_task():
    global LAST_CONFIG
    config = load_config()
    urls = config.get("target_urls", [])
    
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 Starting Automated Background Audit...")
    
    if not urls:
        print("⚠️ No target URLs configured for auto-scanning. Please add URLs in the UI.")
        return

    conn = init_db("output/cookies.db")
    total_cookies = 0
    
    for url in urls:
        print(f"🔍 Scanning {url}...")
        try:
            cookies = get_cookies_from_site(url)
            for cookie in cookies:
                insert_cookie(conn, url, cookie)
            total_cookies += len(cookies)
            print(f"✅ Extracted {len(cookies)} cookies from {url}")
        except Exception as e:
            print(f"❌ Error scanning {url}: {e}")
            
    # Update run count and last run time
    config["run_count"] = config.get("run_count", 0) + 1
    config["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        LAST_CONFIG = config # Prevent scheduler from restarting due to file change
    except Exception as e:
        print(f"Failed to update config file: {e}")

    print(f"✅ Audit Complete! Total records added to DB: {total_cookies}")
    print("-" * 50)

def load_config():
    """UI থেকে সেভ করা সেটিংস লোড করবে"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"unit": "minutes", "interval": 1, "time": "00:00", "day": "monday", "target_urls": [], "run_count": 0, "last_run": "Never"}

def apply_schedule(config):
    """নতুন সেটিংস অনুযায়ী শিডিউল আপডেট করবে"""
    schedule.clear() # আগের সব শিডিউল মুছে ফেলবে
    
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
        # getattr ব্যবহার করে ডাইনামিক দিন সিলেক্ট করা হচ্ছে (যেমন: schedule.every().monday)
        day_method = getattr(schedule.every(), day)
        day_method.at(t).do(automated_audit_task)
        print(f"🔄 Scheduler Updated: Running weekly on {day.capitalize()} at {t}.")

print("⏱️ Advanced Dynamic Scheduler Started...")
print("Waiting for UI commands...")

# ইনফিনিট লুপ যা সবসময় ব্যাকগ্রাউন্ডে চলবে
while True:
    current_config = load_config()
    
    # যদি UI থেকে সেটিংস পরিবর্তন করা হয়, তবেই শিডিউল আপডেট হবে
    if current_config != LAST_CONFIG:
        apply_schedule(current_config)
        LAST_CONFIG = current_config
    
    schedule.run_pending()
    time.sleep(1)