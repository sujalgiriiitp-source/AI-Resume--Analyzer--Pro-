"""
NLP Engine for AI Resume Analyzer Pro.

This module provides the core Natural Language Processing capabilities for parsing
PDF resumes and extracting structured data including contact information, skills,
education, experience, projects, and certifications.

It serves as the foundational data extraction layer that all other models depend on.
"""

import os
import re
import json
from PyPDF2 import PdfReader


# ============================================================================
# Path & Data Loading Utilities
# ============================================================================

def get_project_root():
    """
    Returns the absolute path to the project root directory.

    Uses the location of this file (models/nlp_engine.py) to navigate
    one level up to the project root.

    Returns:
        str: Absolute path to the project root directory.
    """
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_skills_db():
    """
    Loads the skills database from data/skills_db.json.

    The skills database contains categorized skills with their keywords
    and importance weights used for skill extraction and scoring.

    Returns:
        dict: Skills database with 'categories' and 'skills' keys.
              Returns empty structure on file not found or parse error.
    """
    try:
        db_path = os.path.join(get_project_root(), "data", "skills_db.json")
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        print(f"[WARNING] Could not load skills_db.json: {e}")
        return {"categories": {}, "skills": []}


def load_internships_db():
    """
    Loads the internships database from data/internships_db.json.

    The internships database contains available internship positions with
    their required and nice-to-have skills for matching.

    Returns:
        dict: Internships database with 'internships' key.
              Returns empty structure on file not found or parse error.
    """
    try:
        db_path = os.path.join(get_project_root(), "data", "internships_db.json")
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        print(f"[WARNING] Could not load internships_db.json: {e}")
        return {"internships": []}


# ============================================================================
# Text Extraction & Cleaning
# ============================================================================

def extract_text_from_pdf(uploaded_file):
    """
    Extracts all text content from a PDF file.

    Args:
        uploaded_file: A Streamlit UploadedFile object or any file-like object
                       that PdfReader can read from.

    Returns:
        str: Concatenated text from all pages of the PDF.
             Returns empty string if extraction fails.
    """
    try:
        reader = PdfReader(uploaded_file)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as e:
        print(f"[ERROR] Failed to extract text from PDF: {e}")
        return ""


def clean_text(text):
    """
    Normalizes whitespace in text while preserving original casing.

    Collapses multiple spaces into single spaces and multiple newlines
    into double newlines. Strips leading/trailing whitespace.

    Args:
        text (str): Raw text to clean.

    Returns:
        str: Cleaned text with normalized whitespace.
    """
    if not text:
        return ""
    # Collapse multiple spaces into one
    text = re.sub(r'[ \t]+', ' ', text)
    # Collapse 3+ newlines into double newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip each line
    lines = [line.strip() for line in text.split('\n')]
    return '\n'.join(lines).strip()


# ============================================================================
# Contact Information Extraction
# ============================================================================

def extract_name(text):
    """
    Extracts the candidate's name from the resume text.

    Uses the common convention that the first non-empty line of a resume
    contains the candidate's name.

    Args:
        text (str): Full resume text.

    Returns:
        str: Extracted name, or 'Unknown' if text is empty.
    """
    if not text or not text.strip():
        return "Unknown"

    lines = text.strip().split('\n')
    for line in lines:
        stripped = line.strip()
        if stripped and len(stripped) > 1:
            # Remove any leading special characters or bullets
            cleaned = re.sub(r'^[\u2022\-\*\|\>]+\s*', '', stripped)
            if cleaned and len(cleaned) > 1:
                # Limit to reasonable name length (max 60 chars)
                return cleaned[:60]

    return "Unknown"


