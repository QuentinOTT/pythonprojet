"""db.py — Gestion de la base de données SQLite (Partie 1)."""
import sqlite3

DB_PATH = "countries.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                name TEXT PRIMARY KEY,
                region TEXT,
                population INTEGER,
                area REAL
            )
        """)
        conn.commit()

def clear():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM countries")
        conn.commit()

def insert_many(rows):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT OR REPLACE INTO countries (name, region, population, area) VALUES (?, ?, ?, ?)",
            rows
        )
        conn.commit()

def fetch_all():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, region, population, area FROM countries ORDER BY name")
        return cursor.fetchall()

def is_empty():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM countries")
        count = cursor.fetchone()[0]
        return count == 0

def total_population():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(population) FROM countries")
        val = cursor.fetchone()[0]
        return val if val is not None else 0

def avg_population():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT AVG(population) FROM countries")
        val = cursor.fetchone()[0]
        return val if val is not None else 0.0

def population_by_region():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT region, SUM(population) FROM countries GROUP BY region ORDER BY SUM(population) DESC")
        return cursor.fetchall()
