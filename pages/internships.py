"""
Internships Page — Internship Recommendation Engine
====================================================

Displays internship matches with match percentages, skill breakdowns,
and comparative charts.
"""

import streamlit as st
import plotly.graph_objects as go

from models.recommender import get_best_match
from utils.helpers import score_to_color


def _match_color(pct: float) -> str:
    """Return a hex color based on match percentage."""
    if pct >= 70:
        return "#00C853"
    elif pct >= 40:
        return "#FFC107"
    return "#FF5252"


def _internship_card_html(match: dict) -> str:
    """Generate a premium HTML card for an internship match."""
    pct = match.get("match_percentage", 0)
    color = _match_color(pct)
    title = match.get("title", "Untitled")
    category = match.get("category", "General")
    description = match.get("description", "No description available.")
    matched_skills = match.get("matched_skills", [])
    missing_skills = match.get("missing_skills", [])
    required_skills = match.get("required_skills", [])
    nice_to_have = match.get("nice_to_have_matched", [])

    # Build skill tags
    skill_tags = ""
    for skill in required_skills:
        if skill in matched_skills:
            skill_tags += (
                f"<span style='background:linear-gradient(135deg,#00C853,#00E676);"
                f"color:white;padding:4px 10px;border-radius:16px;margin:2px;"
                f"display:inline-block;font-size:12px;'>✅ {skill}</span>"
            )
        elif skill in missing_skills:
            skill_tags += (
                f"<span style='background:linear-gradient(135deg,#FF5252,#FF1744);"
                f"color:white;padding:4px 10px;border-radius:16px;margin:2px;"
                f"display:inline-block;font-size:12px;'>❌ {skill}</span>"
            )
        else:
            skill_tags += (
                f"<span style='background:rgba(255,255,255,0.1);"
                f"color:#ccc;padding:4px 10px;border-radius:16px;margin:2px;"
                f"display:inline-block;font-size:12px;'>{skill}</span>"
            )

    # Nice-to-have tags
    nice_tags = ""
    if nice_to_have:
        nice_tags = "<p style='margin:8px 0 4px 0;font-size:0.8rem;color:#aaa;'>Nice-to-have matched:</p>"
        for s in nice_to_have:
            nice_tags += (
                f"<span style='background:linear-gradient(135deg,#7C4DFF,#B388FF);"
                f"color:white;padding:3px 10px;border-radius:16px;margin:2px;"
                f"display:inline-block;font-size:12px;'>💜 {s}</span>"
            )

    return f"""
    <div style='background: linear-gradient(135deg, #1a1a2e, #16213e);
                padding:22px; border-radius:18px; margin-bottom:16px;
                border-left:5px solid {color};
                box-shadow: 0 4px 20px rgba(0,0,0,0.22);
                transition: transform 0.2s ease;'>
        <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;'>
            <div>
                <h3 style='margin:0; color:#fff; font-size:1.15rem;'>{title}</h3>
                <span style='background:{color}22; color:{color}; padding:3px 12px;
                             border-radius:20px; font-size:0.75rem; font-weight:600;
                             display:inline-block; margin-top:4px;'>{category}</span>
            </div>
            <div style='text-align:right;'>
                <span style='font-size:1.6rem; font-weight:800; color:{color};'>{pct:.0f}%</span>
                <p style='margin:0; font-size:0.75rem; color:#999;'>Match</p>
            </div>
        </div>
        <div style='background:rgba(255,255,255,0.06); border-radius:8px;
                    height:8px; margin:12px 0; overflow:hidden;'>
            <div style='width:{pct}%; height:100%;
                        background: linear-gradient(90deg, {color}, {color}88);
                        border-radius:8px;'></div>
        </div>
        <p style='color:#bbb; font-size:0.88rem; margin:8px 0;'>{description}</p>
        <p style='margin:8px 0 4px 0; font-size:0.8rem; color:#aaa;'>Required Skills:</p>
        <div style='line-height:2;'>{skill_tags}</div>
        {nice_tags}
    </div>
    """