def extract_contact_info(text):
    """
    Extracts email, phone number, and LinkedIn profile from resume text.

    Uses regex patterns to identify contact information commonly found
    in resumes.

    Args:
        text (str): Full resume text.

    Returns:
        dict: Dictionary with keys 'email', 'phone', 'linkedin'.
              Values are strings (empty string if not found).
    """
    result = {"email": "", "phone": "", "linkedin": ""}

    if not text:
        return result

    # Extract email
    email_pattern = r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, text)
    if email_match:
        result["email"] = email_match.group(0)

    # Extract phone number
    phone_pattern = r'[\+]?[\d\s\-\(\)]{10,15}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        phone_candidate = phone_match.group(0).strip()
        # Verify it contains at least 10 digits
        digits_only = re.sub(r'\D', '', phone_candidate)
        if len(digits_only) >= 10:
            result["phone"] = phone_candidate

    # Extract LinkedIn
    linkedin_pattern = r'linkedin\.com/in/[a-zA-Z0-9_\-]+'
    linkedin_match = re.search(linkedin_pattern, text, re.IGNORECASE)
    if linkedin_match:
        result["linkedin"] = linkedin_match.group(0)

    return result


# ============================================================================
# Skills Extraction
# ============================================================================

def extract_skills(text, skills_db=None):
    """
    Identifies technical and professional skills mentioned in the resume.

    Matches skills from the skills database by checking if any of a skill's
    keywords appear in the text using word-boundary regex matching.

    Args:
        text (str): Full resume text.
        skills_db (dict, optional): Skills database. Loaded automatically if None.

    Returns:
        list: List of unique matched skill names (strings).
    """
    if not text:
        return []

    if skills_db is None:
        skills_db = load_skills_db()

    text_lower = text.lower()
    matched_skills = set()

    for skill_entry in skills_db.get("skills", []):
        skill_name = skill_entry.get("name", "")
        keywords = skill_entry.get("keywords", [])

        # Also check the skill name itself as a keyword
        all_keywords = keywords + [skill_name.lower()]

        for keyword in all_keywords:
            keyword_lower = keyword.lower().strip()
            if not keyword_lower:
                continue
            try:
                # Use word boundary matching for accurate detection
                pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                if re.search(pattern, text_lower):
                    matched_skills.add(skill_name)
                    break  # No need to check other keywords for this skill
            except re.error:
                # If regex fails, fall back to simple substring match
                if keyword_lower in text_lower:
                    matched_skills.add(skill_name)
                    break

    return sorted(list(matched_skills))


# ============================================================================
# Education Extraction
# ============================================================================

