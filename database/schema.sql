-- =============================================================================
-- AI Resume Analyzer Pro — Database Schema
-- =============================================================================
-- This schema defines the core tables for persisting student profiles and
-- their resume analysis history.  All JSON-serialised columns (skills,
-- skills_found, missing_skills, recommendations, internship_matches) store
-- valid JSON arrays so they can be deserialised transparently by the
-- application layer.
-- =============================================================================

-- Students table: stores unique student profiles keyed by email.
CREATE TABLE IF NOT EXISTS students (
    id          INTEGER   PRIMARY KEY AUTOINCREMENT,
    name        TEXT      NOT NULL,
    email       TEXT      UNIQUE NOT NULL,
    resume_text TEXT,
    ats_score   REAL      DEFAULT 0,
    skills      TEXT      DEFAULT '[]',   -- JSON array of matched skill names
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis history: one row per analysis run, linked to a student.
CREATE TABLE IF NOT EXISTS analysis_history (
    id                 INTEGER   PRIMARY KEY AUTOINCREMENT,
    student_id         INTEGER   NOT NULL,
    ats_score          REAL      DEFAULT 0,
    skills_found       TEXT      DEFAULT '[]',   -- JSON array
    missing_skills     TEXT      DEFAULT '[]',   -- JSON array
    recommendations    TEXT      DEFAULT '[]',   -- JSON array
    internship_matches TEXT      DEFAULT '[]',   -- JSON array
    analyzed_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
