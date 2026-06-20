"""
ATS Scoring Engine for AI Resume Analyzer Pro.

This module implements an Applicant Tracking System (ATS) scoring algorithm
that evaluates resumes across six weighted categories: skills match, education,
projects, certifications, keywords/action verbs, and experience.

Each category contributes to a total score out of 100, with detailed breakdown
and identification of strengths and weaknesses.
"""

import re
from models.nlp_engine import load_skills_db


# ============================================================================
# Category Labels (used for strength/weakness identification)
# ============================================================================

CATEGORY_LABELS = {
    "skills_match": "Skills Match",
    "education": "Education",
    "projects": "Projects",
    "certifications": "Certifications",
    "keywords": "Keywords & Action Verbs",
    "experience": "Experience",
}


# ============================================================================
# Individual Scoring Functions
# ============================================================================

def score_skills_match(skills_found, skills_db=None):
    """
    Scores the candidate's skills against the full skills taxonomy.

    Calculates a weighted score based on how many skills from the database
    the candidate possesses, using each skill's importance weight.

    Args:
        skills_found (list[str]): List of skill names found in the resume.
        skills_db (dict, optional): Skills database. Loaded automatically if None.

    Returns:
        dict: Score result with keys:
            - score (float): Achieved score (0-30)
            - max (int): Maximum possible score (30)
            - details (str): Human-readable description
    """
    max_score = 30

    if not skills_found:
        return {
            "score": 0.0,
            "max": max_score,
            "details": "No skills detected in the resume."
        }

    if skills_db is None:
        skills_db = load_skills_db()

    all_skills = skills_db.get("skills", [])
    if not all_skills:
        return {
            "score": 0.0,
            "max": max_score,
            "details": "Skills database is empty."
        }

    # Calculate weighted score
    found_lower = {s.lower() for s in skills_found}
    total_weight = 0
    matched_weight = 0

    for skill_entry in all_skills:
        weight = skill_entry.get("weight", 1)
        total_weight += weight
        if skill_entry.get("name", "").lower() in found_lower:
            matched_weight += weight

    # Calculate proportional score
    if total_weight > 0:
        score = (matched_weight / total_weight) * max_score
    else:
        score = 0.0

    score = round(min(score, max_score), 1)
    skill_count = len(skills_found)

    details = (
        f"Matched {skill_count} skill(s) from the taxonomy. "
        f"Weighted coverage: {round((matched_weight / total_weight) * 100, 1)}% "
        f"of total skill importance."
    )

    return {"score": score, "max": max_score, "details": details}


def score_education(education_list):
    """
    Scores the candidate's educational qualifications.

    Awards points based on the highest degree found, ranging from
    Diploma (6 pts) to Ph.D (15 pts).

    Args:
        education_list (list[dict]): List of education entries, each with
            'degree', 'field', and 'institution' keys.

    Returns:
        dict: Score result with keys:
            - score (float): Achieved score (0-15)
            - max (int): Maximum possible score (15)
            - details (str): Human-readable description
    """
    max_score = 15

    if not education_list:
        return {
            "score": 0.0,
            "max": max_score,
            "details": "No education information detected."
        }

    # Degree hierarchy with scores
    degree_scores = {
        "ph.d": 15, "doctorate": 15,
        "m.tech": 12, "m.e.": 12, "m.sc": 12, "mba": 12, "mca": 12, "master": 12,
        "b.tech": 10, "b.e.": 10, "b.sc": 10, "b.com": 10, "bba": 10, "bca": 10, "bachelor": 10,
        "diploma": 6, "associate degree": 6, "associate": 6,
    }

    highest_score = 0
    highest_degree = "None"

    for edu in education_list:
        degree = edu.get("degree", "").strip()
        degree_lower = degree.lower()

        for key, score_val in degree_scores.items():
            if key in degree_lower:
                if score_val > highest_score:
                    highest_score = score_val
                    highest_degree = degree
                break

    score = float(min(highest_score, max_score))
    field_info = ""
    for edu in education_list:
        if edu.get("field"):
            field_info = f" in {edu['field']}"
            break

    if highest_score > 0:
        details = f"Highest degree: {highest_degree}{field_info}."
    else:
        details = "Education entries found but degree level could not be determined."
        score = 3.0  # Partial credit for having education section

    return {"score": score, "max": max_score, "details": details}


