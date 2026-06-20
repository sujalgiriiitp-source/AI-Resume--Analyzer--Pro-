"""
database/db.py — SQLite CRUD Module for AI Resume Analyzer Pro
===============================================================
Provides all database operations: initialisation, student management,
and analysis-history persistence.  Every public function uses context
managers for safe connection handling and returns plain Python objects
(dicts / lists) so callers never need to touch sqlite3 directly.
"""

import json
import os
import sqlite3
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def get_db_path() -> str:
    """Return the absolute path to the SQLite database file."""
    db_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(db_dir, "resume_analyzer.db")


def _get_schema_path() -> str:
    """Return the absolute path to the SQL schema file."""
    db_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(db_dir, "schema.sql")


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def init_db() -> None:
    """
    Read *schema.sql* and execute it against the database, creating tables
    if they do not already exist.  Safe to call multiple times.
    """
    schema_path = _get_schema_path()
    db_path = get_db_path()

    try:
        with open(schema_path, "r", encoding="utf-8") as fh:
            schema_sql = fh.read()

        with sqlite3.connect(db_path) as conn:
            conn.executescript(schema_sql)
            conn.commit()
    except FileNotFoundError:
        print(f"[db] Schema file not found: {schema_path}")
    except sqlite3.Error as exc:
        print(f"[db] Error initialising database: {exc}")


# ---------------------------------------------------------------------------
# Student CRUD
# ---------------------------------------------------------------------------

def add_student(
    name: str,
    email: str,
    resume_text: str = "",
    ats_score: float = 0.0,
    skills: Optional[List[str]] = None,
) -> Optional[int]:
    """
    Insert a new student or **update** the existing record when *email*
    already exists.  *skills* is stored as a JSON-encoded string.

    Returns the ``student_id`` on success, or ``None`` on failure.
    """
    skills_json = json.dumps(skills or [])
    db_path = get_db_path()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check whether the student already exists
            cursor.execute("SELECT id FROM students WHERE email = ?", (email,))
            row = cursor.fetchone()

            if row:
                # Update existing record
                cursor.execute(
                    """
                    UPDATE students
                       SET name        = ?,
                           resume_text = ?,
                           ats_score   = ?,
                           skills      = ?,
                           updated_at  = CURRENT_TIMESTAMP
                     WHERE email = ?
                    """,
                    (name, resume_text, ats_score, skills_json, email),
                )
                conn.commit()
                return row[0]
            else:
                # Insert new record
                cursor.execute(
                    """
                    INSERT INTO students (name, email, resume_text, ats_score, skills)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (name, email, resume_text, ats_score, skills_json),
                )
                conn.commit()
                return cursor.lastrowid

    except sqlite3.Error as exc:
        print(f"[db] Error adding/updating student: {exc}")
        return None


def get_all_students() -> List[Dict[str, Any]]:
    """Return every student record as a list of dicts."""
    db_path = get_db_path()

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        print(f"[db] Error fetching students: {exc}")
        return []


def get_student_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Return a single student dict looked up by *email*, or ``None``."""
    db_path = get_db_path()

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students WHERE email = ?", (email,))
            row = cursor.fetchone()
            return dict(row) if row else None
    except sqlite3.Error as exc:
        print(f"[db] Error fetching student by email: {exc}")
        return None


def delete_student(student_id: int) -> bool:
    """Delete a student (and cascaded analysis rows) by *student_id*."""
    db_path = get_db_path()

    try:
        with sqlite3.connect(db_path) as conn:
            # Enable FK enforcement so CASCADE works
            conn.execute("PRAGMA foreign_keys = ON")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as exc:
        print(f"[db] Error deleting student: {exc}")
        return False


# ---------------------------------------------------------------------------
# Analysis history
# ---------------------------------------------------------------------------

def add_analysis(
    student_id: int,
    ats_score: float = 0.0,
    skills_found: Optional[List[str]] = None,
    missing_skills: Optional[List[str]] = None,
    recommendations: Optional[List[str]] = None,
    internship_matches: Optional[List[Any]] = None,
) -> Optional[int]:
    """
    Persist one analysis run.  All list arguments are JSON-serialised
    before storage.  Returns the new ``analysis_id`` or ``None``.
    """
    db_path = get_db_path()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO analysis_history
                    (student_id, ats_score, skills_found,
                     missing_skills, recommendations, internship_matches)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    student_id,
                    ats_score,
                    json.dumps(skills_found or []),
                    json.dumps(missing_skills or []),
                    json.dumps(recommendations or []),
                    json.dumps(internship_matches or []),
                ),
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error as exc:
        print(f"[db] Error adding analysis: {exc}")
        return None


def get_analysis_history(
    student_id: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Return analysis records.  If *student_id* is provided, filter to that
    student; otherwise return **all** records (newest first).
    """
    db_path = get_db_path()

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if student_id is not None:
                cursor.execute(
                    """
                    SELECT * FROM analysis_history
                     WHERE student_id = ?
                     ORDER BY analyzed_at DESC
                    """,
                    (student_id,),
                )
            else:
                cursor.execute(
                    "SELECT * FROM analysis_history ORDER BY analyzed_at DESC"
                )

            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        print(f"[db] Error fetching analysis history: {exc}")
        return []


# ---------------------------------------------------------------------------
# Aggregate helpers
# ---------------------------------------------------------------------------

def get_student_count() -> int:
    """Return the total number of registered students."""
    db_path = get_db_path()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM students")
            result = cursor.fetchone()
            return result[0] if result else 0
    except sqlite3.Error as exc:
        print(f"[db] Error counting students: {exc}")
        return 0


def get_average_ats_score() -> float:
    """Return the average ATS score across all students (0.0 if none)."""
    db_path = get_db_path()

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT AVG(ats_score) FROM students")
            result = cursor.fetchone()
            return round(result[0], 2) if result and result[0] is not None else 0.0
    except sqlite3.Error as exc:
        print(f"[db] Error computing average ATS score: {exc}")
        return 0.0
