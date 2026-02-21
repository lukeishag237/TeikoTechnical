import sqlite3
import csv
from pathlib import Path

# init files
csv_file = Path("cell-count.csv")
db_file = Path("cell-count.db")
schema_file = Path("schema.sql") 

# Connect to DB
connection = sqlite3.connect(db_file)
cursor = connection.cursor()

#  Load and execute schema from .sql file
with open(schema_file, "r", encoding="utf-8") as f:
    schema_sql = f.read()
cursor.executescript(schema_sql)

# Read CSV and Insert Data
with open(csv_file, newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print("CSV Columns:", reader.fieldnames)

    for row in reader:

        # project
        cursor.execute("""
            INSERT OR IGNORE INTO Projects (project_name)
            VALUES (?)
        """, (row["project"],))
        cursor.execute("SELECT project_id FROM Projects WHERE project_name = ?", (row["project"],))
        project_id = cursor.fetchone()[0]

        # treatment
        cursor.execute("""
            INSERT OR IGNORE INTO Treatments (treatment_name)
            VALUES (?)
        """, (row["treatment"],))
        cursor.execute("SELECT treatment_id FROM Treatments WHERE treatment_name = ?", (row["treatment"],))
        treatment_id = cursor.fetchone()[0]

        # condition
        cursor.execute("""
            INSERT OR IGNORE INTO Conditions (condition_name)
            VALUES (?)
        """, (row["condition"],))
        cursor.execute("SELECT condition_id FROM Conditions WHERE condition_name = ?", (row["condition"],))
        condition_id = cursor.fetchone()[0]

        # subject
        cursor.execute("""
            INSERT OR IGNORE INTO Subjects (
                project_id, treatment_id, condition_id,
                subject_code, age, sex
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            treatment_id,
            condition_id,
            row["subject"],
            row["age"],
            row["sex"]
        ))

        cursor.execute("SELECT subject_id FROM Subjects WHERE subject_code = ?", (row["subject"],))
        subject_id = cursor.fetchone()[0]

        # sample
        cursor.execute("""
            INSERT OR IGNORE INTO Samples (
                subject_id, sample_code, sample_type, time_from_start, response,
                b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            subject_id,
            row["sample"],
            row["sample_type"],
            row["time_from_treatment_start"],
            row["response"],
            row["b_cell"],
            row["cd8_t_cell"],
            row["cd4_t_cell"],
            row["nk_cell"],
            row["monocyte"]
        ))

# Commit and close
connection.commit()
connection.close()