def score_projects(projects_list):
    """
    Scores based on the number of projects listed.

    More projects demonstrate practical application of skills and
    hands-on experience.

    Args:
        projects_list (list[str]): List of project titles.

    Returns:
        dict: Score result with keys:
            - score (float): Achieved score (0-15)
            - max (int): Maximum possible score (15)
            - details (str): Human-readable description
    """
    max_score = 15

    if not projects_list:
        return {
            "score": 0.0,
            "max": max_score,
            "details": "No projects found. Adding projects would significantly strengthen your resume."
        }

    count = len(projects_list)

    # Scoring tiers
    if count >= 4:
        score = 15.0
        quality = "Excellent"
    elif count == 3:
        score = 11.0
        quality = "Good"
    elif count == 2:
        score = 8.0
        quality = "Fair"
    else:  # count == 1
        score = 5.0
        quality = "Needs more"

    details = (
        f"{count} project(s) found. {quality} project portfolio. "
        f"{'Consider adding more projects to showcase your skills.' if count < 3 else 'Strong project section!'}"
    )

    return {"score": score, "max": max_score, "details": details}


def score_certifications(certs_list):
    """
    Scores based on the number of certifications listed.

    Certifications demonstrate commitment to professional development
    and validated expertise.

    Args:
        certs_list (list[str]): List of certification names.

    Returns:
        dict: Score result with keys:
            - score (float): Achieved score (0-10)
            - max (int): Maximum possible score (10)
            - details (str): Human-readable description
    """
    max_score = 10

    if not certs_list:
        return {
            "score": 0.0,
            "max": max_score,
            "details": "No certifications found. Industry certifications can boost your profile."
        }

    count = len(certs_list)

    if count >= 3:
        score = 10.0
        quality = "Excellent"
    elif count == 2:
        score = 7.0
        quality = "Good"
    else:  # count == 1
        score = 4.0
        quality = "Basic"

    cert_names = ", ".join(certs_list[:3])
    details = (
        f"{count} certification(s) found: {cert_names}{'...' if count > 3 else ''}. "
        f"{quality} certification profile."
    )

    return {"score": score, "max": max_score, "details": details}


