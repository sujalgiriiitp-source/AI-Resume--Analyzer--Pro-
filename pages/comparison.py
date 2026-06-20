"""
Comparison Page — Resume Comparison Tool
=========================================

Side-by-side comparison of two PDF resumes with ATS scores,
metrics, charts, and skills overlap analysis.
"""

import streamlit as st
import plotly.graph_objects as go

from models.nlp_engine import parse_resume
from models.ats_scorer import calculate_ats_score
from utils.helpers import score_to_color


def _comparison_card(label: str, parsed: dict, ats: dict, is_winner: bool = False) -> str:
    """Generate HTML for a resume comparison card."""
    score = ats.get("total_score", 0)
    color = score_to_color(score)
    name = parsed.get("name", "Unknown")
    skills_count = len(parsed.get("skills", []))
    projects_count = len(parsed.get("projects", []))
    exp_years = parsed.get("experience_years", 0)
    edu_list = parsed.get("education", [])
    edu_str = (
        f"{edu_list[0].get('degree', '')} — {edu_list[0].get('institution', '')}"
        if edu_list
        else "Not specified"
    )

    border = "border:2px solid #FFD700; box-shadow:0 0 20px rgba(255,215,0,0.3);" if is_winner else ""

    return f"""
    <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);
                padding:24px; border-radius:18px; {border}
                box-shadow:0 4px 20px rgba(0,0,0,0.2);'>
        <div style='text-align:center; margin-bottom:14px;'>
            {"<span style='font-size:1.2rem;'>🏆 WINNER</span><br>" if is_winner else ""}
            <h3 style='color:#fff; margin:4px 0;'>{label}</h3>
            <p style='color:#aaa; margin:0; font-size:0.85rem;'>{name}</p>
        </div>
        <div style='text-align:center; margin:16px 0;'>
            <span style='font-size:2.8rem; font-weight:800; color:{color};'>{score:.0f}</span>
            <span style='color:#888; font-size:1rem;'>/100</span>
        </div>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:10px;'>
            <div style='background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; text-align:center;'>
                <p style='margin:0; font-size:1.2rem; font-weight:700; color:#667eea;'>{skills_count}</p>
                <p style='margin:0; font-size:0.75rem; color:#aaa;'>Skills</p>
            </div>
            <div style='background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; text-align:center;'>
                <p style='margin:0; font-size:1.2rem; font-weight:700; color:#764ba2;'>{projects_count}</p>
                <p style='margin:0; font-size:0.75rem; color:#aaa;'>Projects</p>
            </div>
            <div style='background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; text-align:center;'>
                <p style='margin:0; font-size:1.2rem; font-weight:700; color:#03A9F4;'>{exp_years:.1f}</p>
                <p style='margin:0; font-size:0.75rem; color:#aaa;'>Exp. Years</p>
            </div>
            <div style='background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; text-align:center;'>
                <p style='margin:0; font-size:1.2rem; font-weight:700; color:#FFC107;'>{len(edu_list)}</p>
                <p style='margin:0; font-size:0.75rem; color:#aaa;'>Education</p>
            </div>
        </div>
        <p style='color:#999; font-size:0.78rem; margin:10px 0 0 0; text-align:center;'>🎓 {edu_str}</p>
    </div>
    """


