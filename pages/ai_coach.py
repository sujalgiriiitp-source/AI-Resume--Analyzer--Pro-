"""
AI Coach Page — AI Career Coach
================================

Four-tab interface for resume feedback, improvement plans,
skill roadmaps, and project recommendations.
"""

import streamlit as st

from models.ai_advisor import (
    generate_improvement_suggestions,
    generate_skill_roadmap,
    generate_project_recommendations,
    generate_resume_feedback,
    generate_career_advice,
)
from utils.helpers import score_to_color


# ── Default role list (used if no internship recommendations exist) ──────
_DEFAULT_ROLES = [
    "Data Science Intern",
    "Web Development Intern",
    "Machine Learning Intern",
    "Software Engineering Intern",
    "Cloud Computing Intern",
]


def _get_role_options() -> list:
    """Build role selector options from recommendations or defaults."""
    recs = st.session_state.get("recommendations", [])
    if recs:
        titles = [r.get("title", "") for r in recs if r.get("title")]
        return titles if titles else _DEFAULT_ROLES
    return _DEFAULT_ROLES


def _difficulty_badge(diff: str) -> str:
    """Return a styled HTML badge for difficulty level."""
    diff_lower = diff.lower().strip() if diff else "medium"
    if diff_lower in ("easy", "beginner"):
        bg = "linear-gradient(135deg, #00C853, #00E676)"
    elif diff_lower in ("hard", "advanced"):
        bg = "linear-gradient(135deg, #FF5252, #FF1744)"
    else:
        bg = "linear-gradient(135deg, #FFC107, #FFD54F)"
    return (
        f"<span style='background:{bg}; color:white; padding:3px 12px; "
        f"border-radius:14px; font-size:0.75rem; font-weight:600;'>{diff}</span>"
    )


