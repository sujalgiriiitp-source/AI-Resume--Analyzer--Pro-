"""
Analyzer Page — Resume Upload & ATS Score Calculator
=====================================================

Handles PDF resume upload, NLP parsing, ATS scoring,
result display, and database persistence.
"""

import json
import streamlit as st
import plotly.graph_objects as go

from models.nlp_engine import parse_resume, get_missing_skills, load_skills_db
from models.ats_scorer import calculate_ats_score, get_score_interpretation
from models.recommender import recommend_internships
from database.db import add_student, add_analysis, get_student_by_email
from utils.helpers import score_to_color, score_to_grade, score_to_emoji


# ── Category icons for ATS breakdown ────────────────────────────────────────
_CATEGORY_META = {
    "skills_match":   {"icon": "🎯", "label": "Skills Match"},
    "education":      {"icon": "🎓", "label": "Education"},
    "projects":       {"icon": "💻", "label": "Projects"},
    "certifications": {"icon": "📜", "label": "Certifications"},
    "keywords":       {"icon": "🔑", "label": "Keywords"},
    "experience":     {"icon": "💼", "label": "Experience"},
}


def render_analyzer():
    """Render the Resume Analyzer & ATS Score page."""

    st.markdown(
        "<h1 style='text-align:center;'>📄 Resume Analyzer & ATS Score</h1>"
        "<p style='text-align:center; color:#888;'>Upload your PDF resume and get an instant AI-powered evaluation</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── File Upload ──────────────────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Upload your Resume (PDF)",
        type=["pdf"],
        key="resume_upload",
        help="Supported format: PDF. Max recommended size: 5 MB.",
    )

    if uploaded_file is not None:
        # Only re-analyze if the file is new
        current_name = getattr(uploaded_file, "name", "")
        prev_name = st.session_state.get("_last_uploaded_name", "")

        if current_name != prev_name:
            with st.spinner("🔍 Analyzing your resume — this may take a moment…"):
                try:
                    parsed = parse_resume(uploaded_file)
                    st.session_state.parsed_resume = parsed

                    ats_result = calculate_ats_score(parsed)
                    st.session_state.ats_result = ats_result

                    recs = recommend_internships(parsed)
                    st.session_state.recommendations = recs

                    st.session_state["_last_uploaded_name"] = current_name

                    st.success(
                        f"✅ Resume analyzed successfully! "
                        f"ATS Score: **{ats_result.get('total_score', 0):.0f}/100**"
                    )
                except Exception as exc:
                    st.error(f"❌ Failed to analyze resume: {exc}")
                    return

    # ── Guard ────────────────────────────────────────────────────────────
    parsed = st.session_state.get("parsed_resume")
    ats_result = st.session_state.get("ats_result")

    if parsed is None or ats_result is None:
        st.info("👆 Upload a PDF resume above to begin analysis.")
        return

    # ── Parsed Resume Preview ────────────────────────────────────────────
    with st.expander("📋 Parsed Resume Details", expanded=False):
        info_cols = st.columns(2)
        with info_cols[0]:
            st.markdown(f"**Name:** {parsed.get('name', 'N/A')}")
            st.markdown(f"**Email:** {parsed.get('email', 'N/A')}")
            st.markdown(f"**Phone:** {parsed.get('phone', 'N/A')}")
            st.markdown(f"**LinkedIn:** {parsed.get('linkedin', 'N/A')}")
        with info_cols[1]:
            st.markdown(f"**Word Count:** {parsed.get('word_count', 0)}")
            st.markdown(f"**Experience Years:** {parsed.get('experience_years', 0)}")
            sections = ", ".join(parsed.get("sections_found", []))
            st.markdown(f"**Sections Found:** {sections or 'None'}")

        # Education
        if parsed.get("education"):
            st.markdown("**🎓 Education:**")
            for edu in parsed["education"]:
                st.markdown(
                    f"- {edu.get('degree', '')} in {edu.get('field', '')} "
                    f"— *{edu.get('institution', '')}*"
                )

        # Experience
        if parsed.get("experience"):
            st.markdown("**💼 Experience:**")
            for exp in parsed["experience"]:
                st.markdown(f"- {exp.get('title', '')} ({exp.get('duration', '')})")

        # Projects
        if parsed.get("projects"):
            st.markdown("**💻 Projects:**")
            for proj in parsed["projects"]:
                st.markdown(f"- {proj}")

        # Certifications
        if parsed.get("certifications"):
            st.markdown("**📜 Certifications:**")
            for cert in parsed["certifications"]:
                st.markdown(f"- {cert}")

    st.divider()

    # ── ATS Score — Hero Section ─────────────────────────────────────────
    total_score = ats_result.get("total_score", 0)
    color = score_to_color(total_score)
    emoji = score_to_emoji(total_score)
    grade = score_to_grade(total_score)
    interpretation = get_score_interpretation(total_score)

    st.markdown(
        f"""
        <div style='text-align:center; padding:20px 0;'>
            <div style='display:inline-block; background: linear-gradient(135deg, #1a1a2e, #16213e);
                        padding:30px 60px; border-radius:24px;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                        border: 2px solid {color}44;'>
                <h1 style='margin:0; font-size:3.2rem; color:{color};'>{emoji} {total_score:.0f}/100</h1>
                <p style='margin:6px 0 0 0; font-size:1.1rem; color:#ccc;'>
                    Grade: <span style='color:{color}; font-weight:700;'>{grade}</span>
                </p>
                <p style='margin:6px 0 0 0; font-size:0.9rem; color:#999;'>{interpretation}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── ATS Gauge ────────────────────────────────────────────────────────
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=total_score,
            number={"suffix": "/100", "font": {"size": 38, "color": "#fff"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#888"},
                "bar": {"color": color},
                "bgcolor": "rgba(255,255,255,0.05)",
                "steps": [
                    {"range": [0, 40], "color": "rgba(255,82,82,0.15)"},
                    {"range": [40, 70], "color": "rgba(255,193,7,0.15)"},
                    {"range": [70, 100], "color": "rgba(0,200,83,0.15)"},
                ],
            },
        )
    )
    fig_gauge.update_layout(
        height=280,
        margin=dict(t=30, b=10, l=40, r=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.divider()

    # ── Score Breakdown ──────────────────────────────────────────────────
    st.subheader("📊 Score Breakdown")
    breakdown = ats_result.get("breakdown", {})

    cols = st.columns(3)
    for idx, (key, meta) in enumerate(_CATEGORY_META.items()):
        cat = breakdown.get(key, {})
        score = cat.get("score", 0)
        max_score = cat.get("max", 1)
        details = cat.get("details", "")
        pct = score / max_score if max_score else 0

        with cols[idx % 3]:
            bar_color = "#00C853" if pct >= 0.7 else "#FFC107" if pct >= 0.4 else "#FF5252"
            st.markdown(
                f"""
                <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                            padding:16px; border-radius:14px; margin-bottom:12px;
                            border-left: 4px solid {bar_color};
                            box-shadow: 0 2px 10px rgba(0,0,0,0.18);'>
                    <p style='margin:0; font-size:0.95rem; color:#fff; font-weight:600;'>
                        {meta["icon"]} {meta["label"]}
                    </p>
                    <p style='margin:4px 0; font-size:1.3rem; color:{bar_color}; font-weight:800;'>
                        {score:.1f} / {max_score}
                    </p>
                    <div style='background: rgba(255,255,255,0.08); border-radius:6px;
                                height:8px; overflow:hidden;'>
                        <div style='width:{pct*100:.0f}%; height:100%;
                                    background:{bar_color}; border-radius:6px;'></div>
                    </div>
                    <p style='margin:6px 0 0 0; font-size:0.76rem; color:#999;'>{details}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # ── Strengths & Weaknesses ───────────────────────────────────────────
    str_col, weak_col = st.columns(2)

    with str_col:
        st.subheader("✅ Strengths")
        strengths = ats_result.get("strengths", [])
        if strengths:
            for s in strengths:
                st.markdown(
                    f"""
                    <div style='background: linear-gradient(135deg, #00C85322, #00E67611);
                                padding:10px 14px; border-radius:10px; margin-bottom:6px;
                                border-left:3px solid #00C853;'>
                        <p style='margin:0; color:#b9f6ca; font-size:0.88rem;'>✅ {s}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No specific strengths identified.")

    with weak_col:
        st.subheader("⚠️ Weaknesses")
        weaknesses = ats_result.get("weaknesses", [])
        if weaknesses:
            for w in weaknesses:
                st.markdown(
                    f"""
                    <div style='background: linear-gradient(135deg, #FF525222, #FF174411);
                                padding:10px 14px; border-radius:10px; margin-bottom:6px;
                                border-left:3px solid #FF5252;'>
                        <p style='margin:0; color:#ff8a80; font-size:0.88rem;'>⚠️ {w}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.success("🎉 No weaknesses found — excellent!")

    st.divider()

    # ── Save to Database ─────────────────────────────────────────────────
    st.subheader("💾 Save Analysis to Database")
    with st.form("save_form"):
        form_c1, form_c2 = st.columns(2)
        with form_c1:
            student_name = st.text_input("Name", value=parsed.get("name", ""))
        with form_c2:
            student_email = st.text_input("Email", value=parsed.get("email", ""))

        submitted = st.form_submit_button("💾 Save to Database", use_container_width=True)

    if submitted:
        if not student_name or not student_email:
            st.warning("Please provide both name and email.")
        else:
            try:
                skills_db = load_skills_db()
                found = parsed.get("skills", [])
                missing = get_missing_skills(found, skills_db)
                recs = st.session_state.get("recommendations", [])

                # Check for existing student
                existing = get_student_by_email(student_email)
                if existing:
                    student_id = existing.get("id") or existing.get("student_id")
                    st.info("Student already exists — adding new analysis entry.")
                else:
                    student_id = add_student(
                        name=student_name,
                        email=student_email,
                        resume_text=parsed.get("text", ""),
                        ats_score=total_score,
                        skills=json.dumps(found),
                    )
                    st.success(f"✅ Student **{student_name}** saved (ID: {student_id}).")

                # Save analysis
                analysis_id = add_analysis(
                    student_id=student_id,
                    ats_score=total_score,
                    skills_found=json.dumps(found),
                    missing_skills=json.dumps(missing),
                    recommendations=json.dumps(
                        [w for w in ats_result.get("weaknesses", [])]
                    ),
                    internship_matches=json.dumps(
                        [{"title": r.get("title"), "match": r.get("match_percentage")} for r in (recs or [])]
                    ),
                )
                st.success(f"✅ Analysis saved (ID: {analysis_id}).")
            except Exception as exc:
                st.error(f"❌ Could not save to database: {exc}")
