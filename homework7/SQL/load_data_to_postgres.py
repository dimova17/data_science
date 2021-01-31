import psycopg2
import csv

conn = psycopg2.connect(host='localhost', port='5432', dbname='odscourse', user='postgres', password='secret')
cursor = conn.cursor()

query = """
CREATE TABLE IF NOT EXISTS heart_disease (
    id INTEGER PRIMARY KEY,
    age INTEGER,
    gender INTEGER,
    height REAL,
    weight REAL,
    ap_hi INTEGER,
    ap_lo INTEGER,
    cholesterol INTEGER,
    gluc INTEGER,
    smoke INTEGER,
    alco INTEGER,
    active INTEGER,
    cardio INTEGER
)
"""
cursor.execute(query)
conn.commit()

with open('mlbootcamp5_train.csv', 'r') as f:
    reader = csv.reader(f, delimiter=';')
    # Skip the header row
    next(reader)
    for row in reader:
        cursor.execute(
            "INSERT INTO heart_disease VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            row
        )
conn.commit()