def score_keywords(text):
    """
    Scores the resume's use of professional keywords and action verbs.

    Evaluates three sub-categories:
    - Action verbs (up to 6 pts): Strong, active language
    - Quantified achievements (up to 5 pts): Numbers and metrics
    - Professional keywords (up to 4 pts): Industry terminology

    Args:
        text (str): Full resume text.

    Returns:
        dict: Score result with keys:
            - score (float): Achieved score (0-15)
            - max (int): Maximum possible score (15)
            - details (str): Human-readable description
    """
    max_score = 15

    if not text:
        return {
            "score": 0.0,
            "max": max_score,
            "details": "No text available for keyword analysis."
        }

    text_lower = text.lower()

    # --- Action Verbs (up to 6 points) ---
    action_verbs = [
        'developed', 'implemented', 'designed', 'analyzed', 'managed',
        'optimized', 'built', 'created', 'led', 'improved',
        'increased', 'reduced', 'automated', 'deployed', 'trained',
        'architected', 'collaborated', 'delivered', 'executed', 'launched',
        'mentored', 'orchestrated', 'pioneered', 'resolved', 'streamlined'
    ]

    found_verbs = [verb for verb in action_verbs if re.search(r'\b' + verb + r'\b', text_lower)]
    verb_count = len(found_verbs)
    # Scale: 0=0, 1-2=2, 3-5=4, 6+=6
    if verb_count >= 6:
        verb_score = 6.0
    elif verb_count >= 3:
        verb_score = 4.0
    elif verb_count >= 1:
        verb_score = 2.0
    else:
        verb_score = 0.0

    # --- Quantified Achievements (up to 5 points) ---
    # Look for numbers with context: percentages, dollar amounts, counts
    quant_patterns = [
        r'\d+\s*%',           # Percentages
        r'\$\s*[\d,]+',       # Dollar amounts
        r'(?:increased|reduced|improved|grew|decreased)\s+(?:by\s+)?\d+',  # Metrics
        r'\d+\s*(?:users?|clients?|customers?|projects?|teams?|members?)',   # Counts
        r'(?:top|first|#?\s*1)\s*(?:in|out\s+of|among)',                    # Rankings
    ]

    quant_count = 0
    for pattern in quant_patterns:
        matches = re.findall(pattern, text_lower)
        quant_count += len(matches)

    # Scale: 0=0, 1-2=2, 3-4=3.5, 5+=5
    if quant_count >= 5:
        quant_score = 5.0
    elif quant_count >= 3:
        quant_score = 3.5
    elif quant_count >= 1:
        quant_score = 2.0
    else:
        quant_score = 0.0

    # --- Professional Keywords (up to 4 points) ---
    professional_keywords = [
        'team', 'collaboration', 'agile', 'scrum', 'deadline',
        'client', 'stakeholder', 'leadership', 'communication',
        'problem solving', 'critical thinking', 'time management',
        'project management', 'cross-functional', 'deliverables',
        'metrics', 'kpi', 'strategy', 'innovation', 'initiative'
    ]

    found_professional = [kw for kw in professional_keywords if kw in text_lower]
    prof_count = len(found_professional)

    # Scale: 0=0, 1-2=1.5, 3-4=3, 5+=4
    if prof_count >= 5:
        prof_score = 4.0
    elif prof_count >= 3:
        prof_score = 3.0
    elif prof_count >= 1:
        prof_score = 1.5
    else:
        prof_score = 0.0

    # Total
    total = round(min(verb_score + quant_score + prof_score, max_score), 1)

    # Build details string
    details_parts = []
    if found_verbs:
        details_parts.append(f"Action verbs: {', '.join(found_verbs[:5])}{'...' if len(found_verbs) > 5 else ''}")
    else:
        details_parts.append("No action verbs found")
    details_parts.append(f"Quantified achievements: {quant_count} found")
    if found_professional:
        details_parts.append(f"Professional keywords: {', '.join(found_professional[:5])}")
    else:
        details_parts.append("No professional keywords found")

    details = ". ".join(details_parts) + "."

    return {"score": total, "max": max_score, "details": details}


def score_experience(experience_list, experience_years):
    """
    Scores based on work experience entries and total years.

    Awards points based on years of experience and the presence of
    work history entries.

    Args:
        experience_list (list[dict]): List of experience entries with
            'title' and 'duration' keys.
        experience_years (float): Estimated total years of experience.

    Returns:
        dict: Score result with keys:
            - score (float): Achieved score (0-15)
            - max (int): Maximum possible score (15)
            - details (str): Human-readable description
    """
    max_score = 15

    has_entries = bool(experience_list)
    years = experience_years if experience_years else 0.0

    if years == 0.0 and not has_entries:
        return {
            "score": 0.0,
            "max": max_score,
            "details": "No work experience detected. Internships and part-time work count!"
        }

    # Check for internship mentions in titles
    has_internship = any(
        'intern' in exp.get('title', '').lower()
        for exp in (experience_list or [])
    )

    # Scoring based on years
    if years >= 2:
        score = 15.0
        level = "Strong"
    elif years >= 1:
        score = 10.0
        level = "Good"
    elif years > 0 or has_internship:
        score = 5.0
        level = "Entry-level"
    elif has_entries:
        # Has entries but no quantified years
        score = 3.0
        level = "Minimal"
    else:
        score = 0.0
        level = "None"

    # Bonus for having multiple positions (max +2, but don't exceed cap)
    if has_entries and len(experience_list) > 1:
        position_bonus = min(len(experience_list) - 1, 2)
        score = min(score + position_bonus, max_score)

    entry_count = len(experience_list) if experience_list else 0
    titles = ", ".join(
        exp.get("title", "Unknown") for exp in (experience_list or [])[:3]
    )

    details = (
        f"{level} experience profile. "
        f"{years} year(s) estimated, {entry_count} position(s) found"
        f"{': ' + titles if titles else ''}."
    )

    return {"score": round(score, 1), "max": max_score, "details": details}


