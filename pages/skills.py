"""
Skills Page — Skill Extraction & Gap Analysis
==============================================

Displays found/missing skills as styled tags, categorized breakdowns,
and interactive Plotly charts (radar, bar, donut).
"""

import streamlit as st
import plotly.graph_objects as go

from models.nlp_engine import load_skills_db, get_missing_skills, get_skills_by_category
from utils.helpers import score_to_color


def _skill_tags_html(skills: list, variant: str = "found") -> str:
    """Generate HTML for a list of skill tags.

    Args:
        skills: List of skill name strings.
        variant: 'found' (green) or 'missing' (red).
    """
    if variant == "found":
        bg = "linear-gradient(135deg, #00C853, #00E676)"
        icon = "✅"
    else:
        bg = "linear-gradient(135deg, #FF5252, #FF1744)"
        icon = "❌"

    tags = "".join(
        f"<span style='background:{bg}; color:white; padding:5px 14px; "
        f"border-radius:20px; margin:3px; display:inline-block; "
        f"font-size:13px; font-weight:500;'>{icon} {s}</span>"
        for s in skills
    )
    return f"<div style='line-height:2.2;'>{tags}</div>"


def render_skills():
    """Render the Skills Analysis & Gap Report page."""

    st.markdown(
        "<h1 style='text-align:center;'>🎯 Skills Analysis & Gap Report</h1>"
        "<p style='text-align:center; color:#888;'>Understand your strengths and identify areas for growth</p>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── Guard ────────────────────────────────────────────────────────────
    parsed = st.session_state.get("parsed_resume")
    if parsed is None:
        st.markdown(
            """
            <div style='text-align:center; padding:50px 20px;'>
                <div style='font-size:3.5rem; margin-bottom:10px;'>🎯</div>
                <h3 style='color:#667eea;'>No Resume Analyzed Yet</h3>
                <p style='color:#aaa;'>Head over to <b>📄 Resume Analyzer</b> to upload your resume first.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Data preparation ─────────────────────────────────────────────────
    try:
        found_skills = parsed.get("skills", [])
        skills_db = load_skills_db()
        missing = get_missing_skills(found_skills, skills_db)
        by_category = get_skills_by_category(found_skills, skills_db)
        all_core = skills_db.get("skills", [])
        total = len(all_core) if all_core else 1
        coverage = len(found_skills) / total * 100
    except Exception as exc:
        st.error(f"Error loading skills data: {exc}")
        return

    # ── Summary Metrics ──────────────────────────────────────────────────
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f"""
            <div class='metric-card' style='background: linear-gradient(135deg, #00C853, #00E676);'>
                <h2>{len(found_skills)}</h2>
                <p>Skills Found</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class='metric-card' style='background: linear-gradient(135deg, #FF5252, #FF1744);'>
                <h2>{len(missing)}</h2>
                <p>Missing Skills</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        cov_color = "#00C853" if coverage >= 60 else "#FFC107" if coverage >= 35 else "#FF5252"
        st.markdown(
            f"""
            <div class='metric-card' style='background: linear-gradient(135deg, {cov_color}, {cov_color}cc);'>
                <h2>{coverage:.0f}%</h2>
                <p>Coverage</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Present Skills ───────────────────────────────────────────────────
    st.subheader("✅ Skills Found on Your Resume")
    if found_skills:
        st.markdown(_skill_tags_html(found_skills, "found"), unsafe_allow_html=True)
    else:
        st.info("No skills detected on your resume.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Missing Skills ───────────────────────────────────────────────────
    st.subheader("❌ Missing Skills to Consider")
    if missing:
        st.markdown(_skill_tags_html(missing, "missing"), unsafe_allow_html=True)
    else:
        st.success("🎉 You have excellent skill coverage!")

    st.divider()

    # ── Skills by Category (expandable) ──────────────────────────────────
    st.subheader("📂 Skills by Category")
    categories = skills_db.get("categories", {})

    for cat_name, cat_skills in categories.items():
        found_in_cat = by_category.get(cat_name, [])
        missing_in_cat = [s for s in cat_skills if s.lower() not in [f.lower() for f in found_in_cat]]
        total_in_cat = len(cat_skills)
        found_count = len(found_in_cat)
        cat_pct = found_count / total_in_cat * 100 if total_in_cat else 0
        cat_color = "#00C853" if cat_pct >= 60 else "#FFC107" if cat_pct >= 35 else "#FF5252"

        with st.expander(
            f"{cat_name}  —  {found_count}/{total_in_cat} skills ({cat_pct:.0f}%)"
        ):
            if found_in_cat:
                st.markdown("**Found:**")
                st.markdown(_skill_tags_html(found_in_cat, "found"), unsafe_allow_html=True)
            if missing_in_cat:
                st.markdown("**Missing:**")
                st.markdown(_skill_tags_html(missing_in_cat, "missing"), unsafe_allow_html=True)

    st.divider()

    # ── Charts ───────────────────────────────────────────────────────────
    st.subheader("📊 Visual Analytics")

    chart_c1, chart_c2 = st.columns(2)

    # ── Radar Chart ──────────────────────────────────────────────────────
    with chart_c1:
        st.markdown("**🕸️ Skills Radar by Category**")
        try:
            cat_names = list(categories.keys())
            cat_pcts = []
            for cname in cat_names:
                total_c = len(categories[cname]) if categories[cname] else 1
                found_c = len(by_category.get(cname, []))
                cat_pcts.append(found_c / total_c * 100)

            if cat_names:
                fig_radar = go.Figure()
                fig_radar.add_trace(
                    go.Scatterpolar(
                        r=cat_pcts + [cat_pcts[0]],
                        theta=cat_names + [cat_names[0]],
                        fill="toself",
                        fillcolor="rgba(102,126,234,0.25)",
                        line=dict(color="#667eea", width=2),
                        marker=dict(color="#667eea", size=6),
                        name="Coverage %",
                    )
                )
                fig_radar.update_layout(
                    polar=dict(
                        bgcolor="rgba(0,0,0,0)",
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            gridcolor="rgba(255,255,255,0.1)",
                            tickfont=dict(color="#888", size=10),
                        ),
                        angularaxis=dict(
                            gridcolor="rgba(255,255,255,0.1)",
                            tickfont=dict(size=11),
                        ),
                    ),
                    showlegend=False,
                    height=380,
                    margin=dict(t=30, b=30, l=70, r=70),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#FAFAFA",
                )
                st.plotly_chart(fig_radar, use_container_width=True)
        except Exception as exc:
            st.warning(f"Could not render radar chart: {exc}")

    # ── Gap Analysis Bar Chart ───────────────────────────────────────────
    with chart_c2:
        st.markdown("**📊 Skill Gap Analysis**")
        try:
            cat_names = list(categories.keys())
            found_counts = [len(by_category.get(c, [])) for c in cat_names]
            total_counts = [len(categories[c]) for c in cat_names]

            fig_bar = go.Figure()
            # Total (background)
            fig_bar.add_trace(
                go.Bar(
                    y=cat_names,
                    x=total_counts,
                    orientation="h",
                    name="Total",
                    marker_color="rgba(255,255,255,0.08)",
                    text=total_counts,
                    textposition="auto",
                    textfont=dict(color="#888"),
                )
            )
            # Found (overlay)
            fig_bar.add_trace(
                go.Bar(
                    y=cat_names,
                    x=found_counts,
                    orientation="h",
                    name="Found",
                    marker_color="#667eea",
                    text=found_counts,
                    textposition="auto",
                    textfont=dict(color="#fff"),
                )
            )
            fig_bar.update_layout(
                barmode="overlay",
                height=380,
                margin=dict(t=20, b=30, l=10, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#FAFAFA",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
                yaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as exc:
            st.warning(f"Could not render bar chart: {exc}")

    # ── Donut Chart (full width) ─────────────────────────────────────────
    st.markdown("**🍩 Skills Distribution by Category**")
    try:
        cat_names = list(categories.keys())
        found_counts = [len(by_category.get(c, [])) for c in cat_names]
        # Filter out categories with 0 found
        non_zero = [(n, c) for n, c in zip(cat_names, found_counts) if c > 0]
        if non_zero:
            labels, values = zip(*non_zero)
            colors = [
                "#667eea", "#764ba2", "#00C853", "#FFC107",
                "#03A9F4", "#FF5252", "#E040FB", "#00BCD4",
                "#FF9800", "#8BC34A",
            ]
            fig_donut = go.Figure(
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.45,
                    marker=dict(colors=colors[: len(labels)]),
                    textinfo="label+percent",
                    textfont=dict(size=12),
                    hoverinfo="label+value+percent",
                )
            )
            fig_donut.update_layout(
                height=380,
                margin=dict(t=20, b=20, l=20, r=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#FAFAFA",
                showlegend=True,
                legend=dict(
                    orientation="h", yanchor="bottom", y=-0.15,
                    xanchor="center", x=0.5,
                ),
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("No skills found to visualize.")
    except Exception as exc:
        st.warning(f"Could not render donut chart: {exc}")