def extract_education(text):
    """
    Extracts educational qualifications from the resume text.

    Identifies degrees (B.Tech, M.Sc, PhD, etc.), fields of study,
    and institution names using regex pattern matching.

    Args:
        text (str): Full resume text.

    Returns:
        list: List of dicts with keys 'degree', 'field', 'institution'.
              Returns empty list if no education found.
    """
    if not text:
        return []

    education_list = []
    text_lower = text.lower()

    # Degree patterns with their canonical names
    degree_patterns = [
        # Doctoral
        (r'ph\.?\s*d\.?', 'Ph.D'),
        (r'doctorate', 'Doctorate'),
        # Masters
        (r'm\.?\s*tech\.?', 'M.Tech'),
        (r'm\.?\s*e\.(?!\w)', 'M.E.'),
        (r'm\.?\s*sc\.?', 'M.Sc'),
        (r'm\.?\s*b\.?\s*a\.?(?:\s|$|,)', 'MBA'),
        (r'm\.?\s*c\.?\s*a\.?(?:\s|$|,)', 'MCA'),
        (r'master(?:s|\'s)?\s+(?:of|in)', 'Master'),
        # Bachelors
        (r'b\.?\s*tech\.?', 'B.Tech'),
        (r'b\.?\s*e\.(?!\w)', 'B.E.'),
        (r'b\.?\s*sc\.?', 'B.Sc'),
        (r'b\.?\s*com\.?', 'B.Com'),
        (r'b\.?\s*b\.?\s*a\.?(?:\s|$|,)', 'BBA'),
        (r'b\.?\s*c\.?\s*a\.?(?:\s|$|,)', 'BCA'),
        (r'bachelor(?:s|\'s)?\s+(?:of|in)', 'Bachelor'),
        # Diploma
        (r'diploma', 'Diploma'),
        (r'associate(?:s|\'s)?\s+degree', 'Associate Degree'),
    ]

    # Fields of study
    field_patterns = [
        r'computer\s+science(?:\s+(?:and|&)\s+engineering)?',
        r'information\s+technology',
        r'electrical\s+engineering',
        r'electronics?\s+(?:and|&)?\s*communications?\s+engineering',
        r'mechanical\s+engineering',
        r'civil\s+engineering',
        r'chemical\s+engineering',
        r'data\s+science',
        r'artificial\s+intelligence',
        r'machine\s+learning',
        r'software\s+engineering',
        r'mathematics',
        r'statistics',
        r'physics',
        r'chemistry',
        r'biology',
        r'commerce',
        r'business\s+administration',
        r'economics',
        r'finance',
        r'marketing',
    ]

    found_degrees = set()

    for pattern, degree_name in degree_patterns:
        matches = list(re.finditer(pattern, text_lower))
        for match in matches:
            if degree_name in found_degrees:
                continue
            found_degrees.add(degree_name)

            # Try to extract field of study from surrounding text
            # Look at text after the degree mention (within ~100 chars)
            surrounding = text_lower[match.start():min(match.end() + 150, len(text_lower))]
            field = ""
            for fp in field_patterns:
                field_match = re.search(fp, surrounding)
                if field_match:
                    field = field_match.group(0).strip().title()
                    break

            # Try to extract institution name
            # Look for common patterns: "from <Institution>", "at <Institution>"
            # Or look for lines near the degree mention containing university/college/institute
            institution = ""
            context_start = max(0, match.start() - 50)
            context_end = min(len(text), match.end() + 200)
            context = text[context_start:context_end]

            inst_patterns = [
                r'(?:university|college|institute|school|academy)\s+(?:of\s+)?[\w\s,]+',
                r'(?:IIT|NIT|IIIT|BITS|VIT|SRM|MIT|AIIMS)\s*[\w\s,]*',
            ]
            for ip in inst_patterns:
                inst_match = re.search(ip, context, re.IGNORECASE)
                if inst_match:
                    institution = inst_match.group(0).strip()[:80]  # Limit length
                    break

            education_list.append({
                "degree": degree_name,
                "field": field,
                "institution": institution
            })

    return education_list


# ============================================================================
# Experience Extraction
# ============================================================================

