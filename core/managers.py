"""
Author: Kislay
GitHub: https://github.com/iKislay
LinkedIn: https://www.linkedin.com/in/kislayy/

Core database and progress management utilities for GitEye.
"""

import logging
import os
import pickle
import sqlite3
import sys
import time
from typing import Optional
from selenium.common.exceptions import UnableToSetCookieException
from selenium.webdriver.common.by import By
import csv

logger = logging.getLogger("API-Leakage-Core")

class ProgressManagerError(Exception):
    """Custom exception for ProgressManager class errors"""
    def __init__(self, message: str):
        super().__init__(message)

class ProgressManager:
    """
    Manages and persists progress information for long-running operations.
    """
    def __init__(self, progress_file: str = ".progress.txt"):
        self.progress_file = progress_file

    def save(self, from_iter: int, total: int) -> None:
        with open(self.progress_file, "w", encoding="utf-8") as file:
            file.write(f"{from_iter}/{total}/{time.time()}")

    def load(self, total: int) -> int:
        if not os.path.exists(self.progress_file):
            return 0
        with open(self.progress_file, "r", encoding="utf-8") as file:
            last_, totl_, tmst_ = file.read().strip().split("/")
            last, totl = int(last_), int(totl_)
        if time.time() - float(tmst_) < 3600 and totl == total:
            action = input(f"🔍 Progress found, continue from last progress ({last}/{totl})? [yes] | no: ").lower()
            if action in {"yes", "y", ""}:
                return last
        return 0

class CookieManager:
    """
    Manages browser cookie operations.
    """
    def __init__(self, driver):
        self.driver = driver

    def save(self) -> None:
        cookies = self.driver.get_cookies()
        with open("cookies.pkl", "wb") as file:
            pickle.dump(cookies, file)
            logger.info("🍪 Cookies saved")

    def load(self) -> None:
        try:
            with open("cookies.pkl", "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except UnableToSetCookieException:
                        logger.debug("⚠️ Unable to set a cookie %s", cookie)
        except (EOFError, pickle.UnpicklingError):
            if os.path.exists("cookies.pkl"):
                os.remove("cookies.pkl")
            logger.error("❌ Error loading cookies, invalid cookies removed. Please restart.")

    def verify_user_login(self) -> bool:
        logger.info("🔗 Redirecting ...")
        self.driver.get("https://github.com/")
        if self.driver.find_elements(by=By.XPATH, value="//*[contains(text(), 'Sign in')]"):
            if os.path.exists("cookies.pkl"):
                os.remove("cookies.pkl")
            logger.error("❌ Not logged in. Please restart and try again.")
            sys.exit(1)
        return True

class DatabaseManager:
    """
    Manages the database, including creating tables and handling data interactions.
    """
    def __init__(self, service: str):
        if service.lower() == 'anthropic':
            self.db_filename = 'anthropic_db.db'
        elif service.lower() == 'openai':
            self.db_filename = 'openai_db.db'
        elif service.lower() == 'grok':
            self.db_filename = 'grok_db.db'
        elif service.lower() == 'xai_api':
            self.db_filename = 'xai_api_db.db'
        else:
            raise ValueError(f"Unknown service: {service}")
        self.con: Optional[sqlite3.Connection] = None
        self.cur: Optional[sqlite3.Cursor] = None

    def __enter__(self):
        if not os.path.exists(self.db_filename):
            logger.info(f"Creating database {self.db_filename}")
        self.con = sqlite3.connect(self.db_filename)
        self.cur = self.con.cursor()
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='APIKeys'")
        if self.cur.fetchone() is None:
            logger.info("Creating table APIKeys")
            self.cur.execute("CREATE TABLE APIKeys(apiKey, status, lastChecked)")
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='URLs'")
        if self.cur.fetchone() is None:
            logger.info("Creating table URLs")
            self.cur.execute("CREATE TABLE URLs(url, key)")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.con:
            self.con.close()

    def all_iq_keys(self) -> list:
        if self.cur is None:
            raise RuntimeError("Database cursor is not initialized.")
        self.cur.execute("SELECT * FROM APIKeys WHERE status='rate_limit_error'")
        return self.cur.fetchall()

    def all_keys(self) -> list:
        if self.cur is None:
            raise RuntimeError("Database cursor is not initialized.")
        self.cur.execute("SELECT * FROM APIKeys")
        return self.cur.fetchall()

    def deduplicate(self) -> None:
        if self.cur is None or self.con is None:
            raise RuntimeError("Database connection is not initialized.")
        self.cur.execute("DELETE FROM APIKeys WHERE rowid NOT IN (SELECT MIN(rowid) FROM APIKeys GROUP BY apiKey)")
        self.con.commit()

    def delete(self, api_key: str) -> None:
        if self.cur is None or self.con is None:
            raise RuntimeError("Database connection is not initialized.")
        self.cur.execute("DELETE FROM APIKeys WHERE apiKey=?", (api_key,))
        self.con.commit()

    def insert(self, api_key: str, status: str) -> None:
        if self.cur is None or self.con is None:
            raise RuntimeError("Database connection is not initialized.")
        self.cur.execute("INSERT INTO APIKeys VALUES (?, ?, ?)" , (api_key, status, int(time.time())))
        self.con.commit()

    def key_exists(self, api_key: str) -> bool:
        if self.cur is None:
            raise RuntimeError("Database cursor is not initialized.")
        self.cur.execute("SELECT 1 FROM APIKeys WHERE apiKey=?", (api_key,))
        return self.cur.fetchone() is not None

    def insert_url(self, url: str) -> None:
        if self.cur is None or self.con is None:
            raise RuntimeError("Database connection is not initialized.")
        self.cur.execute("INSERT INTO URLs VALUES (?, ?)" , (url, int(time.time())))
        self.con.commit()

    def get_url(self, url: str) -> Optional[str]:
        if self.cur is None:
            raise RuntimeError("Database cursor is not initialized.")
        self.cur.execute("SELECT url FROM URLs WHERE url=?", (url,))
        row = self.cur.fetchone()
        return row[0] if row else None

    def export_to_csv(self, csv_filename: str = "api_keys_export.csv", service: str = "") -> None:
        """
        Export all API keys to a CSV file in a user-friendly format. Overwrites the file each time.
        Adds a 'service' and 'status_code' column.
        """
        if self.cur is None:
            raise RuntimeError("Database cursor is not initialized.")
        self.cur.execute("SELECT apiKey, status, lastChecked FROM APIKeys")
        rows = self.cur.fetchall()
        # Deduplicate by apiKey (keep latest)
        unique = {}
        for apiKey, status, lastChecked in rows:
            # If status is a tuple (status, status_code), unpack it
            if isinstance(status, str) and status.startswith("("):
                try:
                    status_tuple = eval(status)
                    if isinstance(status_tuple, tuple) and len(status_tuple) == 2:
                        status, status_code = status_tuple
                    else:
                        status_code = ""
                except Exception:
                    status_code = ""
            elif isinstance(status, tuple) and len(status) == 2:
                status, status_code = status
            else:
                status_code = ""
            unique[apiKey] = (status, status_code, lastChecked)
        with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["apiKey", "status", "status_code", "service", "lastChecked"])
            for apiKey, (status, status_code, lastChecked) in unique.items():
                writer.writerow([apiKey, status, status_code, service, lastChecked]) 