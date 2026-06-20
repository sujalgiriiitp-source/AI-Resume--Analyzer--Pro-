"""
reports/pdf_report.py — Professional PDF Report Generator
==========================================================
Uses the **fpdf2** library to produce a polished, multi-section PDF
report summarising a student's ATS analysis results.  The generated
document is returned as raw bytes (via ``BytesIO``) so it can be
streamed directly to Streamlit's download button or saved to disk.
"""

import io
from datetime import datetime
from typing import Any, Dict, List, Optional

from fpdf import FPDF


# ---------------------------------------------------------------------------
# Custom PDF class with header / footer
# ---------------------------------------------------------------------------

class _ResumePDF(FPDF):
    """Internal FPDF subclass that draws a branded header and page footer."""

    def __init__(self, student_name: str, **kwargs):
        super().__init__(**kwargs)
        self.student_name = student_name

    # ── Header ─────────────────────────────────────────────────────────
    def header(self):
        # Brand bar — gradient-like solid colour
        self.set_fill_color(108, 99, 255)  # #6C63FF
        self.rect(0, 0, 210, 28, "F")

        # Logo text
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 5)
        self.cell(0, 10, "AI Resume Analyzer Pro", align="L")

        # Subtitle
        self.set_font("Helvetica", "", 10)
        self.set_xy(10, 16)
        self.cell(0, 6, "Professional ATS Analysis Report", align="L")

        self.ln(22)

    # ── Footer ─────────────────────────────────────────────────────────
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(160, 160, 160)
        report_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        self.cell(0, 10, f"Generated on {report_date}", align="L")
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="R")


# ---------------------------------------------------------------------------
# Section-drawing helpers (private)
# ---------------------------------------------------------------------------

def _section_title(pdf: FPDF, title: str) -> None:
    """Draw a coloured section heading with an underline accent."""
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(108, 99, 255)
    pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
    # Accent underline
    pdf.set_draw_color(108, 99, 255)
    pdf.set_line_width(0.6)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)


def _body_text(pdf: FPDF, text: str, bold: bool = False) -> None:
    """Write a line of body text in dark grey."""
    style = "B" if bold else ""
    pdf.set_font("Helvetica", style, 11)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 7, text)


def _key_value(pdf: FPDF, key: str, value: str) -> None:
    """Render a bold key followed by a regular value on one line."""
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(50, 50, 50)
    key_width = pdf.get_string_width(key + ": ") + 2
    pdf.cell(key_width, 7, f"{key}: ")
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, str(value), new_x="LMARGIN", new_y="NEXT")


