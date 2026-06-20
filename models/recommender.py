"""
Internship Recommendation Engine for AI Resume Analyzer Pro.

This module recommends internships based on skill matching between the candidate's
resume and available internship positions. It uses both direct skill comparison
and TF-IDF cosine similarity for robust matching.

The recommendation engine evaluates required and nice-to-have skills with
weighted scoring to produce ranked internship matches.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models.nlp_engine import load_internships_db, load_skills_db


# ============================================================================
# Skill Vector Construction
# ============================================================================

def build_skill_vector(skills_list, all_skills):
    """
    Creates a binary vector representing which skills a candidate possesses.

    Each position in the vector corresponds to a skill in the all_skills
    vocabulary, set to 1 if the candidate has that skill, 0 otherwise.

    Args:
        skills_list (list[str]): List of skill names the candidate has.
        all_skills (list[str]): Complete vocabulary of all possible skill names.

    Returns:
        numpy.ndarray: Binary vector of shape (len(all_skills),).
    """
    if not all_skills:
        return np.array([])

    vector = np.zeros(len(all_skills), dtype=np.float64)

    if not skills_list:
        return vector

    # Build lowercase lookup for case-insensitive matching
    skills_lower = {s.lower() for s in skills_list}

    for i, skill in enumerate(all_skills):
        if skill.lower() in skills_lower:
            vector[i] = 1.0

    return vector


# ============================================================================
# Match Percentage Calculation
# ============================================================================

def calculate_match_percentage(resume_skills, required_skills, nice_to_have=None):
    """
    Calculates a weighted match percentage between candidate skills and role requirements.

    Applies an 80/20 weighting: 80% for required skills match and 20% for
    nice-to-have skills match.

    Args:
        resume_skills (list[str]): Candidate's skills from resume.
        required_skills (list[str]): Skills required for the internship.
        nice_to_have (list[str], optional): Additional desirable skills.

    Returns:
        float: Match percentage from 0.0 to 100.0, rounded to 1 decimal.
    """
    if not required_skills:
        return 0.0

    # Case-insensitive skill matching
    resume_lower = {s.lower() for s in (resume_skills or [])}

    # Calculate required skills match ratio
    required_matched = sum(
        1 for skill in required_skills if skill.lower() in resume_lower
    )
    required_ratio = required_matched / len(required_skills)

    # Calculate nice-to-have match ratio
    if nice_to_have and len(nice_to_have) > 0:
        nice_matched = sum(
            1 for skill in nice_to_have if skill.lower() in resume_lower
        )
        nice_ratio = nice_matched / len(nice_to_have)
        # Weighted combination: 80% required + 20% nice-to-have
        overall = 0.8 * required_ratio + 0.2 * nice_ratio
    else:
        overall = required_ratio

    return round(overall * 100.0, 1)


# ============================================================================
# TF-IDF Enhanced Matching (Internal Helper)
# ============================================================================

def _compute_tfidf_similarity(resume_text, internship_descriptions):
    """
    Computes TF-IDF cosine similarity between resume text and internship descriptions.

    This provides an additional signal beyond direct skill matching,
    capturing semantic relevance through text similarity.

    Args:
        resume_text (str): Full resume text.
        internship_descriptions (list[str]): List of internship description texts.

    Returns:
        numpy.ndarray: Array of similarity scores, one per internship.
    """
    if not resume_text or not internship_descriptions:
        return np.zeros(len(internship_descriptions) if internship_descriptions else 0)

    try:
        # Combine resume with all descriptions for TF-IDF fitting
        all_documents = [resume_text] + internship_descriptions

        vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2)
        )
        tfidf_matrix = vectorizer.fit_transform(all_documents)

        # Compute cosine similarity between resume (index 0) and each description
        resume_vector = tfidf_matrix[0:1]
        desc_vectors = tfidf_matrix[1:]

        similarities = cosine_similarity(resume_vector, desc_vectors).flatten()
        return similarities

    except Exception as e:
        print(f"[WARNING] TF-IDF similarity computation failed: {e}")
        return np.zeros(len(internship_descriptions))


# ============================================================================
# Main Recommendation Function
# ============================================================================

def recommend_internships(parsed_resume, internships_db=None):
    """
    Recommends internships based on the candidate's parsed resume.

    For each internship in the database, calculates a match percentage
    based on required and nice-to-have skills, identifies matched and
    missing skills, and returns results sorted by match percentage.

    Args:
        parsed_resume (dict): Parsed resume from nlp_engine.parse_resume.
        internships_db (dict, optional): Internships database. Loaded if None.

    Returns:
        list[dict]: List of internship_match dicts sorted by match_percentage
            descending. Each dict contains:
            - title (str): Internship title
            - match_percentage (float): 0-100 match score
            - required_skills (list[str]): Skills required
            - matched_skills (list[str]): Skills candidate has
            - missing_skills (list[str]): Skills candidate lacks
            - nice_to_have_matched (list[str]): Bonus skills matched
            - description (str): Internship description
            - category (str): Internship category
    """
    if internships_db is None:
        internships_db = load_internships_db()

    internships = internships_db.get("internships", [])
    if not internships:
        return []

    resume_skills = parsed_resume.get("skills", [])
    resume_text = parsed_resume.get("text", "")
    resume_lower = {s.lower() for s in resume_skills}

    # Compute TF-IDF similarities for additional context
    descriptions = [
        intern.get("description", "") for intern in internships
    ]
    tfidf_scores = _compute_tfidf_similarity(resume_text, descriptions)

    recommendations = []

    for idx, internship in enumerate(internships):
        title = internship.get("title", "Unknown Position")
        description = internship.get("description", "")
        required = internship.get("required_skills", [])
        nice_to_have = internship.get("nice_to_have", [])
        category = internship.get("category", "General")

        # Calculate skill-based match percentage
        skill_match = calculate_match_percentage(resume_skills, required, nice_to_have)

        # Blend with TF-IDF score (90% skill match + 10% text similarity)
        tfidf_score = tfidf_scores[idx] * 100 if idx < len(tfidf_scores) else 0
        blended_match = round(0.9 * skill_match + 0.1 * tfidf_score, 1)

        # Identify matched required skills (case-insensitive)
        matched_skills = [
            skill for skill in required
            if skill.lower() in resume_lower
        ]

        # Identify missing required skills
        missing_skills = [
            skill for skill in required
            if skill.lower() not in resume_lower
        ]

        # Identify matched nice-to-have skills
        nice_to_have_matched = [
            skill for skill in nice_to_have
            if skill.lower() in resume_lower
        ]

        recommendations.append({
            "title": title,
            "match_percentage": blended_match,
            "required_skills": required,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "nice_to_have_matched": nice_to_have_matched,
            "description": description,
            "category": category
        })

    # Sort by match percentage descending
    recommendations.sort(key=lambda x: x["match_percentage"], reverse=True)

    return recommendations


# ============================================================================
# Utility Functions
# ============================================================================

def get_best_match(recommendations):
    """
    Returns the top-ranked internship recommendation.

    Args:
        recommendations (list[dict]): List of internship_match dicts
            (assumed sorted by match_percentage descending).

    Returns:
        dict or None: The best matching internship, or None if list is empty.
    """
    if not recommendations:
        return None
    return recommendations[0]


def get_skill_importance_for_role(role_title, internships_db=None):
    """
    Returns the required and nice-to-have skills for a specific role.

    Performs case-insensitive partial matching on the role title.

    Args:
        role_title (str): The internship/role title to look up.
        internships_db (dict, optional): Internships database. Loaded if None.

    Returns:
        dict: Dictionary with keys:
            - required (list[str]): Required skills for the role
            - nice_to_have (list[str]): Nice-to-have skills for the role
    """
    if not role_title:
        return {"required": [], "nice_to_have": []}

    if internships_db is None:
        internships_db = load_internships_db()

    role_lower = role_title.lower()

    for internship in internships_db.get("internships", []):
        intern_title = internship.get("title", "").lower()

        # Case-insensitive partial match
        if role_lower in intern_title or intern_title in role_lower:
            return {
                "required": internship.get("required_skills", []),
                "nice_to_have": internship.get("nice_to_have", [])
            }

    # No match found
    return {"required": [], "nice_to_have": []}
