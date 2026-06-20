"""
Admin Page — Admin Panel
========================

Student management, search, analysis history, and data export.
"""

import streamlit as st
import pandas as pd
import json
from io import StringIO

from database.db import (
    get_all_students,
    get_student_count,
    get_average_ats_score,
    delete_student,
    get_analysis_history,
)


def render_admin():
    """Render the Admin Panel page."""

    st.markdown(
        "<h1 style='text-align:center;'>👤 Admin Panel</h1>"
        "<p style='text-align:center; color:#888;'>Manage student records, view analysis history, and export data</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Summary Metrics ──────────────────────────────────────────────────
    try:
        total_students = get_student_count()
        avg_score = get_average_ats_score()
    except Exception as exc:
        st.error(f"Database error: {exc}")
        total_students = 0
        avg_score = 0.0

    m1, m2 = st.columns(2)
    with m1:
        st.markdown(
            f"""
            <div class='metric-card' style='background: linear-gradient(135deg, #667eea, #764ba2);'>
                <h2>{total_students}</h2>
                <p>Total Students</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        avg_color = "#00C853" if avg_score >= 70 else "#FFC107" if avg_score >= 40 else "#FF5252"
        st.markdown(
            f"""
            <div class='metric-card' style='background: linear-gradient(135deg, {avg_color}, {avg_color}bb);'>
                <h2>{avg_score:.1f}</h2>
                <p>Average ATS Score</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()

    # ── Student Records ──────────────────────────────────────────────────
    st.subheader("📋 Student Records")

    try:
        students = get_all_students()
    except Exception as exc:
        st.error(f"Could not fetch students: {exc}")
        students = []

    # Search filter
    search = st.text_input(
        "🔍 Search by name or email",
        placeholder="Type to filter…",
        key="admin_search",
    )

    filtered = students
    if search:
        q = search.lower()
        filtered = [
            s for s in students
            if q in s.get("name", "").lower() or q in s.get("email", "").lower()
        ]

    if filtered:
        # Build DataFrame
        df = pd.DataFrame(filtered)
        display_cols = [c for c in ["id", "name", "email", "ats_score", "skills"] if c in df.columns]
        st.dataframe(
            df[display_cols] if display_cols else df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No student records found." if not search else "No students match your search.")

    st.divider()

    # ── Student Management (Delete) ──────────────────────────────────────
    st.subheader("🗑️ Student Management")
    if students:
        for student in filtered:
            sid = student.get("id") or student.get("student_id", "?")
            name = student.get("name", "Unknown")
            email = student.get("email", "")

            with st.container():
                row_c1, row_c2, row_c3 = st.columns([3, 3, 1])
                with row_c1:
                    st.markdown(
                        f"<p style='margin:6px 0; font-weight:600; color:#fff;'>{name}</p>",
                        unsafe_allow_html=True,
                    )
                with row_c2:
                    st.markdown(
                        f"<p style='margin:6px 0; color:#aaa;'>{email}</p>",
                        unsafe_allow_html=True,
                    )
                with row_c3:
                    if st.button("🗑️", key=f"del_{sid}", help=f"Delete {name}"):
                        st.session_state[f"confirm_del_{sid}"] = True

                # Confirmation
                if st.session_state.get(f"confirm_del_{sid}", False):
                    st.warning(f"⚠️ Are you sure you want to delete **{name}** (ID: {sid})?")
                    conf_c1, conf_c2, _ = st.columns([1, 1, 4])
                    with conf_c1:
                        if st.button("✅ Yes", key=f"yes_{sid}"):
                            try:
                                delete_student(sid)
                                st.success(f"Deleted {name}.")
                                st.session_state[f"confirm_del_{sid}"] = False
                                st.rerun()
                            except Exception as exc:
                                st.error(f"Delete failed: {exc}")
                    with conf_c2:
                        if st.button("❌ No", key=f"no_{sid}"):
                            st.session_state[f"confirm_del_{sid}"] = False
                            st.rerun()
    else:
        st.info("No students to manage.")

    st.divider()

    # ── Analysis History ─────────────────────────────────────────────────
    st.subheader("📜 Analysis History")
    if students:
        student_options = {
            f"{s.get('name', 'Unknown')} ({s.get('email', '')})": s.get("id") or s.get("student_id")
            for s in students
        }
        selected_label = st.selectbox(
            "Select a student",
            options=list(student_options.keys()),
            key="admin_history_select",
        )
        selected_id = student_options.get(selected_label)

        if selected_id is not None:
            try:
                history = get_analysis_history(student_id=selected_id)
            except Exception as exc:
                st.error(f"Error fetching history: {exc}")
                history = []

            if history:
                for idx, entry in enumerate(history):
                    analysis_id = entry.get("id") or entry.get("analysis_id", idx)
                    score = entry.get("ats_score", 0)
                    score_color = "#00C853" if score >= 70 else "#FFC107" if score >= 40 else "#FF5252"

                    with st.expander(f"Analysis #{analysis_id}  —  ATS Score: {score}"):
                        st.markdown(
                            f"<p style='font-size:1.1rem; font-weight:700; color:{score_color};'>ATS Score: {score}/100</p>",
                            unsafe_allow_html=True,
                        )

                        # Skills found
                        skills_raw = entry.get("skills_found", "[]")
                        try:
                            skills_list = json.loads(skills_raw) if isinstance(skills_raw, str) else skills_raw
                        except (json.JSONDecodeError, TypeError):
                            skills_list = []
                        if skills_list:
                            tags = " ".join(
                                f"<span style='background:#00C853;color:#fff;padding:3px 10px;"
                                f"border-radius:14px;margin:2px;display:inline-block;font-size:12px;'>"
                                f"{s}</span>"
                                for s in skills_list
                            )
                            st.markdown(f"**Skills Found:** <div style='line-height:2;'>{tags}</div>", unsafe_allow_html=True)

                        # Missing skills
                        missing_raw = entry.get("missing_skills", "[]")
                        try:
                            missing_list = json.loads(missing_raw) if isinstance(missing_raw, str) else missing_raw
                        except (json.JSONDecodeError, TypeError):
                            missing_list = []
                        if missing_list:
                            tags = " ".join(
                                f"<span style='background:#FF5252;color:#fff;padding:3px 10px;"
                                f"border-radius:14px;margin:2px;display:inline-block;font-size:12px;'>"
                                f"{s}</span>"
                                for s in missing_list
                            )
                            st.markdown(f"**Missing Skills:** <div style='line-height:2;'>{tags}</div>", unsafe_allow_html=True)

                        # Recommendations
                        recs_raw = entry.get("recommendations", "[]")
                        try:
                            recs_list = json.loads(recs_raw) if isinstance(recs_raw, str) else recs_raw
                        except (json.JSONDecodeError, TypeError):
                            recs_list = []
                        if recs_list:
                            for r in recs_list:
                                st.markdown(f"- {r}")
            else:
                st.info("No analysis history for this student.")
    else:
        st.info("No students in the database.")

    st.divider()

    # ── Export All Data ──────────────────────────────────────────────────
    st.subheader("📥 Export All Data")
    if students:
        try:
            df_export = pd.DataFrame(students)
            csv_buf = StringIO()
            df_export.to_csv(csv_buf, index=False)
            st.download_button(
                "📊 Download All Students as CSV",
                data=csv_buf.getvalue(),
                file_name="all_students_export.csv",
                mime="text/csv",
                use_container_width=True,
            )
        except Exception as exc:
            st.warning(f"Export failed: {exc}")
    else:
        st.info("No data to export.")