# ============================================================================
# Main Scoring Function
# ============================================================================

def calculate_ats_score(parsed_resume, skills_db=None):
    """
    Calculates the complete ATS score for a parsed resume.

    This is the main function that orchestrates all scoring categories,
    sums the total score, and identifies strengths and weaknesses.

    Args:
        parsed_resume (dict): Parsed resume dictionary from nlp_engine.parse_resume.
        skills_db (dict, optional): Skills database. Loaded automatically if None.

    Returns:
        dict: ATS result dictionary with keys:
            - total_score (float): Overall score 0-100
            - breakdown (dict): Per-category score details
            - strengths (list[str]): Categories scoring >70% of max
            - weaknesses (list[str]): Categories scoring <40% of max
    """
    if skills_db is None:
        skills_db = load_skills_db()

    # Extract data from parsed resume
    skills_found = parsed_resume.get("skills", [])
    education_list = parsed_resume.get("education", [])
    projects_list = parsed_resume.get("projects", [])
    certs_list = parsed_resume.get("certifications", [])
    text = parsed_resume.get("text", "")
    experience_list = parsed_resume.get("experience", [])
    experience_years = parsed_resume.get("experience_years", 0.0)

    # Calculate each category score
    skills_result = score_skills_match(skills_found, skills_db=skills_db)
    education_result = score_education(education_list)
    projects_result = score_projects(projects_list)
    certs_result = score_certifications(certs_list)
    keywords_result = score_keywords(text)
    experience_result = score_experience(experience_list, experience_years)

    # Build breakdown dictionary
    breakdown = {
        "skills_match": skills_result,
        "education": education_result,
        "projects": projects_result,
        "certifications": certs_result,
        "keywords": keywords_result,
        "experience": experience_result,
    }

    # Calculate total score
    total_score = round(
        skills_result["score"]
        + education_result["score"]
        + projects_result["score"]
        + certs_result["score"]
        + keywords_result["score"]
        + experience_result["score"],
        1
    )

    # Identify strengths (>70% of category max) and weaknesses (<40% of category max)
    strengths = []
    weaknesses = []

    for category_key, result in breakdown.items():
        category_label = CATEGORY_LABELS.get(category_key, category_key.replace("_", " ").title())
        score_ratio = result["score"] / result["max"] if result["max"] > 0 else 0

        if score_ratio > 0.7:
            strengths.append(f"{category_label} ({result['score']}/{result['max']})")
        elif score_ratio < 0.4:
            weaknesses.append(f"{category_label} ({result['score']}/{result['max']})")

    return {
        "total_score": total_score,
        "breakdown": breakdown,
        "strengths": strengths,
        "weaknesses": weaknesses
    }


# ============================================================================
# Score Interpretation
# ============================================================================

def get_score_interpretation(total_score):
    """
    Returns a human-readable interpretation of the ATS score.

    Args:
        total_score (float): The total ATS score (0-100).

    Returns:
        str: Interpretation string with category and advice.
    """
    if total_score >= 80:
        return (
            "Excellent — Your resume is well-optimized for ATS systems. "
            "It demonstrates strong skills, experience, and professional presentation. "
            "Focus on tailoring it for specific roles to maximize impact."
        )
    elif total_score >= 60:
        return (
            "Good — Your resume has strong elements but could be improved in some areas. "
            "Review the weakness areas in the breakdown and consider adding more "
            "quantified achievements and relevant keywords."
        )
    elif total_score >= 40:
        return (
            "Average — Several areas need improvement for better ATS performance. "
            "Focus on adding more relevant skills, projects, and certifications. "
            "Use action verbs and quantify your achievements wherever possible."
        )
    else:
        return (
            "Needs Improvement — Significant enhancements are required to pass ATS filters. "
            "Start by ensuring all key sections (Skills, Projects, Education, Experience) "
            "are present and well-populated. Add relevant certifications and use "
            "industry-standard keywords throughout your resume."
        )