def render_ai_coach():
    """Render the AI Career Coach page."""

    st.markdown(
        "<h1 style='text-align:center;'>🤖 AI Career Coach</h1>"
        "<p style='text-align:center; color:#888;'>Personalised AI-driven guidance to accelerate your career</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Guard ────────────────────────────────────────────────────────────
    parsed = st.session_state.get("parsed_resume")
    if parsed is None:
        st.markdown(
            """
            <div style='text-align:center; padding:50px 20px;'>
                <div style='font-size:3.5rem; margin-bottom:10px;'>🤖</div>
                <h3 style='color:#667eea;'>No Resume Analyzed Yet</h3>
                <p style='color:#aaa;'>Navigate to <b>📄 Resume Analyzer</b> and upload your resume to unlock AI coaching.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    ats_result = st.session_state.get("ats_result")
    recommendations = st.session_state.get("recommendations", [])

    # ── Tabs ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(
        ["💡 Resume Feedback", "🎯 Improvement Plan", "🗺️ Skill Roadmap", "🚀 Project Ideas"]
    )

    # ══════════════════════════════════════════════════════════════════════
    # Tab 1 — Resume Feedback
    # ══════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### 💡 Section-by-Section Resume Feedback")
        st.markdown(
            "<p style='color:#aaa;'>AI-generated advice for each section of your resume.</p>",
            unsafe_allow_html=True,
        )

        try:
            feedback = generate_resume_feedback(parsed, ats_result)
            if feedback and isinstance(feedback, dict):
                for section_key, content in feedback.items():
                    section_title = section_key.replace("_", " ").title()
                    with st.expander(f"📝 {section_title}", expanded=False):
                        if isinstance(content, list):
                            for item in content:
                                st.markdown(
                                    f"""
                                    <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);
                                                padding:12px 16px; border-radius:10px; margin-bottom:6px;
                                                border-left:3px solid #667eea;'>
                                        <p style='margin:0; color:#ddd; font-size:0.88rem;'>{item}</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                        elif isinstance(content, dict):
                            for sub_key, sub_val in content.items():
                                st.markdown(f"**{sub_key.replace('_', ' ').title()}:**")
                                st.markdown(
                                    f"<p style='color:#ccc; font-size:0.9rem;'>{sub_val}</p>",
                                    unsafe_allow_html=True,
                                )
                        else:
                            st.markdown(
                                f"""
                                <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);
                                            padding:14px 18px; border-radius:12px;
                                            border-left:3px solid #667eea;'>
                                    <p style='margin:0; color:#ddd; font-size:0.9rem;'>{content}</p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
            else:
                st.info("No feedback generated. Try re-analyzing your resume.")
        except Exception as exc:
            st.error(f"⚠️ Could not generate resume feedback: {exc}")

    # ══════════════════════════════════════════════════════════════════════
    # Tab 2 — Improvement Plan
    # ══════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 🎯 Personalised Improvement Plan")
        st.markdown(
            "<p style='color:#aaa;'>Actionable steps to boost your ATS score and career readiness.</p>",
            unsafe_allow_html=True,
        )

        try:
            suggestions = generate_improvement_suggestions(parsed, ats_result)

            if suggestions and isinstance(suggestions, dict):
                # Missing Skills
                missing_skills = suggestions.get("missing_skills", [])
                if missing_skills:
                    st.markdown("#### ❌ Missing Skills to Add")
                    tags = "".join(
                        f"<span style='background:linear-gradient(135deg,#FF5252,#FF1744);"
                        f"color:white;padding:5px 14px;border-radius:20px;margin:3px;"
                        f"display:inline-block;font-size:13px;font-weight:500;'>❌ {s}</span>"
                        for s in missing_skills
                    )
                    st.markdown(f"<div style='line-height:2.2;'>{tags}</div>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)

                # Suggested Projects
                projects = suggestions.get("suggested_projects", [])
                if projects:
                    st.markdown("#### 💻 Suggested Projects")
                    for proj in projects:
                        if isinstance(proj, dict):
                            title = proj.get("title", proj.get("name", "Project"))
                            desc = proj.get("description", "")
                        else:
                            title = str(proj)
                            desc = ""
                        st.markdown(
                            f"""
                            <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);
                                        padding:14px 18px; border-radius:12px; margin-bottom:8px;
                                        border-left:4px solid #764ba2;
                                        box-shadow:0 2px 10px rgba(0,0,0,0.15);'>
                                <p style='margin:0; font-weight:600; color:#fff;'>💻 {title}</p>
                                {"<p style='margin:4px 0 0 0; color:#bbb; font-size:0.85rem;'>" + desc + "</p>" if desc else ""}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    st.markdown("<br>", unsafe_allow_html=True)

                # Certifications
                certs = suggestions.get("certifications", [])
                if certs:
                    st.markdown("#### 📜 Recommended Certifications")
                    for cert in certs:
                        cert_text = cert if isinstance(cert, str) else cert.get("name", str(cert))
                        st.markdown(
                            f"""
                            <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);
                                        padding:12px 16px; border-radius:10px; margin-bottom:6px;
                                        border-left:4px solid #FFC107;'>
                                <p style='margin:0; color:#fff; font-size:0.9rem;'>📜 {cert_text}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    st.markdown("<br>", unsafe_allow_html=True)

                # Formatting Tips
                tips = suggestions.get("formatting_tips", [])
                if tips:
                    st.markdown("#### 🎨 Formatting Tips")
                    st.markdown(
                        "<div style='background:linear-gradient(135deg,#1a1a2e,#16213e);"
                        "padding:18px 22px; border-radius:14px; border-left:4px solid #03A9F4;'>",
                        unsafe_allow_html=True,
                    )
                    for i, tip in enumerate(tips, 1):
                        tip_text = tip if isinstance(tip, str) else str(tip)
                        st.markdown(
                            f"<p style='margin:6px 0; color:#ddd; font-size:0.88rem;'>"
                            f"<b style='color:#03A9F4;'>{i}.</b> {tip_text}</p>",
                            unsafe_allow_html=True,
                        )
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info("No improvement suggestions generated.")
        except Exception as exc:
            st.error(f"⚠️ Could not generate improvement plan: {exc}")

    # ══════════════════════════════════════════════════════════════════════
    # Tab 3 — Skill Roadmap
    # ══════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("### 🗺️ Personalised Skill Roadmap")
        st.markdown(
            "<p style='color:#aaa;'>A step-by-step plan to build skills for your target role.</p>",
            unsafe_allow_html=True,
        )

        role_options = _get_role_options()
        selected_role = st.selectbox(
            "🎯 Select your target role",
            options=role_options,
            key="roadmap_role",
        )

        if selected_role:
            current_skills = parsed.get("skills", [])
            try:
                roadmap = generate_skill_roadmap(current_skills, selected_role)

                if roadmap and isinstance(roadmap, list):
                    total_steps = len(roadmap)
                    for idx, step in enumerate(roadmap):
                        step_num = idx + 1
                        skill = step.get("skill", "Unknown Skill")
                        reason = step.get("reason", "")
                        resources = step.get("resources", [])
                        duration = step.get("duration", "")

                        # Progress calculation
                        progress_pct = step_num / total_steps * 100

                        # Gradient border colors cycle
                        border_colors = ["#667eea", "#764ba2", "#00C853", "#FFC107", "#03A9F4", "#E040FB"]
                        border_color = border_colors[idx % len(border_colors)]

                        st.markdown(
                            f"""
                            <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);
                                        padding:20px 22px; border-radius:16px; margin-bottom:14px;
                                        border-left:5px solid {border_color};
                                        box-shadow:0 3px 14px rgba(0,0,0,0.2);'>
                                <div style='display:flex; align-items:center; gap:12px; margin-bottom:8px;'>
                                    <div style='background:{border_color}; color:white; width:36px; height:36px;
                                                border-radius:50%; display:flex; align-items:center;
                                                justify-content:center; font-weight:800; font-size:0.95rem;
                                                flex-shrink:0;'>{step_num}</div>
                                    <div>
                                        <p style='margin:0; font-size:1.05rem; font-weight:700; color:#fff;'>{skill}</p>
                                        <p style='margin:2px 0 0 0; font-size:0.78rem; color:#888;'>
                                            Step {step_num} of {total_steps} &middot; {duration}
                                        </p>
                                    </div>
                                </div>
                                <p style='color:#bbb; font-size:0.88rem; margin:8px 0;'>{reason}</p>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Resources
                        if resources:
                            res_html = "<p style='margin:6px 0 2px 0; font-size:0.8rem; color:#aaa;'>📚 Resources:</p><ul style='margin:0; padding-left:18px;'>"
                            for res in resources:
                                res_text = res if isinstance(res, str) else str(res)
                                res_html += f"<li style='color:#ccc; font-size:0.82rem; margin:2px 0;'>{res_text}</li>"
                            res_html += "</ul>"
                            st.markdown(res_html, unsafe_allow_html=True)

                        # Progress bar
                        st.markdown(
                            f"""
                                <div style='background:rgba(255,255,255,0.06); border-radius:6px;
                                            height:5px; margin-top:10px; overflow:hidden;'>
                                    <div style='width:{progress_pct:.0f}%; height:100%;
                                                background:linear-gradient(90deg, {border_color}, {border_color}88);
                                                border-radius:6px;'></div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("No roadmap generated. Try selecting a different role.")
            except Exception as exc:
                st.error(f"⚠️ Could not generate skill roadmap: {exc}")

    # ══════════════════════════════════════════════════════════════════════
    # Tab 4 — Project Ideas
    # ══════════════════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### 🚀 Project Recommendations")
        st.markdown(
            "<p style='color:#aaa;'>Hands-on projects to strengthen your profile for your target role.</p>",
            unsafe_allow_html=True,
        )

        role_options_p = _get_role_options()
        selected_role_p = st.selectbox(
            "🎯 Select your target role",
            options=role_options_p,
            key="projects_role",
        )

        if selected_role_p:
            current_skills = parsed.get("skills", [])
            try:
                projects = generate_project_recommendations(current_skills, selected_role_p)

                if projects and isinstance(projects, list):
                    # Two-column grid
                    cols = st.columns(2)
                    for idx, proj in enumerate(projects):
                        title = proj.get("title", "Untitled Project")
                        desc = proj.get("description", "")
                        skills = proj.get("skills", [])
                        difficulty = proj.get("difficulty", "Medium")
                        time_est = proj.get("time", "")

                        # Skill tags
                        skill_tags = "".join(
                            f"<span style='background:rgba(102,126,234,0.2); color:#667eea;"
                            f"padding:3px 10px; border-radius:14px; margin:2px;"
                            f"display:inline-block; font-size:12px;'>{s}</span>"
                            for s in skills
                        )

                        card_html = f"""
                        <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);
                                    padding:22px; border-radius:16px; margin-bottom:14px;
                                    box-shadow:0 4px 18px rgba(0,0,0,0.2);
                                    border-top:3px solid #667eea;
                                    min-height:220px;'>
                            <h4 style='margin:0 0 8px 0; color:#fff;'>🚀 {title}</h4>
                            <p style='color:#bbb; font-size:0.88rem; margin:0 0 12px 0;'>{desc}</p>
                            <div style='line-height:2; margin-bottom:10px;'>{skill_tags}</div>
                            <div style='display:flex; gap:12px; align-items:center; flex-wrap:wrap;'>
                                {_difficulty_badge(difficulty)}
                                {"<span style='color:#aaa; font-size:0.8rem;'>⏱️ " + time_est + "</span>" if time_est else ""}
                            </div>
                        </div>
                        """

                        with cols[idx % 2]:
                            st.markdown(card_html, unsafe_allow_html=True)
                else:
                    st.info("No project recommendations generated. Try a different role.")
            except Exception as exc:
                st.error(f"⚠️ Could not generate project ideas: {exc}")
