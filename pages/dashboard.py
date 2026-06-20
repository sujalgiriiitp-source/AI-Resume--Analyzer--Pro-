"""
Dashboard Page — Student Career Dashboard
==========================================

Displays an overview of resume analysis results including ATS score,
skill coverage, job readiness, internship matches, and export options.
"""

import streamlit as st
import plotly.graph_objects as go

from models.nlp_engine import load_skills_db, get_missing_skills, get_skills_by_category
from models.recommender import get_best_match
from reports.pdf_report import generate_pdf_report
from reports.csv_report import generate_csv_report
from utils.helpers import score_to_color, score_to_grade, score_to_emoji, format_percentage


def _metric_card(value: str, label: str, gradient: str, emoji: str = "") -> str:
    """Return HTML for a premium metric card."""
    return f"""
    <div class='metric-card' style='background: linear-gradient(135deg, {gradient});'>
        <h2>{emoji} {value}</h2>
        <p>{label}</p>
    </div>
    """


def _internship_card(match: dict, rank: int) -> str:
    """Return HTML for an internship summary card."""
    pct = match.get("match_percentage", 0)
    bar_color = "#00C853" if pct >= 70 else "#FFC107" if pct >= 40 else "#FF5252"
    return f"""
    <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                padding: 16px; border-radius: 14px; margin-bottom: 10px;
                border-left: 4px solid {bar_color};
                box-shadow: 0 2px 12px rgba(0,0,0,0.18);'>
        <p style='margin:0; font-weight:700; color:#fff; font-size:0.95rem;'>
            #{rank} {match.get('title', 'N/A')}
        </p>
        <div style='background: rgba(255,255,255,0.08); border-radius:8px;
                    height:8px; margin:8px 0; overflow:hidden;'>
            <div style='width:{pct}%; height:100%;
                        background: linear-gradient(90deg, {bar_color}, {bar_color}aa);
                        border-radius:8px;'></div>
        </div>
        <p style='margin:0; font-size:0.8rem; color:{bar_color};'>
            {pct:.1f}% match &middot; {match.get('category', '')}
        </p>
    </div>
    """


def _tip_card(tip: str, idx: int) -> str:
    """Return HTML for an improvement tip card."""
    icons = ["💡", "🔧", "📈", "🎯", "⚡"]
    icon = icons[idx % len(icons)]
    return f"""
    <div style='background: linear-gradient(135deg, #2d1b4e, #1a1a2e);
                padding: 14px 16px; border-radius: 12px; margin-bottom: 8px;
                border-left: 4px solid #FFC107;
                box-shadow: 0 2px 10px rgba(0,0,0,0.15);'>
        <p style='margin:0; color:#fff; font-size:0.88rem;'>
            {icon} {tip}
        </p>
    </div>
    """


