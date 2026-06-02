
# ingest_pipeline.py
# SQLite ingestion pipeline (human-style, readable, testable)

import sqlite3
import pandas as pd
from pathlib import Path
import json

INPUT_CSV = Path("data/enrolments.csv")
DB_PATH = Path("data/courses.db")

def parse_prerequisites(value):
    if pd.isna(value) or value == "":
        return "[]"
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return json.dumps([int(v) for v in parsed])
    except:
        pass
    # fallback comma-separated
    for sep in [",","|",";"]:
        if sep in str(value):
            return json.dumps([int(x.strip()) for x in str(value).split(sep)])
    return json.dumps([int(value)])

def main():
    df = pd.read_csv(INPUT_CSV)
    df.columns = [c.strip().lower().replace(" ","_") for c in df.columns]
    # Trim strings
    for col in df.select_dtypes(include='object'):
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x,str) else x)
    # Parse prerequisites
    if 'prerequisites' in df.columns:
        df['prerequisites'] = df['prerequisites'].map(parse_prerequisites)
    conn = sqlite3.connect(DB_PATH)
    # Create tables if not exist
    conn.execute("CREATE TABLE IF NOT EXISTS courses(course_id INTEGER PRIMARY KEY, name TEXT, description TEXT, prerequisites TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS enrollments(enrollment_id INTEGER PRIMARY KEY, participant_id TEXT, participant_name TEXT, course_id INTEGER, course_date DATE, amount REAL, subsidy REAL, credits_used REAL)")
    # Insert data (replace if exists)
    df_courses = df[['course_id','name','description','prerequisites']].drop_duplicates(subset=['course_id'])
    df_enrollments = df[['enrollment_id','participant_id','participant_name','course_id','course_date','amount','subsidy','credits_used']].drop_duplicates(subset=['enrollment_id'])
    df_courses.to_sql('courses', conn, if_exists='replace', index=False)
    df_enrollments.to_sql('enrollments', conn, if_exists='replace', index=False)
    print(f"Loaded {len(df_courses)} courses and {len(df_enrollments)} enrollments")
    conn.close()

if __name__=="__main__":
    main()
