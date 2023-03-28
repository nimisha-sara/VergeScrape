import sqlite3
import csv


class DataBase:
    def __init__(self):
        self.conn = sqlite3.connect('VergeScrape.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Verge_News (
                ID INTEGER PRIMARY KEY,
                URL TEXT,
                HEADLINE TEXT,
                AUTHOR TEXT,
                DATE TEXT
            )
        """)
        self.conn.commit()

    def insert_article_from_csv(self, csv_file):
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.cursor.execute("""
                    SELECT * FROM Verge_News
                    WHERE url = ?
                """, (row['url'],))
                existing_article = self.cursor.fetchone()

                if not existing_article:
                    self.cursor.execute("""
                        INSERT INTO Verge_News (url, headline, author, date)
                        VALUES (?, ?, ?, ?)
                    """, (row['url'], row['headline'], row['author'], row['date']))
                    self.conn.commit()