def render_dashboard():
    """Render the Student Career Dashboard page."""

    st.markdown(
        "<h1 style='text-align:center; margin-bottom:0.2rem;'>🏠 Student Career Dashboard</h1>"
        "<p style='text-align:center; color:#888; margin-top:0;'>Your personalized career analytics at a glance</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Guard: no resume analyzed yet ────────────────────────────────────
    parsed = st.session_state.get("parsed_resume")
    ats_result = st.session_state.get("ats_result")
    recommendations = st.session_state.get("recommendations")

    if parsed is None or ats_result is None:
        st.markdown(
            """
            <div style='text-align:center; padding:60px 20px;'>
                <div style='font-size:4rem; margin-bottom:12px;'>📄</div>
                <h2 style='color:#667eea; margin-bottom:8px;'>Welcome to AI Resume Analyzer Pro!</h2>
                <p style='color:#aaa; max-width:520px; margin:0 auto 24px auto;'>
                    Upload your resume to unlock powerful AI-driven insights — ATS scoring,
                    skill-gap analysis, internship matching, and personalised career coaching.
                </p>
                <div style='background: linear-gradient(135deg,#667eea,#764ba2);
                            display:inline-block; padding:12px 32px; border-radius:30px;
                            color:#fff; font-weight:600; font-size:1rem;
                            box-shadow: 0 4px 20px rgba(102,126,234,0.4);'>
                    ← Navigate to <b>📄 Resume Analyzer</b> in the sidebar
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Derived metrics ──────────────────────────────────────────────────
    try:
        total_score = ats_result.get("total_score", 0)
        found_skills = parsed.get("skills", [])

        skills_db = load_skills_db()
        all_core = skills_db.get("skills", [])
        total_core = len(all_core) if all_core else 1
        skill_coverage = len(found_skills) / total_core * 100

        exp_years = parsed.get("experience_years", 0)
        job_readiness = (
            0.40 * (total_score / 100)
            + 0.30 * min(skill_coverage / 100, 1.0)
            + 0.30 * min(exp_years / 2, 1.0)
        ) * 100

        best = get_best_match(recommendations) if recommendations else None
        best_pct = best.get("match_percentage", 0) if best else 0

        score_color = score_to_color(total_score)
        score_emoji = score_to_emoji(total_score)
        grade = score_to_grade(total_score)
    except Exception as exc:
        st.error(f"Error computing metrics: {exc}")
        return

    # ── Row 1: Metric Cards ──────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            _metric_card(f"{total_score:.0f}", "ATS Score", "#667eea, #764ba2", score_emoji),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            _metric_card(
                f"{skill_coverage:.0f}%", "Skill Coverage", "#00C853, #00E676", "📊"
            ),
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            _metric_card(
                f"{job_readiness:.0f}%", "Job Readiness", "#FF6F00, #FFA726", "🚀"
            ),
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            _metric_card(
                f"{best_pct:.0f}%", "Internship Readiness", "#0288D1, #03A9F4", "💼"
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Row 2: ATS Gauge + Skills Radar ──────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 ATS Score Gauge")
        fig_gauge = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=total_score,
                number={"suffix": "/100", "font": {"size": 42, "color": "#fff"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#888"},
                    "bar": {"color": score_color},
                    "bgcolor": "rgba(255,255,255,0.05)",
                    "steps": [
                        {"range": [0, 40], "color": "rgba(255,82,82,0.18)"},
                        {"range": [40, 70], "color": "rgba(255,193,7,0.18)"},
                        {"range": [70, 100], "color": "rgba(0,200,83,0.18)"},
                    ],
                    "threshold": {
                        "line": {"color": "#fff", "width": 3},
                        "thickness": 0.8,
                        "value": total_score,
                    },
                },
                title={"text": f"Grade: {grade}", "font": {"size": 16, "color": "#bbb"}},
            )
        )
        fig_gauge.update_layout(
            height=320,
            margin=dict(t=40, b=20, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FAFAFA",
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_right:
        st.subheader("🕸️ Skills Radar")
        try:
            by_cat = get_skills_by_category(found_skills, skills_db)
            categories_list = list(by_cat.keys()) if by_cat else []
            cat_values = []
            for cat in categories_list:
                # Count how many skills in this category are in found_skills
                cat_skills_all = skills_db.get("categories", {}).get(cat, [])
                found_in_cat = len(by_cat.get(cat, []))
                total_in_cat = len(cat_skills_all) if cat_skills_all else 1
                cat_values.append(found_in_cat / total_in_cat * 100)

            if categories_list:
                fig_radar = go.Figure()
                fig_radar.add_trace(
                    go.Scatterpolar(
                        r=cat_values + [cat_values[0]],
                        theta=categories_list + [categories_list[0]],
                        fill="toself",
                        fillcolor="rgba(102,126,234,0.25)",
                        line=dict(color="#667eea", width=2),
                        name="Your Skills",
                    )
                )
                fig_radar.update_layout(
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            gridcolor="rgba(255,255,255,0.1)",
                            tickfont=dict(color="#888"),
                        ),
                        angularaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
                    ),
                    showlegend=False,
                    height=320,
                    margin=dict(t=40, b=20, l=60, r=60),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#FAFAFA",
                )
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("No categorized skills data available.")
        except Exception as exc:
            st.warning(f"Could not render radar chart: {exc}")

    st.divider()

    # ── Row 3: Internship Summary + Tips ─────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("💼 Top Internship Matches")
        if recommendations:
            sorted_recs = sorted(
                recommendations, key=lambda x: x.get("match_percentage", 0), reverse=True
            )
            for rank, match in enumerate(sorted_recs[:3], start=1):
                st.markdown(_internship_card(match, rank), unsafe_allow_html=True)
        else:
            st.info("No internship matches available.")

    with col_b:
        st.subheader("⚡ Quick Improvement Tips")
        weaknesses = ats_result.get("weaknesses", [])
        if weaknesses:
            for idx, tip in enumerate(weaknesses[:3]):
                st.markdown(_tip_card(tip, idx), unsafe_allow_html=True)
        else:
            st.success("🎉 No major weaknesses detected — great job!")

    st.divider()

    # ── Export Buttons ───────────────────────────────────────────────────
    st.subheader("📥 Export Reports")
    exp_c1, exp_c2, _ = st.columns([1, 1, 2])

    with exp_c1:
        try:
            missing = get_missing_skills(found_skills, skills_db)
            suggestions_obj = ats_result.get("weaknesses", [])
            intern_matches = recommendations or []
            pdf_bytes = generate_pdf_report(
                student_name=parsed.get("name", "Student"),
                email=parsed.get("email", ""),
                ats_data=ats_result,
                skills_found=found_skills,
                missing_skills=missing,
                internship_matches=intern_matches,
                suggestions=suggestions_obj,
            )
            st.download_button(
                "📄 Download PDF Report",
                data=pdf_bytes,
                file_name="resume_analysis_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as exc:
            st.warning(f"PDF generation unavailable: {exc}")

    with exp_c2:
        try:
            missing = get_missing_skills(found_skills, skills_db)
            csv_str = generate_csv_report(
                student_name=parsed.get("name", "Student"),
                email=parsed.get("email", ""),
                ats_score=total_score,
                skills_found=found_skills,
                missing_skills=missing,
                internship_matches=recommendations or [],
            )
            st.download_button(
                "📊 Download CSV Report",
                data=csv_str,
                file_name="resume_analysis_report.csv",
                mime="text/csv",
                use_container_width=True,
            )
        except Exception as exc:
            st.warning(f"CSV generation unavailable: {exc}")