def extract_experience(text):
    """
    Extracts work experience details from the resume text.

    Identifies job titles, durations, and calculates total years of experience
    from patterns like 'X years', 'X months', and common job title keywords.

    Args:
        text (str): Full resume text.

    Returns:
        tuple: (experience_list, total_years) where:
            - experience_list: list of dicts with 'title' and 'duration' keys
            - total_years: float estimate of total experience in years
    """
    if not text:
        return [], 0.0

    text_lower = text.lower()
    experience_list = []
    total_years = 0.0

    # Extract duration patterns
    year_patterns = re.findall(r'(\d+(?:\.\d+)?)\s*(?:\+\s*)?year', text_lower)
    month_patterns = re.findall(r'(\d+(?:\.\d+)?)\s*(?:\+\s*)?month', text_lower)

    # Calculate total years from explicit mentions
    for y in year_patterns:
        try:
            total_years = max(total_years, float(y))
        except ValueError:
            pass

    for m in month_patterns:
        try:
            month_years = float(m) / 12.0
            total_years = max(total_years, month_years)
        except ValueError:
            pass

    # Job title patterns
    title_keywords = [
        r'(?:software|web|full[\s\-]?stack|front[\s\-]?end|back[\s\-]?end|mobile)\s+developer',
        r'(?:software|application|systems?)\s+engineer',
        r'(?:data|business|financial|research|quality)\s+analyst',
        r'(?:data|ml|machine\s+learning|ai)\s+(?:scientist|engineer)',
        r'(?:project|product|program|operations?)\s+manager',
        r'(?:software|engineering|data|research|marketing|hr|finance)\s+intern',
        r'intern(?:ship)?',
        r'developer',
        r'engineer',
        r'analyst',
        r'designer',
        r'consultant',
        r'coordinator',
        r'specialist',
        r'associate',
        r'trainee',
        r'assistant',
        r'executive',
        r'architect',
        r'administrator',
        r'lead',
        r'manager',
    ]

    found_titles = set()
    for tp in title_keywords:
        matches = re.finditer(tp, text_lower)
        for match in matches:
            title = match.group(0).strip().title()
            if title not in found_titles and len(title) > 3:
                found_titles.add(title)

                # Try to find associated duration nearby
                context_start = max(0, match.start() - 100)
                context_end = min(len(text_lower), match.end() + 100)
                context = text_lower[context_start:context_end]

                duration = ""
                dur_match = re.search(
                    r'(\d+\s*(?:\+\s*)?(?:year|month|week)s?(?:\s*(?:and|&|-)\s*\d+\s*(?:month|week)s?)?)',
                    context
                )
                if dur_match:
                    duration = dur_match.group(0).strip()

                # Also check for date range patterns (Jan 2022 - Present)
                if not duration:
                    date_match = re.search(
                        r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s*\d{2,4}\s*[-–]\s*(?:present|current|(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s*\d{2,4})',
                        context,
                        re.IGNORECASE
                    )
                    if date_match:
                        duration = date_match.group(0).strip()

                experience_list.append({
                    "title": title,
                    "duration": duration
                })

    # If we found experience entries but no explicit years, estimate
    if experience_list and total_years == 0.0:
        # Estimate based on number of positions (rough heuristic)
        total_years = min(len(experience_list) * 0.5, 3.0)

    # Deduplicate by title
    seen_titles = set()
    unique_experience = []
    for exp in experience_list:
        title_key = exp["title"].lower()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_experience.append(exp)

    return unique_experience, round(total_years, 1)


# ============================================================================
# Projects Extraction
# ============================================================================

def extract_projects(text):
    """
    Extracts project titles from the resume text.

    Looks for a 'Projects' section header and extracts bullet points,
    numbered items, or capitalized lines that follow it.

    Args:
        text (str): Full resume text.

    Returns:
        list: List of project title strings.
              Returns empty list if no projects section found.
    """
    if not text:
        return []

    projects = []

    # Find the projects section
    # Look for "Projects" or "Project" or "Academic Projects" or "Personal Projects"
    section_pattern = r'(?:^|\n)\s*(?:academic\s+|personal\s+|major\s+|key\s+)?projects?\s*(?:completed|done|worked\s+on)?\s*[:\-]?\s*\n'
    section_match = re.search(section_pattern, text, re.IGNORECASE | re.MULTILINE)

    if section_match:
        # Get text after the section header until the next section
        section_start = section_match.end()

        # Find the next section header
        next_section = re.search(
            r'\n\s*(?:education|experience|skills|certification|achievement|award|hobbies|interests|references|objective|summary|languages|publications)\s*[:\-]?\s*\n',
            text[section_start:],
            re.IGNORECASE
        )
        section_end = section_start + next_section.start() if next_section else len(text)
        section_text = text[section_start:section_end]

        # Extract project entries
        lines = section_text.split('\n')
        for line in lines:
            stripped = line.strip()
            if not stripped or len(stripped) < 3:
                continue

            # Match bullet points, numbered items, or bold/capitalized titles
            # Remove bullet markers
            cleaned = re.sub(r'^[\u2022\-\*\|\>\d\.]+\s*', '', stripped)
            cleaned = cleaned.strip()

            if not cleaned or len(cleaned) < 3:
                continue

            # Heuristic: project titles are usually shorter and may be followed by descriptions
            # Take lines that look like titles (reasonably short, not a full sentence)
            if len(cleaned) <= 120:
                # Skip lines that look like descriptions (start with common description words)
                desc_starters = ['used', 'utilized', 'implemented', 'using', 'built', 'the', 'this', 'a ', 'an ']
                is_description = any(cleaned.lower().startswith(s) for s in desc_starters)

                if not is_description:
                    # Clean up: take only the title part (before any description separator)
                    title = re.split(r'[\-–—:|]', cleaned)[0].strip()
                    if title and len(title) >= 3 and title not in projects:
                        projects.append(title[:100])  # Limit title length

    # If no section found, try to find project-like patterns anywhere
    if not projects:
        # Look for patterns like "Project: <title>" or "Project Name: <title>"
        project_mentions = re.findall(
            r'(?:project\s*(?:title|name)?\s*[:\-]\s*)([^\n]{3,80})',
            text,
            re.IGNORECASE
        )
        for pm in project_mentions:
            title = pm.strip()
            if title and title not in projects:
                projects.append(title)

    return projects[:10]  # Limit to 10 projects max


# ============================================================================
# Certifications Extraction
# ============================================================================

def extract_certifications(text):
    """
    Extracts certifications from the resume text.

    Looks for a 'Certifications' section header and also detects known
    certification names and platforms (AWS, Google, Coursera, etc.).

    Args:
        text (str): Full resume text.

    Returns:
        list: List of certification name strings.
              Returns empty list if no certifications found.
    """
    if not text:
        return []

    certifications = []
    text_lower = text.lower()

    # Known certification patterns
    known_certs = [
        (r'aws\s+certified\s+[\w\s\-]+', 'AWS Certified'),
        (r'google\s+(?:cloud|analytics|data)\s+[\w\s\-]+(?:certificate|certified|certification)?', 'Google Certification'),
        (r'microsoft\s+(?:azure|certified)\s+[\w\s\-]+', 'Microsoft Certification'),
        (r'ibm\s+(?:data\s+science|ai|machine\s+learning)\s*[\w\s\-]*(?:certificate|certification)?', 'IBM Certification'),
        (r'cisco\s+(?:ccna|ccnp|ccie)\s*[\w\s\-]*', 'Cisco Certification'),
        (r'comptia\s+(?:a\+|network\+|security\+|cloud\+)\s*[\w\s\-]*', 'CompTIA Certification'),
        (r'pmp\s+(?:certification|certified)?', 'PMP'),
        (r'(?:certified\s+)?scrum\s+master', 'Scrum Master'),
        (r'six\s+sigma\s+[\w\s]+(?:belt)?', 'Six Sigma'),
        (r'hackerrank\s+[\w\s\-]+(?:certificate|certification)?', 'HackerRank'),
        (r'coursera\s+[\w\s\-]+(?:certificate|specialization)?', 'Coursera Certificate'),
        (r'udemy\s+[\w\s\-]+(?:certificate|course)?', 'Udemy Certificate'),
        (r'edx\s+[\w\s\-]+(?:certificate)?', 'edX Certificate'),
        (r'nptel\s+[\w\s\-]+(?:certificate|certification)?', 'NPTEL Certificate'),
        (r'linkedin\s+learning\s+[\w\s\-]+', 'LinkedIn Learning'),
        (r'tensorflow\s+(?:developer\s+)?certif(?:icate|ication|ied)', 'TensorFlow Certification'),
        (r'(?:deep\s+learning|machine\s+learning)\s+specialization', 'ML Specialization'),
    ]

    found_certs = set()

    # Check for known cert patterns
    for pattern, cert_name in known_certs:
        match = re.search(pattern, text_lower)
        if match:
            # Use the actual text found for more specificity
            actual_text = text[match.start():match.end()].strip()
            if actual_text not in found_certs:
                found_certs.add(actual_text)
                certifications.append(actual_text)

    # Find certifications section and extract entries
    section_pattern = r'(?:^|\n)\s*certific(?:ation|ate)s?\s*[:\-]?\s*\n'
    section_match = re.search(section_pattern, text, re.IGNORECASE | re.MULTILINE)

    if section_match:
        section_start = section_match.end()

        # Find the next section header
        next_section = re.search(
            r'\n\s*(?:education|experience|skills|projects?|achievement|award|hobbies|interests|references|objective|summary)\s*[:\-]?\s*\n',
            text[section_start:],
            re.IGNORECASE
        )
        section_end = section_start + next_section.start() if next_section else len(text)
        section_text = text[section_start:section_end]

        lines = section_text.split('\n')
        for line in lines:
            stripped = line.strip()
            if not stripped or len(stripped) < 3:
                continue
            # Remove bullet markers
            cleaned = re.sub(r'^[\u2022\-\*\|\>\d\.]+\s*', '', stripped).strip()
            if cleaned and len(cleaned) >= 3 and cleaned not in found_certs:
                found_certs.add(cleaned)
                certifications.append(cleaned[:120])

    return certifications[:15]  # Limit to 15 certifications max


# ============================================================================
# Section Detection
# ============================================================================

def detect_sections(text):
    """
    Detects which standard resume sections are present in the text.

    Checks for common section headers like Education, Experience, Projects,
    Skills, Certifications, etc.

    Args:
        text (str): Full resume text.

    Returns:
        list: List of found section names (lowercase strings).
    """
    if not text:
        return []

    text_lower = text.lower()
    found_sections = []

    # Section headers to look for (with variations)
    sections = {
        "education": [r'education', r'academic\s+background', r'qualifications?'],
        "experience": [r'(?:work\s+)?experience', r'employment\s+history', r'work\s+history', r'professional\s+experience'],
        "projects": [r'projects?', r'academic\s+projects?', r'personal\s+projects?'],
        "skills": [r'(?:technical\s+)?skills?', r'core\s+competenc(?:ies|y)', r'technologies'],
        "certifications": [r'certific(?:ation|ate)s?', r'licenses?\s+(?:and|&)\s+certific(?:ation|ate)s?'],
        "objective": [r'(?:career\s+)?objective', r'career\s+goal'],
        "summary": [r'(?:professional\s+|executive\s+)?summary', r'profile', r'about\s+me'],
        "achievements": [r'achievements?', r'accomplishments?', r'honors?'],
        "hobbies": [r'hobbies', r'interests?', r'extracurricular'],
        "languages": [r'languages?'],
        "references": [r'references?'],
        "awards": [r'awards?', r'recognitions?'],
        "publications": [r'publications?', r'research\s+papers?'],
    }

    for section_name, patterns in sections.items():
        for pattern in patterns:
            # Look for the pattern as a section header (typically on its own line)
            header_pattern = r'(?:^|\n)\s*' + pattern + r'\s*[:\-]?\s*(?:\n|$)'
            if re.search(header_pattern, text_lower, re.MULTILINE):
                found_sections.append(section_name)
                break

    return found_sections


# ============================================================================
# Main Parse Function
# ============================================================================

def parse_resume(uploaded_file):
    """
    Main resume parsing function — the primary interface for other modules.

    Extracts text from a PDF file and runs all extraction functions to produce
    a comprehensive structured representation of the resume.

    Args:
        uploaded_file: A Streamlit UploadedFile object (PDF file).

    Returns:
        dict: Parsed resume dictionary with keys:
            - name (str): Candidate's name
            - email (str): Email address
            - phone (str): Phone number
            - linkedin (str): LinkedIn profile URL
            - text (str): Full cleaned text
            - skills (list[str]): Matched skill names
            - education (list[dict]): Education entries
            - experience (list[dict]): Experience entries
            - projects (list[str]): Project titles
            - certifications (list[str]): Certification names
            - experience_years (float): Total experience in years
            - word_count (int): Total word count
            - sections_found (list[str]): Detected section names
    """
    # Default empty result
    default_result = {
        "name": "Unknown",
        "email": "",
        "phone": "",
        "linkedin": "",
        "text": "",
        "skills": [],
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "experience_years": 0.0,
        "word_count": 0,
        "sections_found": []
    }

    # Step 1: Extract raw text from PDF
    raw_text = extract_text_from_pdf(uploaded_file)
    if not raw_text or not raw_text.strip():
        return default_result

    # Step 2: Clean the text
    cleaned_text = clean_text(raw_text)

    # Step 3: Load skills database once for reuse
    skills_db = load_skills_db()

    # Step 4: Extract all components
    name = extract_name(cleaned_text)
    contact_info = extract_contact_info(cleaned_text)
    skills = extract_skills(cleaned_text, skills_db=skills_db)
    education = extract_education(cleaned_text)
    experience_list, experience_years = extract_experience(cleaned_text)
    projects = extract_projects(cleaned_text)
    certifications = extract_certifications(cleaned_text)
    sections = detect_sections(cleaned_text)

    # Step 5: Calculate word count
    word_count = len(cleaned_text.split())

    # Step 6: Assemble the parsed resume dictionary
    parsed_resume = {
        "name": name,
        "email": contact_info.get("email", ""),
        "phone": contact_info.get("phone", ""),
        "linkedin": contact_info.get("linkedin", ""),
        "text": cleaned_text,
        "skills": skills,
        "education": education,
        "experience": experience_list,
        "projects": projects,
        "certifications": certifications,
        "experience_years": experience_years,
        "word_count": word_count,
        "sections_found": sections
    }

    return parsed_resume


# ============================================================================
# Skill Analysis Utilities
# ============================================================================

# 14 core skills that are considered essential for data-related roles
CORE_SKILLS = [
    "Python", "SQL", "Pandas", "NumPy", "Power BI", "Tableau",
    "Excel", "Machine Learning", "Data Analytics", "Statistics",
    "Git", "GitHub", "Streamlit", "Flask"
]


def get_missing_skills(found_skills, skills_db=None):
    """
    Identifies which core skills are missing from the candidate's profile.

    Compares found skills against the 14 core skills essential for
    data-related roles.

    Args:
        found_skills (list[str]): List of skill names found in the resume.
        skills_db (dict, optional): Skills database (unused but kept for API consistency).

    Returns:
        list: List of core skill names not found in the resume.
    """
    if not found_skills:
        return list(CORE_SKILLS)

    # Case-insensitive comparison
    found_lower = {s.lower() for s in found_skills}
    missing = [skill for skill in CORE_SKILLS if skill.lower() not in found_lower]

    return missing


def get_skills_by_category(found_skills, skills_db=None):
    """
    Groups the candidate's found skills by their category.

    Uses the skills database to look up each skill's category and
    organizes them into a dictionary.

    Args:
        found_skills (list[str]): List of skill names found in the resume.
        skills_db (dict, optional): Skills database. Loaded automatically if None.

    Returns:
        dict: Dictionary where keys are category names and values are
              lists of skill names belonging to that category.
    """
    if not found_skills:
        return {}

    if skills_db is None:
        skills_db = load_skills_db()

    # Build a lookup: skill name (lowercase) -> category
    skill_category_map = {}
    for skill_entry in skills_db.get("skills", []):
        name = skill_entry.get("name", "")
        category = skill_entry.get("category", "Other")
        skill_category_map[name.lower()] = category

    # Group found skills by category
    categorized = {}
    for skill in found_skills:
        category = skill_category_map.get(skill.lower(), "Other")
        if category not in categorized:
            categorized[category] = []
        categorized[category].append(skill)

    return categorized