def _score_to_grade(score: float) -> str:
    """Map score to letter grade (mirrors utils/helpers.py)."""
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
    return "F"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_pdf_report(
    student_name: str,
    email: str,
    ats_data: Dict[str, Any],
    skills_found: List[str],
    missing_skills: List[str],
    internship_matches: List[Dict[str, Any]],
    suggestions: List[str],
) -> bytes:
    """
    Generate a professional multi-page PDF report.

    Parameters
    ----------
    student_name : str
        Full name of the student.
    email : str
        Student email address.
    ats_data : dict
        Must include ``"overall_score"`` (float 0-100).  May also include
        sub-score keys such as ``"skills_score"``, ``"format_score"``,
        ``"experience_score"``, ``"education_score"`` — each 0-100.
    skills_found : list[str]
        Skills detected in the resume.
    missing_skills : list[str]
        Recommended skills the resume is currently lacking.
    internship_matches : list[dict]
        Each dict should contain ``"title"``, ``"match_percentage"``,
        and optionally ``"category"`` and ``"description"``.
    suggestions : list[str]
        Actionable improvement recommendations.

    Returns
    -------
    bytes
        Raw PDF content suitable for streaming or writing to a file.
    """

    pdf = _ResumePDF(student_name=student_name, orientation="P", unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    overall_score = ats_data.get("overall_score", 0)
    grade = _score_to_grade(overall_score)
    report_date = datetime.now().strftime("%B %d, %Y")

    # ── 1. Student Information ─────────────────────────────────────────
    _section_title(pdf, "Student Information")
    _key_value(pdf, "Name", student_name)
    _key_value(pdf, "Email", email)
    _key_value(pdf, "Report Date", report_date)
    pdf.ln(6)

    # ── 2. ATS Score Summary ───────────────────────────────────────────
    _section_title(pdf, "ATS Score Summary")

    # Large score display
    pdf.set_font("Helvetica", "B", 36)
    if overall_score >= 75:
        pdf.set_text_color(102, 187, 106)   # green
    elif overall_score >= 50:
        pdf.set_text_color(255, 167, 38)    # orange
    else:
        pdf.set_text_color(255, 75, 75)     # red

    pdf.cell(50, 20, f"{overall_score:.0f}%")
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(108, 99, 255)
    pdf.cell(0, 20, f"Grade: {grade}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── 3. Score Breakdown Table ───────────────────────────────────────
    breakdown_keys = {
        "skills_score":     "Skills Match",
        "format_score":     "Resume Format",
        "experience_score": "Experience Relevance",
        "education_score":  "Education Alignment",
    }

    # Only show table if at least one sub-score is present
    sub_scores = {label: ats_data.get(key, None) for key, label in breakdown_keys.items()}
    available = {k: v for k, v in sub_scores.items() if v is not None}

    if available:
        _section_title(pdf, "Score Breakdown")

        # Table header
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_fill_color(108, 99, 255)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(95, 9, "Category", border=1, fill=True, align="C")
        pdf.cell(95, 9, "Score", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")

        # Table rows
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(50, 50, 50)
        fill = False
        for label, value in available.items():
            if fill:
                pdf.set_fill_color(240, 240, 255)
            else:
                pdf.set_fill_color(255, 255, 255)
            pdf.cell(95, 8, label, border=1, fill=True, align="L")
            pdf.cell(95, 8, f"{value:.1f}%", border=1, fill=True, align="C", new_x="LMARGIN", new_y="NEXT")
            fill = not fill

        pdf.ln(6)

    # ── 4. Skills Found ────────────────────────────────────────────────
    _section_title(pdf, f"Skills Found ({len(skills_found)})")
    if skills_found:
        skills_text = ", ".join(skills_found)
        _body_text(pdf, skills_text)
    else:
        _body_text(pdf, "No matching skills were detected in the resume.")
    pdf.ln(4)

    # ── 5. Missing / Recommended Skills ────────────────────────────────
    _section_title(pdf, f"Missing Skills ({len(missing_skills)})")
    if missing_skills:
        missing_text = ", ".join(missing_skills)
        _body_text(pdf, missing_text)
    else:
        _body_text(pdf, "Great job! No critical skill gaps were identified.")
    pdf.ln(4)

    # ── 6. Top Internship Matches ──────────────────────────────────────
    _section_title(pdf, "Top Internship Matches")
    if internship_matches:
        for idx, match in enumerate(internship_matches, start=1):
            title = match.get("title", "N/A")
            pct = match.get("match_percentage", 0)
            category = match.get("category", "")
            description = match.get("description", "")

            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(50, 50, 50)
            pdf.cell(0, 7, f"{idx}. {title}  —  {pct:.0f}% match", new_x="LMARGIN", new_y="NEXT")

            if category:
                pdf.set_font("Helvetica", "I", 10)
                pdf.set_text_color(120, 120, 120)
                pdf.cell(0, 6, f"   Category: {category}", new_x="LMARGIN", new_y="NEXT")

            if description:
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(80, 80, 80)
                pdf.multi_cell(0, 6, f"   {description}")

            pdf.ln(2)
    else:
        _body_text(pdf, "No internship matches found based on current skills.")
    pdf.ln(4)

    # ── 7. Improvement Suggestions ─────────────────────────────────────
    _section_title(pdf, "Improvement Suggestions")
    if suggestions:
        for idx, suggestion in enumerate(suggestions, start=1):
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(50, 50, 50)
            pdf.multi_cell(0, 7, f"{idx}. {suggestion}")
            pdf.ln(1)
    else:
        _body_text(pdf, "No additional suggestions at this time.")
    pdf.ln(6)

    # ── 8. Final footer note ───────────────────────────────────────────
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(160, 160, 160)
    pdf.cell(
        0, 8,
        "This report was auto-generated by AI Resume Analyzer Pro. "
        "Results are indicative and should be used as guidance only.",
        new_x="LMARGIN", new_y="NEXT",
    )

    # ── Serialise to bytes via BytesIO ─────────────────────────────────
    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.read()
