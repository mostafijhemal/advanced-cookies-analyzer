# db_handler.py
import sqlite3
from datetime import datetime

def init_db(db_path="output/cookies.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cookies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            website TEXT,
            name TEXT,
            value TEXT,
            domain TEXT,
            path TEXT,
            expiry INTEGER,
            secure BOOLEAN,
            http_only BOOLEAN,
            scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn

def insert_cookie(conn, website, cookie):
    c = conn.cursor()
    c.execute('''
        INSERT INTO cookies (
            website, name, value, domain, path, expiry, secure, http_only, scan_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        website,
        cookie.get("name"),
        cookie.get("value"),
        cookie.get("domain"),
        cookie.get("path"),
        cookie.get("expiry"),
        cookie.get("secure"),
        cookie.get("httpOnly"),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()

def fetch_all_cookies(db_path="output/cookies.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT website, name, value, domain, path, expiry, secure, http_only, scan_date FROM cookies")
    rows = c.fetchall()
    conn.close()
    return rows

def fetch_all_cookies(db_path="output/cookies.db"):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT website, name, value, domain, path, expiry, secure, http_only, scan_date FROM cookies")
    rows = c.fetchall()
    conn.close()
    return rows

def clear_database(db_path="output/cookies.db"):
    """Function to delete all cookie data from the database"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DELETE FROM cookies")
    conn.commit()
    conn.close()