def render_internships():
    """Render the Internship Recommendations page."""

    st.markdown(
        "<h1 style='text-align:center;'>💼 Internship Recommendations</h1>"
        "<p style='text-align:center; color:#888;'>AI-matched internships based on your resume profile</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Guard ────────────────────────────────────────────────────────────
    recommendations = st.session_state.get("recommendations")
    if not recommendations:
        st.markdown(
            """
            <div style='text-align:center; padding:50px 20px;'>
                <div style='font-size:3.5rem; margin-bottom:10px;'>💼</div>
                <h3 style='color:#667eea;'>No Internship Matches Yet</h3>
                <p style='color:#aaa;'>Upload and analyze your resume in <b>📄 Resume Analyzer</b> to get matched.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Sort by match percentage ─────────────────────────────────────────
    sorted_recs = sorted(
        recommendations, key=lambda x: x.get("match_percentage", 0), reverse=True
    )

    # ── Summary Metrics ──────────────────────────────────────────────────
    try:
        best = get_best_match(recommendations)
        avg_pct = sum(r.get("match_percentage", 0) for r in sorted_recs) / len(sorted_recs)
        best_pct = best.get("match_percentage", 0) if best else 0
    except Exception:
        avg_pct = 0
        best_pct = 0

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f"""
            <div class='metric-card' style='background: linear-gradient(135deg, #667eea, #764ba2);'>
                <h2>{len(sorted_recs)}</h2>
                <p>Total Matches</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class='metric-card' style='background: linear-gradient(135deg, #00C853, #00E676);'>
                <h2>{best_pct:.0f}%</h2>
                <p>Best Match</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class='metric-card' style='background: linear-gradient(135deg, #03A9F4, #0288D1);'>
                <h2>{avg_pct:.0f}%</h2>
                <p>Average Match</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Internship Cards ─────────────────────────────────────────────────
    st.subheader("🏢 All Internship Matches")
    for match in sorted_recs:
        st.markdown(_internship_card_html(match), unsafe_allow_html=True)

    st.divider()

    # ── Comparative Bar Chart ────────────────────────────────────────────
    st.subheader("📊 Match Comparison Chart")
    try:
        titles = [r.get("title", "N/A") for r in sorted_recs]
        pcts = [r.get("match_percentage", 0) for r in sorted_recs]
        colors = [_match_color(p) for p in pcts]

        fig_bar = go.Figure(
            go.Bar(
                y=titles,
                x=pcts,
                orientation="h",
                marker_color=colors,
                text=[f"{p:.0f}%" for p in pcts],
                textposition="auto",
                textfont=dict(color="#fff", size=13),
            )
        )
        fig_bar.update_layout(
            height=max(250, len(titles) * 55),
            margin=dict(t=20, b=20, l=10, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#FAFAFA",
            xaxis=dict(
                title="Match %",
                range=[0, 100],
                gridcolor="rgba(255,255,255,0.06)",
            ),
            yaxis=dict(gridcolor="rgba(255,255,255,0.06)", autorange="reversed"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    except Exception as exc:
        st.warning(f"Could not render chart: {exc}")

    st.divider()

    # ── Best Match Highlight ─────────────────────────────────────────────
    st.subheader("🏆 Best Match")
    if best:
        best_color = _match_color(best.get("match_percentage", 0))
        matched = best.get("matched_skills", [])
        skill_chips = " ".join(
            f"<span style='background:linear-gradient(135deg,#00C853,#00E676);"
            f"color:white;padding:4px 10px;border-radius:16px;margin:2px;"
            f"display:inline-block;font-size:12px;'>✅ {s}</span>"
            for s in matched
        )
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #1a1a2e, #0f3460);
                        padding:28px; border-radius:20px;
                        border:2px solid {best_color};
                        box-shadow: 0 6px 30px {best_color}33;'>
                <div style='display:flex; align-items:center; gap:12px; flex-wrap:wrap;'>
                    <span style='font-size:2.5rem;'>🏆</span>
                    <div>
                        <h2 style='margin:0; color:#fff;'>{best.get('title', 'N/A')}</h2>
                        <span style='background:{best_color}22; color:{best_color};
                                     padding:3px 14px; border-radius:20px; font-size:0.85rem;
                                     font-weight:600;'>{best.get('category', '')}</span>
                    </div>
                    <span style='margin-left:auto; font-size:2.2rem; font-weight:800;
                                 color:{best_color};'>{best.get('match_percentage', 0):.0f}%</span>
                </div>
                <p style='color:#bbb; margin:14px 0 8px 0;'>{best.get('description', '')}</p>
                <p style='margin:4px 0; color:#aaa; font-size:0.82rem;'>Matched Skills:</p>
                <div style='line-height:2;'>{skill_chips}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
