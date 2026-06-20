"""
utils/helpers.py — Utility Functions for AI Resume Analyzer Pro
================================================================
Stateless helper functions used across the application for score
formatting, colour mapping, text manipulation, and chart theming.
"""

from typing import Dict


# ---------------------------------------------------------------------------
# Score → visual mapping helpers
# ---------------------------------------------------------------------------

def score_to_color(score: float) -> str:
    """
    Map a numeric ATS score (0-100) to a hex colour string.

    Ranges:
        < 40  → red
        40-60 → orange
        60-75 → yellow
        > 75  → green
    """
    if score < 40:
        return "#FF4B4B"   # Red
    elif score < 60:
        return "#FFA726"   # Orange
    elif score < 75:
        return "#FFEE58"   # Yellow
    else:
        return "#66BB6A"   # Green


def score_to_grade(score: float) -> str:
    """
    Convert a numeric ATS score to a letter grade.

    Mapping:
        >= 90 → A+
        >= 80 → A
        >= 70 → B
        >= 60 → C
        >= 50 → D
        <  50 → F
    """
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"


def score_to_emoji(score: float) -> str:
    """
    Return an emoji that visually represents the score tier.

    Mapping:
        >= 90 → 🌟
        >= 75 → 🎯
        >= 60 → 👍
        >= 40 → ⚠️
        <  40 → 🔴
    """
    if score >= 90:
        return "🌟"
    elif score >= 75:
        return "🎯"
    elif score >= 60:
        return "👍"
    elif score >= 40:
        return "⚠️"
    else:
        return "🔴"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_percentage(value: float) -> str:
    """
    Format a numeric value as a percentage string with one decimal place.

    Examples:
        78.333  → "78.3%"
        100.0   → "100.0%"
        0       → "0.0%"
    """
    return f"{value:.1f}%"


def truncate_text(text: str, max_length: int = 200) -> str:
    """
    Truncate *text* to *max_length* characters, appending an ellipsis if
    the string was shortened.  Returns the original string when it is
    already within the limit.
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "…"


# ---------------------------------------------------------------------------
# Chart / brand colour palette
# ---------------------------------------------------------------------------

def get_color_palette() -> Dict[str, str]:
    """
    Return a dictionary of brand colours used for Plotly / Matplotlib
    charts throughout the application.

    Keys:
        primary, secondary, accent, success, warning, danger,
        info, bg_dark, bg_card, text_primary, text_secondary,
        gradient_start, gradient_mid, gradient_end
    """
    return {
        # Core brand
        "primary":        "#6C63FF",
        "secondary":      "#3F3D56",
        "accent":         "#00D2FF",
        # Semantic
        "success":        "#66BB6A",
        "warning":        "#FFA726",
        "danger":         "#FF4B4B",
        "info":           "#29B6F6",
        # Backgrounds
        "bg_dark":        "#0E1117",
        "bg_card":        "#1B1F2A",
        # Text
        "text_primary":   "#FAFAFA",
        "text_secondary": "#B0BEC5",
        # Gradients
        "gradient_start": "#6C63FF",
        "gradient_mid":   "#00D2FF",
        "gradient_end":   "#00E5A0",
    }
