"""
AI Resume Analyzer Pro — Main Application Entry Point
=====================================================

This is the main Streamlit application that orchestrates the entire
AI Resume Analyzer Pro platform. It handles navigation, theming,
session state management, and page routing.

Run with: streamlit run app.py
"""

import os
import streamlit as st

# ── Page config (MUST be the very first Streamlit call) ──────────────────────
st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ──────────────────────────────────────────────────────────────────
from database.db import init_db
from pages.dashboard import render_dashboard
from pages.analyzer import render_analyzer
from pages.skills import render_skills
from pages.internships import render_internships
from pages.comparison import render_comparison
from pages.ai_coach import render_ai_coach
from pages.admin import render_admin


# ── CSS Loader ───────────────────────────────────────────────────────────────
def load_css():
    """Load custom CSS from the assets directory."""
    css_path = os.path.join(os.path.dirname(__file__), "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ── Inline fallback styles (always injected) ────────────────────────────────
def inject_base_styles():
    """Inject baseline premium styles so the app looks great even without styles.css."""
    st.markdown(
        """
        <style>
        /* ── Global tweaks ─────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Sidebar branding area */
        .sidebar-brand {
            text-align: center;
            padding: 1.2rem 0 0.6rem 0;
        }
        .sidebar-brand h1 {
            font-size: 1.35rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
        }
        .sidebar-brand p {
            font-size: 0.78rem;
            opacity: 0.65;
            margin: 0.15rem 0 0 0;
        }

        /* Premium metric card */
        .metric-card {
            padding: 22px 18px;
            border-radius: 16px;
            text-align: center;
            box-shadow: 0 4px 24px rgba(0,0,0,0.18);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .metric-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.28);
        }
        .metric-card h2 {
            margin: 0;
            font-weight: 800;
            font-size: 2rem;
            color: #fff;
        }
        .metric-card p {
            margin: 4px 0 0 0;
            color: rgba(255,255,255,0.82);
            font-size: 0.88rem;
            font-weight: 500;
        }

        /* Skill tags */
        .skill-tag {
            display: inline-block;
            padding: 5px 14px;
            border-radius: 20px;
            margin: 3px;
            font-size: 13px;
            font-weight: 500;
            color: #fff;
        }
        .skill-tag-found { background: linear-gradient(135deg, #00C853, #00E676); }
        .skill-tag-missing { background: linear-gradient(135deg, #FF5252, #FF1744); }

        /* Footer */
        .app-footer {
            text-align: center;
            padding: 2rem 0 1rem 0;
            opacity: 0.5;
            font-size: 0.78rem;
        }

        /* Hide default streamlit hamburger for cleaner look */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Session-state defaults ──────────────────────────────────────────────────
def init_session_state():
    """Ensure all required session-state keys exist."""
    defaults = {
        "parsed_resume": None,
        "ats_result": None,
        "recommendations": None,
        "dark_mode": True,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ── Page map ─────────────────────────────────────────────────────────────────
PAGE_MAP = {
    "🏠 Dashboard": render_dashboard,
    "📄 Resume Analyzer": render_analyzer,
    "🎯 Skills Analysis": render_skills,
    "💼 Internship Matcher": render_internships,
    "⚖️ Resume Comparison": render_comparison,
    "🤖 AI Career Coach": render_ai_coach,
    "👤 Admin Panel": render_admin,
}


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    """Application entry point."""
    # Bootstrap
    init_session_state()
    inject_base_styles()
    load_css()

    # Initialize database
    try:
        init_db()
    except Exception as exc:
        st.error(f"⚠️ Database initialization failed: {exc}")

    # ── Sidebar ──────────────────────────────────────────────────────────
    with st.sidebar:
        # Branding
        st.markdown(
            """
            <div class='sidebar-brand'>
                <h1>🎯 AI Resume Analyzer Pro</h1>
                <p>Smart Career Analytics Platform</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Navigation
        selected_page = st.radio(
            "Navigation",
            list(PAGE_MAP.keys()),
            label_visibility="collapsed",
        )

        st.divider()

        # Theme toggle
        dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
        st.session_state.dark_mode = dark_mode

        # Quick-status indicator
        if st.session_state.parsed_resume is not None:
            name = st.session_state.parsed_resume.get("name", "Student")
            score = (
                st.session_state.ats_result.get("total_score", 0)
                if st.session_state.ats_result
                else 0
            )
            st.markdown(
                f"""
                <div style='background: linear-gradient(135deg,#1a1a2e,#16213e);
                            padding:14px; border-radius:12px; margin-top:8px;
                            border-left:4px solid #667eea;'>
                    <p style='margin:0;font-size:0.82rem;color:#bbb;'>Active Resume</p>
                    <p style='margin:2px 0 0 0;font-weight:600;color:#fff;'>{name}</p>
                    <p style='margin:2px 0 0 0;font-size:0.8rem;color:#667eea;'>
                        ATS Score: {score:.0f}/100
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("📄 Upload a resume to get started!", icon="📄")

        st.divider()

        st.caption("Built with ❤️ using Streamlit")

    # ── Page renderer ────────────────────────────────────────────────────
    page_fn = PAGE_MAP.get(selected_page, render_dashboard)
    try:
        page_fn()
    except Exception as exc:
        st.error(f"⚠️ An error occurred while rendering the page: {exc}")
        st.exception(exc)

    # ── Footer ───────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class='app-footer'>
            <p>AI Resume Analyzer Pro v1.0 &mdash;
            Empowering students with AI-driven career insights</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
