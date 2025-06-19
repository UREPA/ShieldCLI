# viewer.py
import sqlite3

def afficher_donnees(db_path="reports.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for table in cursor.execute("SELECT name FROM sqlite_master WHERE type='table';"):
        print(f"\n--- Table: {table[0]} ---")
        for row in cursor.execute(f"SELECT * FROM {table[0]}"):
            print(row)

    conn.close()

if __name__ == "__main__":
    afficher_donnees()