def render_comparison():
    """Render the Resume Comparison page."""

    st.markdown(
        "<h1 style='text-align:center;'>⚖️ Resume Comparison</h1>"
        "<p style='text-align:center; color:#888;'>Compare two resumes side-by-side to see how they stack up</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── File Uploaders ───────────────────────────────────────────────────
    up_c1, up_c2 = st.columns(2)
    with up_c1:
        file1 = st.file_uploader("📄 Upload Resume 1 (PDF)", type=["pdf"], key="cmp_file1")
    with up_c2:
        file2 = st.file_uploader("📄 Upload Resume 2 (PDF)", type=["pdf"], key="cmp_file2")

    if file1 is None or file2 is None:
        st.markdown(
            """
            <div style='text-align:center; padding:40px 20px;'>
                <div style='font-size:3rem; margin-bottom:10px;'>⚖️</div>
                <p style='color:#aaa;'>Upload <b>two PDF resumes</b> above to start comparing.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Parse & Score ────────────────────────────────────────────────────
    with st.spinner("🔍 Parsing and scoring both resumes…"):
        try:
            parsed1 = parse_resume(file1)
            ats1 = calculate_ats_score(parsed1)
        except Exception as exc:
            st.error(f"❌ Error processing Resume 1: {exc}")
            return

        try:
            parsed2 = parse_resume(file2)
            ats2 = calculate_ats_score(parsed2)
        except Exception as exc:
            st.error(f"❌ Error processing Resume 2: {exc}")
            return

    score1 = ats1.get("total_score", 0)
    score2 = ats2.get("total_score", 0)
    winner = 1 if score1 >= score2 else 2

    # ── Winner Banner ────────────────────────────────────────────────────
    winner_name = parsed1.get("name", "Resume 1") if winner == 1 else parsed2.get("name", "Resume 2")
    winner_score = max(score1, score2)
    st.markdown(
        f"""
        <div style='text-align:center; background:linear-gradient(135deg,#FFD700,#FFA000);
                    padding:16px; border-radius:14px; margin-bottom:20px;
                    box-shadow:0 4px 20px rgba(255,215,0,0.3);'>
            <p style='margin:0; color:#1a1a2e; font-size:1.1rem; font-weight:700;'>
                🏆 Winner: {winner_name} — ATS Score {winner_score:.0f}/100
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Side-by-Side Cards ───────────────────────────────────────────────
    card_c1, card_c2 = st.columns(2)
    with card_c1:
        st.markdown(
            _comparison_card("📄 Resume 1", parsed1, ats1, is_winner=(winner == 1)),
            unsafe_allow_html=True,
        )
    with card_c2:
        st.markdown(
            _comparison_card("📄 Resume 2", parsed2, ats2, is_winner=(winner == 2)),
            unsafe_allow_html=True,
        )

    st.divider()

    # ── Comparative Bar Chart ────────────────────────────────────────────
    st.subheader("📊 Metrics Comparison")
    try:
        metrics = ["ATS Score", "Skills", "Projects", "Experience"]
        vals1 = [
            score1,
            len(parsed1.get("skills", [])) * 10,
            len(parsed1.get("projects", [])) * 20,
            parsed1.get("experience_years", 0) * 10,
        ]
        vals2 = [
            score2,
            len(parsed2.get("skills", [])) * 10,
            len(parsed2.get("projects", [])) * 20,
            parsed2.get("experience_years", 0) * 10,
        ]

        name1 = parsed1.get("name", "Resume 1") or "Resume 1"
        name2 = parsed2.get("name", "Resume 2") or "Resume 2"

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                name=name1,
                x=metrics,
                y=vals1,
                marker_color="#667eea",
                text=[f"{v:.0f}" for v in vals1],
                textposition="auto",
                textfont=dict(color="#fff"),
            )
        )
        fig.add_trace(
            go.Bar(
                name=name2,
                x=metrics,
                y=vals2,
                marker_color="#764ba2",
                text=[f"{v:.0f}" for v in vals2],
                textposition="auto",
                textfont=dict(color="#fff"),
            )
        )
        fig.update_layout(
            barmode="group",
            height=360,
            margin=dict(t=30, b=30, l=30, r=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FAFAFA",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", title="Score (scaled)"),
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as exc:
        st.warning(f"Could not render comparison chart: {exc}")

    st.divider()

    # ── Skills Venn-like Comparison ──────────────────────────────────────
    st.subheader("🔀 Skills Overlap")
    skills1 = set(s.lower() for s in parsed1.get("skills", []))
    skills2 = set(s.lower() for s in parsed2.get("skills", []))
    common = skills1 & skills2
    unique1 = skills1 - skills2
    unique2 = skills2 - skills1

    # Display original casing where possible
    orig_skills1 = {s.lower(): s for s in parsed1.get("skills", [])}
    orig_skills2 = {s.lower(): s for s in parsed2.get("skills", [])}

    v1, v2, v3 = st.columns(3)
    with v1:
        st.markdown(
            f"<h4 style='color:#667eea;'>Unique to Resume 1 ({len(unique1)})</h4>",
            unsafe_allow_html=True,
        )
        tags = "".join(
            f"<span style='background:linear-gradient(135deg,#667eea,#764ba2);"
            f"color:white;padding:4px 12px;border-radius:18px;margin:2px;"
            f"display:inline-block;font-size:12px;'>{orig_skills1.get(s, s)}</span>"
            for s in unique1
        )
        st.markdown(f"<div style='line-height:2.2;'>{tags}</div>" if tags else "<p style='color:#888;'>None</p>", unsafe_allow_html=True)

    with v2:
        st.markdown(
            f"<h4 style='color:#00C853;'>Common Skills ({len(common)})</h4>",
            unsafe_allow_html=True,
        )
        tags = "".join(
            f"<span style='background:linear-gradient(135deg,#00C853,#00E676);"
            f"color:white;padding:4px 12px;border-radius:18px;margin:2px;"
            f"display:inline-block;font-size:12px;'>{orig_skills1.get(s, orig_skills2.get(s, s))}</span>"
            for s in common
        )
        st.markdown(f"<div style='line-height:2.2;'>{tags}</div>" if tags else "<p style='color:#888;'>None</p>", unsafe_allow_html=True)

    with v3:
        st.markdown(
            f"<h4 style='color:#E040FB;'>Unique to Resume 2 ({len(unique2)})</h4>",
            unsafe_allow_html=True,
        )
        tags = "".join(
            f"<span style='background:linear-gradient(135deg,#E040FB,#7C4DFF);"
            f"color:white;padding:4px 12px;border-radius:18px;margin:2px;"
            f"display:inline-block;font-size:12px;'>{orig_skills2.get(s, s)}</span>"
            for s in unique2
        )
        st.markdown(f"<div style='line-height:2.2;'>{tags}</div>" if tags else "<p style='color:#888;'>None</p>", unsafe_allow_html=True)
