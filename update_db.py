import sqlite3
import os

db_path = os.path.join('instance', 'medmining.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def add_column(table, column, type_def):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {type_def}")
        print(f"Added column {column} to {table}")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(f"Column {column} already exists in {table}")
        else:
            print(f"Error adding {column} to {table}: {e}")

# Add missing columns to 'user' table
add_column('user', 'years_experience', 'INTEGER DEFAULT 0')
add_column('user', 'age', 'INTEGER')
add_column('user', 'gender', 'VARCHAR(20)')
add_column('user', 'blood_group', 'VARCHAR(10)')

# Add missing columns to 'medical_record' table
add_column('medical_record', 'is_medicine_report', 'BOOLEAN DEFAULT 0')

conn.commit()
conn.close()
print("Database schema update complete.")
