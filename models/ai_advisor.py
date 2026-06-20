"""
AI Career Advisor for AI Resume Analyzer Pro.

This module provides rule-based career coaching and advisory functionality.
It generates personalized improvement suggestions, skill roadmaps, project
recommendations, resume feedback, and career advice — all without external APIs.

Think of this module as a virtual career coach that analyzes resume data
and ATS scores to produce actionable, specific guidance for candidates.
"""

from models.nlp_engine import load_skills_db, get_missing_skills


# ============================================================================
# Skill Roadmap Definitions (per role)
# ============================================================================

# Complete learning roadmaps for each target role
ROLE_ROADMAPS = {
    "data analyst": [
        {
            "skill": "Python",
            "reason": "Foundation for data manipulation, automation, and analysis. Required in 90% of data analyst roles.",
            "resources": [
                "Coursera: Python for Everybody by University of Michigan",
                "Kaggle: Python Micro-Course (Free)",
                "Book: Automate the Boring Stuff with Python"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "SQL",
            "reason": "Essential for querying databases and extracting data. Used daily by data analysts.",
            "resources": [
                "Mode Analytics: SQL Tutorial (Free)",
                "Coursera: SQL for Data Science by UC Davis",
                "HackerRank: SQL Practice Problems"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "Excel",
            "reason": "Industry-standard tool for quick analysis, reporting, and data organization.",
            "resources": [
                "Coursera: Excel Skills for Business Specialization",
                "LinkedIn Learning: Excel Essential Training",
                "YouTube: ExcelJet Channel"
            ],
            "duration": "1 week"
        },
        {
            "skill": "Pandas",
            "reason": "Python's primary data manipulation library. Enables efficient data cleaning and transformation.",
            "resources": [
                "Kaggle: Pandas Micro-Course (Free)",
                "Real Python: Pandas Tutorials",
                "Book: Python for Data Analysis by Wes McKinney"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "NumPy",
            "reason": "Foundation for numerical computing in Python. Powers Pandas and scientific libraries.",
            "resources": [
                "NumPy Official Tutorial (Free)",
                "Coursera: Introduction to Data Science in Python",
                "YouTube: NumPy Tutorial by freeCodeCamp"
            ],
            "duration": "1 week"
        },
        {
            "skill": "Power BI",
            "reason": "Leading business intelligence tool for creating interactive dashboards and reports.",
            "resources": [
                "Microsoft Learn: Power BI Learning Path (Free)",
                "Coursera: Data Visualization with Power BI",
                "YouTube: Guy in a Cube Channel"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "Tableau",
            "reason": "Industry-leading data visualization platform. Highly valued by employers.",
            "resources": [
                "Tableau Public: Free Training Videos",
                "Coursera: Data Visualization with Tableau Specialization",
                "Udemy: Tableau A-Z: Hands-On Tableau Training"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "Statistics",
            "reason": "Core analytical skill for understanding distributions, testing hypotheses, and deriving insights.",
            "resources": [
                "Khan Academy: Statistics and Probability (Free)",
                "Coursera: Statistics with Python Specialization",
                "Book: Practical Statistics for Data Scientists"
            ],
            "duration": "3 weeks"
        },
        {
            "skill": "Data Analytics",
            "reason": "Brings together all skills into end-to-end analysis workflows and storytelling with data.",
            "resources": [
                "Google Data Analytics Professional Certificate (Coursera)",
                "Kaggle: Complete Data Analytics Projects",
                "DataCamp: Data Analyst with Python Track"
            ],
            "duration": "4 weeks"
        },
    ],

    "business analyst": [
        {
            "skill": "Excel",
            "reason": "The backbone of business analysis. Used for modeling, forecasting, and reporting.",
            "resources": [
                "Coursera: Excel Skills for Business Specialization",
                "Udemy: Microsoft Excel - From Beginner to Expert",
                "LinkedIn Learning: Excel for Business Analysts"
            ],
            "duration": "1 week"
        },
        {
            "skill": "SQL",
            "reason": "Essential for pulling data from business databases to support decision-making.",
            "resources": [
                "Coursera: SQL for Data Science by UC Davis",
                "W3Schools: SQL Tutorial (Free)",
                "LeetCode: SQL Practice Problems"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "Power BI",
            "reason": "Create dashboards and visual reports that communicate insights to stakeholders.",
            "resources": [
                "Microsoft Learn: Power BI Learning Path (Free)",
                "Udemy: Power BI for Business Intelligence",
                "YouTube: Pragmatic Works Power BI Tutorials"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "Tableau",
            "reason": "Alternative visualization tool preferred by many enterprises for data storytelling.",
            "resources": [
                "Tableau Public: Free Learning Resources",
                "Coursera: Data Visualization with Tableau",
                "YouTube: Tableau Tim Channel"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "Statistics",
            "reason": "Understand data patterns, run A/B tests, and make evidence-based recommendations.",
            "resources": [
                "Coursera: Business Statistics and Analysis",
                "Khan Academy: Statistics (Free)",
                "Book: Statistics for Business and Economics"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "Data Analytics",
            "reason": "Core competency for translating raw data into actionable business insights.",
            "resources": [
                "Google Data Analytics Professional Certificate",
                "Coursera: Business Analytics Specialization by Wharton",
                "edX: Data Analysis for Business"
            ],
            "duration": "3 weeks"
        },
        {
            "skill": "Python",
            "reason": "Increasingly expected of business analysts for automation and advanced analysis.",
            "resources": [
                "Coursera: Python for Everybody",
                "DataCamp: Python for Business Analysts",
                "Automate the Boring Stuff with Python (Free online)"
            ],
            "duration": "3 weeks"
        },
    ],

    "python developer": [
        {
            "skill": "Python",
            "reason": "Core programming language. Must have deep proficiency including OOP, decorators, and generators.",
            "resources": [
                "Coursera: Python 3 Programming Specialization by UMich",
                "Real Python: Intermediate and Advanced Tutorials",
                "Book: Fluent Python by Luciano Ramalho"
            ],
            "duration": "3 weeks"
        },
        {
            "skill": "Git",
            "reason": "Version control is non-negotiable for professional development. Used in every team.",
            "resources": [
                "Atlassian: Git Tutorial (Free)",
                "Coursera: Version Control with Git",
                "YouTube: Git and GitHub Crash Course by Traversy Media"
            ],
            "duration": "1 week"
        },
        {
            "skill": "GitHub",
            "reason": "Platform for collaboration, code review, and showcasing projects. Your developer portfolio.",
            "resources": [
                "GitHub Learning Lab (Free)",
                "GitHub Docs: Getting Started",
                "YouTube: GitHub for Beginners"
            ],
            "duration": "1 week"
        },
        {
            "skill": "Flask",
            "reason": "Lightweight web framework for building APIs and web applications in Python.",
            "resources": [
                "Flask Official Tutorial: Flaskr Blog App (Free)",
                "Coursera: Developing AI Applications with Python and Flask",
                "Book: Flask Web Development by Miguel Grinberg"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "Streamlit",
            "reason": "Rapidly build data-driven web apps and dashboards. Great for prototyping and demos.",
            "resources": [
                "Streamlit Official Docs: Get Started (Free)",
                "YouTube: Build 12 Data Science Apps with Streamlit",
                "Streamlit Gallery: Community Examples"
            ],
            "duration": "1 week"
        },
        {
            "skill": "SQL",
            "reason": "Backend developers need database skills. SQL is essential for data persistence.",
            "resources": [
                "SQLBolt: Interactive SQL Lessons (Free)",
                "Coursera: Databases and SQL for Data Science",
                "PostgreSQL Tutorial (Free)"
            ],
            "duration": "2 weeks"
        },
    ],

    "ml intern": [
        {
            "skill": "Python",
            "reason": "The language of machine learning. All major ML frameworks are Python-first.",
            "resources": [
                "Coursera: Python for Everybody",
                "Kaggle: Python Course (Free)",
                "Book: Python Crash Course"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "NumPy",
            "reason": "Fundamental library for numerical computing. Understanding arrays is essential for ML.",
            "resources": [
                "NumPy Official Getting Started (Free)",
                "DataCamp: Intro to NumPy",
                "YouTube: NumPy Full Course by freeCodeCamp"
            ],
            "duration": "1 week"
        },
        {
            "skill": "Pandas",
            "reason": "Data preprocessing is 80% of ML work. Pandas makes data cleaning manageable.",
            "resources": [
                "Kaggle: Pandas Course (Free)",
                "Real Python: Pandas Tutorials",
                "YouTube: Corey Schafer Pandas Tutorial"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "Statistics",
            "reason": "Understanding probability, distributions, and hypothesis testing underpins all ML algorithms.",
            "resources": [
                "Khan Academy: Statistics (Free)",
                "Coursera: Statistics with Python by UMich",
                "Book: Think Stats by Allen Downey (Free online)"
            ],
            "duration": "3 weeks"
        },
        {
            "skill": "Machine Learning",
            "reason": "Core ML concepts: regression, classification, clustering, model evaluation, and feature engineering.",
            "resources": [
                "Coursera: Machine Learning by Andrew Ng (Stanford)",
                "Kaggle: Intro to Machine Learning (Free)",
                "Book: Hands-On Machine Learning by Aurélien Géron"
            ],
            "duration": "4 weeks"
        },
    ],

    "data science intern": [
        {
            "skill": "Python",
            "reason": "Primary language for data science. Required for analysis, modeling, and visualization.",
            "resources": [
                "Coursera: Python for Everybody by UMich",
                "DataCamp: Intro to Python for Data Science",
                "Kaggle: Python Course (Free)"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "SQL",
            "reason": "Data scientists must query databases efficiently. SQL is used in every data pipeline.",
            "resources": [
                "Mode Analytics: SQL Tutorial (Free)",
                "Coursera: SQL for Data Science by UC Davis",
                "Kaggle: Intro to SQL (Free)"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "Pandas",
            "reason": "The workhorse of data manipulation in Python. Essential for EDA and data preparation.",
            "resources": [
                "Kaggle: Pandas Course (Free)",
                "Real Python: Pandas DataFrames Tutorial",
                "Book: Python for Data Analysis by Wes McKinney"
            ],
            "duration": "2 weeks"
        },
        {
            "skill": "NumPy",
            "reason": "Foundation for scientific computing. Powers Pandas, scikit-learn, and TensorFlow under the hood.",
            "resources": [
                "NumPy Getting Started Guide (Free)",
                "YouTube: NumPy Tutorial by Keith Galli",
                "Coursera: Introduction to Data Science in Python"
            ],
            "duration": "1 week"
        },
        {
            "skill": "Statistics",
            "reason": "Statistical thinking is the backbone of data science. Essential for analysis and inference.",
            "resources": [
                "Khan Academy: Statistics and Probability (Free)",
                "Coursera: Statistics with Python Specialization",
                "Book: Practical Statistics for Data Scientists"
            ],
            "duration": "3 weeks"
        },
        {
            "skill": "Machine Learning",
            "reason": "Core data science skill for building predictive models and extracting patterns from data.",
            "resources": [
                "Coursera: Machine Learning Specialization by Andrew Ng",
                "Kaggle: Intro to Machine Learning (Free)",
                "Fast.ai: Practical Deep Learning (Free)"
            ],
            "duration": "4 weeks"
        },
        {
            "skill": "Data Analytics",
            "reason": "End-to-end analytical workflow: from data collection to insight communication.",
            "resources": [
                "Google Data Analytics Professional Certificate",
                "Coursera: IBM Data Science Professional Certificate",
                "Kaggle: Data Science Projects and Competitions"
            ],
            "duration": "3 weeks"
        },
    ],
}


# ============================================================================
# Project Recommendations Database (per role)
# ============================================================================

ROLE_PROJECTS = {
    "data analyst": [
        {
            "title": "Sales Performance Dashboard",
            "description": "Build an interactive sales dashboard using Power BI or Tableau with real-world retail datasets. Include KPIs like revenue trends, top products, regional performance, and seasonal patterns.",
            "skills_used": ["Power BI", "Tableau", "SQL", "Excel", "Data Analytics"],
            "difficulty": "Beginner",
            "estimated_time": "1 week"
        },
        {
            "title": "Customer Segmentation Analysis",
            "description": "Perform RFM (Recency, Frequency, Monetary) analysis on e-commerce data using Python and Pandas. Cluster customers into segments and create actionable marketing recommendations.",
            "skills_used": ["Python", "Pandas", "NumPy", "Statistics", "Data Analytics"],
            "difficulty": "Intermediate",
            "estimated_time": "2 weeks"
        },
        {
            "title": "Survey Data Analysis & Visualization",
            "description": "Analyze survey responses using Python, clean messy data, perform statistical tests, and create publication-quality visualizations using Matplotlib and Seaborn.",
            "skills_used": ["Python", "Pandas", "Statistics", "Data Analytics"],
            "difficulty": "Beginner",
            "estimated_time": "1 week"
        },
        {
            "title": "Financial Report Automation",
            "description": "Automate monthly financial report generation using Python and Excel. Pull data from CSVs, compute metrics, and generate formatted Excel reports with charts.",
            "skills_used": ["Python", "Excel", "Pandas", "Data Analytics"],
            "difficulty": "Intermediate",
            "estimated_time": "2 weeks"
        },
        {
            "title": "Web Scraping & Data Analysis Pipeline",
            "description": "Build a web scraper to collect job listing data, clean and store it in a database, then analyze trends in job markets using SQL and Python.",
            "skills_used": ["Python", "SQL", "Pandas", "Data Analytics"],
            "difficulty": "Advanced",
            "estimated_time": "3 weeks"
        },
    ],

    "business analyst": [
        {
            "title": "Market Research Dashboard",
            "description": "Create a comprehensive market research dashboard in Power BI that tracks competitor pricing, market share, and industry trends using publicly available data.",
            "skills_used": ["Power BI", "Excel", "Data Analytics", "Statistics"],
            "difficulty": "Beginner",
            "estimated_time": "1 week"
        },
        {
            "title": "SWOT Analysis Tool",
            "description": "Build a Python-based SWOT analysis tool that takes company data as input and generates structured Strengths, Weaknesses, Opportunities, and Threats reports.",
            "skills_used": ["Python", "Excel", "Data Analytics"],
            "difficulty": "Beginner",
            "estimated_time": "1 week"
        },
        {
            "title": "KPI Tracking System",
            "description": "Design a KPI tracking system using Excel and Power BI that monitors business metrics, sends alerts for deviations, and generates weekly executive summaries.",
            "skills_used": ["Excel", "Power BI", "SQL", "Data Analytics"],
            "difficulty": "Intermediate",
            "estimated_time": "2 weeks"
        },
        {
            "title": "Business Process Flowchart Generator",
            "description": "Create a Python application that visualizes business processes as flowcharts. Input process steps and decision points, output professional diagrams.",
            "skills_used": ["Python", "Data Analytics"],
            "difficulty": "Intermediate",
            "estimated_time": "2 weeks"
        },
        {
            "title": "Competitor Analysis Report Generator",
            "description": "Build an automated system that scrapes competitor data, compares features and pricing, and generates a structured comparison report using Python and Tableau.",
            "skills_used": ["Python", "Tableau", "SQL", "Data Analytics"],
            "difficulty": "Advanced",
            "estimated_time": "3 weeks"
        },
    ],

    "python developer": [
        {
            "title": "Portfolio Website with Flask",
            "description": "Build a personal portfolio website using Flask with project showcase, blog, contact form, and admin panel. Deploy on a cloud platform.",
            "skills_used": ["Python", "Flask", "Git", "GitHub", "SQL"],
            "difficulty": "Beginner",
            "estimated_time": "2 weeks"
        },
        {
            "title": "REST API for Task Management",
            "description": "Create a full CRUD REST API using Flask with JWT authentication, SQLite database, input validation, error handling, and Swagger documentation.",
            "skills_used": ["Python", "Flask", "SQL", "Git", "GitHub"],
            "difficulty": "Intermediate",
            "estimated_time": "2 weeks"
        },
        {
            "title": "Web Scraper with Data Pipeline",
            "description": "Build a web scraping tool using BeautifulSoup/Scrapy that collects data, processes it through a pipeline, stores in a database, and provides a Streamlit dashboard.",
            "skills_used": ["Python", "Streamlit", "SQL", "Pandas", "Git"],
            "difficulty": "Intermediate",
            "estimated_time": "2 weeks"
        },
        {
            "title": "Real-Time Chat Application",
            "description": "Develop a real-time chat app using Flask-SocketIO with user authentication, message history, private rooms, and a responsive frontend.",
            "skills_used": ["Python", "Flask", "Git", "GitHub", "SQL"],
            "difficulty": "Advanced",
            "estimated_time": "3 weeks"
        },
        {
            "title": "Automation Scripts Collection",
            "description": "Create a library of 10+ automation scripts: file organizer, email sender, PDF merger, image resizer, system monitor, etc. Package and publish on GitHub.",
            "skills_used": ["Python", "Git", "GitHub"],
            "difficulty": "Beginner",
            "estimated_time": "2 weeks"
        },
    ],

    "ml intern": [
        {
            "title": "House Price Prediction Model",
            "description": "Build a regression model to predict house prices using scikit-learn. Include feature engineering, model comparison, hyperparameter tuning, and a Streamlit deployment.",
            "skills_used": ["Python", "Machine Learning", "Pandas", "NumPy", "Streamlit"],
            "difficulty": "Beginner",
            "estimated_time": "2 weeks"
        },
        {
            "title": "Sentiment Analysis on Product Reviews",
            "description": "Build an NLP pipeline for sentiment classification on Amazon/Yelp reviews. Compare Bag-of-Words, TF-IDF, and word embeddings with multiple classifiers.",
            "skills_used": ["Python", "Machine Learning", "Pandas", "NumPy", "Statistics"],
            "difficulty": "Intermediate",
            "estimated_time": "2 weeks"
        },
        {
            "title": "Image Classifier with CNN",
            "description": "Build a Convolutional Neural Network for image classification (e.g., CIFAR-10). Implement data augmentation, transfer learning, and deploy with a web interface.",
            "skills_used": ["Python", "Machine Learning", "NumPy"],
            "difficulty": "Advanced",
            "estimated_time": "3 weeks"
        },
        {
            "title": "Movie Recommendation System",
            "description": "Implement collaborative filtering and content-based recommendation algorithms. Use the MovieLens dataset and create an interactive Streamlit app.",
            "skills_used": ["Python", "Machine Learning", "Pandas", "Streamlit"],
            "difficulty": "Intermediate",
            "estimated_time": "2 weeks"
        },
        {
            "title": "Spam Email Detector",
            "description": "Build a text classification model that detects spam emails. Include feature extraction, model training, evaluation metrics, and a real-time prediction interface.",
            "skills_used": ["Python", "Machine Learning", "Pandas", "NumPy"],
            "difficulty": "Beginner",
            "estimated_time": "1 week"
        },
    ],

    "data science intern": [
        {
            "title": "Exploratory Data Analysis on Real-World Dataset",
            "description": "Perform comprehensive EDA on a dataset (e.g., COVID-19, World Happiness Report). Include data cleaning, statistical analysis, visualizations, and a written report.",
            "skills_used": ["Python", "Pandas", "NumPy", "Statistics", "Data Analytics"],
            "difficulty": "Beginner",
            "estimated_time": "1 week"
        },
        {
            "title": "End-to-End Predictive Modeling Pipeline",
            "description": "Build a complete ML pipeline: data ingestion, cleaning, feature engineering, model selection, hyperparameter tuning, evaluation, and deployment. Use scikit-learn's Pipeline API.",
            "skills_used": ["Python", "Machine Learning", "Pandas", "NumPy", "Statistics"],
            "difficulty": "Intermediate",
            "estimated_time": "3 weeks"
        },
        {
            "title": "NLP Text Classification System",
            "description": "Build a text classifier for news articles or customer feedback. Implement preprocessing, vectorization, multiple models, and evaluation with confusion matrices.",
            "skills_used": ["Python", "Machine Learning", "Pandas", "Data Analytics"],
            "difficulty": "Intermediate",
            "estimated_time": "2 weeks"
        },
        {
            "title": "Time Series Forecasting Dashboard",
            "description": "Build a forecasting system for stock prices or weather data. Implement ARIMA, Prophet, and LSTM models. Create a Streamlit dashboard for interactive forecasting.",
            "skills_used": ["Python", "Machine Learning", "Statistics", "Pandas", "Streamlit"],
            "difficulty": "Advanced",
            "estimated_time": "3 weeks"
        },
        {
            "title": "A/B Testing Analysis Framework",
            "description": "Create a framework for analyzing A/B test results. Include sample size calculation, statistical significance testing, effect size estimation, and automated report generation.",
            "skills_used": ["Python", "Statistics", "Pandas", "Data Analytics"],
            "difficulty": "Intermediate",
            "estimated_time": "2 weeks"
        },
    ],
}


# ============================================================================
# Career Path Definitions
# ============================================================================

CAREER_PATHS = {
    "data analyst": [
        "Data Analyst Intern",
        "Junior Data Analyst",
        "Data Analyst",
        "Senior Data Analyst",
        "Lead Data Analyst / Analytics Manager"
    ],
    "business analyst": [
        "Business Analyst Intern",
        "Junior Business Analyst",
        "Business Analyst",
        "Senior Business Analyst",
        "Business Intelligence Manager"
    ],
    "python developer": [
        "Python Developer Intern",
        "Junior Python Developer",
        "Python Developer",
        "Senior Python Developer",
        "Tech Lead / Software Architect"
    ],
    "ml intern": [
        "ML Intern",
        "Junior ML Engineer",
        "Machine Learning Engineer",
        "Senior ML Engineer",
        "ML Lead / AI Research Scientist"
    ],
    "data science intern": [
        "Data Science Intern",
        "Junior Data Scientist",
        "Data Scientist",
        "Senior Data Scientist",
        "Principal Data Scientist / Head of Data Science"
    ],
}


# ============================================================================
# Improvement Suggestions
# ============================================================================

def generate_improvement_suggestions(parsed_resume, ats_result):
    """
    Generates prioritized improvement suggestions based on resume analysis.

    Analyzes the parsed resume and ATS score breakdown to identify gaps
    and produce actionable recommendations for skills, projects,
    certifications, and formatting.

    Args:
        parsed_resume (dict): Parsed resume from nlp_engine.parse_resume.
        ats_result (dict): ATS score result from ats_scorer.calculate_ats_score.

    Returns:
        dict: Improvement suggestions with keys:
            - missing_skills (list[dict]): Skill suggestions with 'skill' and 'reason'
            - missing_projects (list[str]): Project ideas
            - missing_certifications (list[str]): Certification recommendations
            - formatting_suggestions (list[str]): Resume formatting tips
    """
    current_skills = parsed_resume.get("skills", [])
    weaknesses = ats_result.get("weaknesses", [])
    breakdown = ats_result.get("breakdown", {})

    # --- Missing Skills ---
    missing_core = get_missing_skills(current_skills)

    # Detailed reasons for each missing core skill
    skill_reasons = {
        "Python": "Python is the #1 programming language for data science, analytics, and automation. Required in 90%+ of data-related roles.",
        "SQL": "SQL is essential for database querying. Every data role requires extracting and manipulating data from relational databases.",
        "Pandas": "Pandas is Python's primary data manipulation library. Critical for data cleaning, transformation, and analysis workflows.",
        "NumPy": "NumPy provides efficient numerical computing. It underpins Pandas, scikit-learn, and virtually all scientific Python libraries.",
        "Power BI": "Power BI is Microsoft's leading BI tool. Highly sought after for creating interactive business dashboards and reports.",
        "Tableau": "Tableau is the industry standard for data visualization. Mastering it opens doors to analyst and BI roles.",
        "Excel": "Excel remains ubiquitous in business. Proficiency in pivot tables, VLOOKUP, and data analysis features is expected.",
        "Machine Learning": "ML skills differentiate you from basic analysts. Understanding algorithms and model evaluation is increasingly expected.",
        "Data Analytics": "Data analytics is a meta-skill that ties together tools and techniques for deriving actionable insights from data.",
        "Statistics": "Statistical knowledge enables you to make data-driven decisions, run experiments, and validate hypotheses rigorously.",
        "Git": "Git version control is standard in software development. Essential for collaboration and tracking code changes.",
        "GitHub": "GitHub is your professional portfolio. Employers review your GitHub profile to assess your coding skills and projects.",
        "Streamlit": "Streamlit enables rapid creation of data apps. Great for showcasing ML models and analysis results interactively.",
        "Flask": "Flask is a lightweight Python web framework. Valuable for building APIs, web apps, and deploying ML models.",
    }

    missing_skills_suggestions = []
    for skill in missing_core:
        reason = skill_reasons.get(skill, f"{skill} is a valuable skill that enhances your professional profile.")
        missing_skills_suggestions.append({"skill": skill, "reason": reason})

    # --- Missing Projects ---
    projects = parsed_resume.get("projects", [])
    project_suggestions = []

    project_score = breakdown.get("projects", {}).get("score", 0)
    if project_score < 11:  # Less than 3 projects
        # Suggest projects based on current and missing skills
        current_lower = {s.lower() for s in current_skills}

        if "python" in current_lower:
            project_suggestions.append(
                "Build a Data Cleaning & Analysis Pipeline using Python and Pandas on a real-world Kaggle dataset"
            )
        if "sql" in current_lower:
            project_suggestions.append(
                "Create an E-commerce Database Analysis project using SQL queries to derive business insights"
            )
        if not projects:
            project_suggestions.append(
                "Start with a Personal Portfolio Website to showcase your skills and projects"
            )
        project_suggestions.append(
            "Build a Dashboard using Power BI or Tableau with publicly available datasets (COVID-19, World Bank, etc.)"
        )
        project_suggestions.append(
            "Create an automated web scraper that collects, cleans, and visualizes data from any website"
        )

        if "machine learning" in current_lower:
            project_suggestions.append(
                "Build a Sentiment Analysis tool using NLP techniques on Twitter or product review data"
            )

    # --- Missing Certifications ---
    certs = parsed_resume.get("certifications", [])
    cert_suggestions = []

    cert_score = breakdown.get("certifications", {}).get("score", 0)
    if cert_score < 7:
        cert_suggestions = [
            "Google Data Analytics Professional Certificate on Coursera — Comprehensive, industry-recognized, and beginner-friendly",
            "IBM Data Science Professional Certificate on Coursera — Covers Python, SQL, ML, and data visualization",
            "Microsoft Power BI Data Analyst Associate (PL-300) — Validates Power BI expertise for business roles",
            "HackerRank Python Certification — Free and quick way to validate Python programming skills",
            "AWS Cloud Practitioner — Entry-level cloud certification valued across industries",
        ]

    # --- Formatting Suggestions ---
    formatting = []
    word_count = parsed_resume.get("word_count", 0)
    sections = parsed_resume.get("sections_found", [])

    if word_count < 200:
        formatting.append(
            f"Your resume is very short ({word_count} words). Aim for 400-800 words to provide sufficient detail about your skills and experience."
        )
    elif word_count > 1500:
        formatting.append(
            f"Your resume is quite long ({word_count} words). Consider trimming to 600-800 words for better readability and ATS compatibility."
        )

    if not parsed_resume.get("email"):
        formatting.append("Add your email address prominently at the top of your resume.")
    if not parsed_resume.get("phone"):
        formatting.append("Include your phone number in the contact information section.")
    if not parsed_resume.get("linkedin"):
        formatting.append("Add your LinkedIn profile URL. Many recruiters check LinkedIn before scheduling interviews.")

    essential_sections = ["education", "skills", "projects", "experience"]
    missing_sections = [s for s in essential_sections if s not in sections]
    if missing_sections:
        formatting.append(
            f"Missing important sections: {', '.join(s.title() for s in missing_sections)}. "
            "Add these to ensure ATS systems can parse your resume effectively."
        )

    if "objective" not in sections and "summary" not in sections:
        formatting.append(
            "Consider adding a 'Professional Summary' or 'Career Objective' section at the top. "
            "A 2-3 sentence summary helps recruiters quickly understand your profile."
        )

    formatting.append("Use consistent formatting: same font, clear section headers, and bullet points for readability.")
    formatting.append("Save your resume as a clean PDF to preserve formatting across different ATS platforms.")

    return {
        "missing_skills": missing_skills_suggestions,
        "missing_projects": project_suggestions,
        "missing_certifications": cert_suggestions,
        "formatting_suggestions": formatting
    }


# ============================================================================
# Skill Roadmap Generation
# ============================================================================

def generate_skill_roadmap(current_skills, target_role):
    """
    Generates a personalized learning roadmap for a target role.

    Skips skills the candidate already has and provides step-by-step
    guidance with specific resources and time estimates.

    Args:
        current_skills (list[str]): Candidate's current skills.
        target_role (str): Target internship/role title.

    Returns:
        list[dict]: Ordered list of learning steps, each with:
            - step (int): Step number
            - skill (str): Skill to learn
            - reason (str): Why this skill matters for the role
            - resources (list[str]): Specific learning resources
            - duration (str): Estimated learning time
    """
    current_lower = {s.lower() for s in (current_skills or [])}

    # Find matching role roadmap
    role_key = _match_role_key(target_role)
    roadmap_template = ROLE_ROADMAPS.get(role_key, ROLE_ROADMAPS.get("data analyst", []))

    # Filter out skills the candidate already has
    roadmap = []
    step_num = 1

    for item in roadmap_template:
        skill_name = item["skill"]
        if skill_name.lower() not in current_lower:
            roadmap.append({
                "step": step_num,
                "skill": skill_name,
                "reason": item["reason"],
                "resources": item["resources"],
                "duration": item["duration"]
            })
            step_num += 1

    # If all skills are covered, provide advanced suggestions
    if not roadmap:
        roadmap = [{
            "step": 1,
            "skill": "Advanced Specialization",
            "reason": f"You already have the core skills for {target_role}! Focus on deepening your expertise and building an impressive project portfolio.",
            "resources": [
                "Kaggle Competitions: Apply your skills to real-world challenges",
                "Open-source contributions on GitHub",
                "Build and deploy a complete end-to-end project"
            ],
            "duration": "Ongoing"
        }]

    return roadmap


# ============================================================================
# Project Recommendations
# ============================================================================

def generate_project_recommendations(current_skills, target_role):
    """
    Generates project recommendations tailored to the target role.

    Prioritizes projects that match the candidate's current skills
    (easier to start) while also suggesting stretch projects.

    Args:
        current_skills (list[str]): Candidate's current skills.
        target_role (str): Target internship/role title.

    Returns:
        list[dict]: Project recommendations, each with:
            - title (str): Project name
            - description (str): What to build
            - skills_used (list[str]): Skills needed
            - difficulty (str): Beginner/Intermediate/Advanced
            - estimated_time (str): Time estimate
    """
    current_lower = {s.lower() for s in (current_skills or [])}

    # Find matching role projects
    role_key = _match_role_key(target_role)
    projects = ROLE_PROJECTS.get(role_key, ROLE_PROJECTS.get("data analyst", []))

    # Sort projects: prioritize those where the candidate has more of the required skills
    def skill_coverage(project):
        skills_needed = project.get("skills_used", [])
        if not skills_needed:
            return 0
        matched = sum(1 for s in skills_needed if s.lower() in current_lower)
        return matched / len(skills_needed)

    # Sort by coverage (most achievable first), then by difficulty
    difficulty_order = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
    sorted_projects = sorted(
        projects,
        key=lambda p: (-skill_coverage(p), difficulty_order.get(p.get("difficulty", "Intermediate"), 1))
    )

    return sorted_projects


# ============================================================================
# Resume Feedback
# ============================================================================

def generate_resume_feedback(parsed_resume, ats_result):
    """
    Generates detailed section-by-section resume feedback.

    Provides constructive, specific feedback based on actual resume data
    and ATS scoring results, acting as a professional resume reviewer.

    Args:
        parsed_resume (dict): Parsed resume from nlp_engine.parse_resume.
        ats_result (dict): ATS score result from ats_scorer.calculate_ats_score.

    Returns:
        dict: Feedback dictionary with keys:
            - overall (str): 2-3 sentence overall assessment
            - skills_section (str): Skills feedback
            - projects_section (str): Projects feedback
            - education_section (str): Education feedback
            - experience_section (str): Experience feedback
            - formatting (str): Formatting feedback
            - tips (list[str]): 5-7 actionable tips
    """
    total_score = ats_result.get("total_score", 0)
    breakdown = ats_result.get("breakdown", {})
    skills = parsed_resume.get("skills", [])
    projects = parsed_resume.get("projects", [])
    education = parsed_resume.get("education", [])
    experience = parsed_resume.get("experience", [])
    certs = parsed_resume.get("certifications", [])
    word_count = parsed_resume.get("word_count", 0)
    sections = parsed_resume.get("sections_found", [])

    # --- Overall Assessment ---
    if total_score >= 80:
        overall = (
            f"Your resume scores {total_score}/100, which is excellent! "
            "It demonstrates strong qualifications with a good balance of skills, projects, and experience. "
            "Focus on tailoring it for specific roles and adding quantified achievements to stand out even more."
        )
    elif total_score >= 60:
        overall = (
            f"Your resume scores {total_score}/100, which is good but has room for improvement. "
            "You have a solid foundation, but strengthening weaker areas could significantly boost your chances. "
            "Review the detailed feedback below for specific action items."
        )
    elif total_score >= 40:
        overall = (
            f"Your resume scores {total_score}/100, indicating several areas need attention. "
            "While you have some positive elements, key sections need enhancement to be competitive. "
            "Prioritize the suggestions below to make the biggest impact quickly."
        )
    else:
        overall = (
            f"Your resume scores {total_score}/100, suggesting significant improvements are needed. "
            "Don't be discouraged — every strong resume started somewhere. "
            "Focus on the most impactful changes first: add relevant skills, projects, and structure your resume with clear sections."
        )

    # --- Skills Section Feedback ---
    skill_count = len(skills)
    skill_score = breakdown.get("skills_match", {}).get("score", 0)
    if skill_count == 0:
        skills_feedback = (
            "No skills were detected in your resume. This is a critical gap — "
            "create a dedicated 'Technical Skills' section listing your programming languages, "
            "tools, frameworks, and domain knowledge. Aim for 8-15 relevant skills."
        )
    elif skill_count < 5:
        skills_feedback = (
            f"Only {skill_count} skill(s) detected: {', '.join(skills)}. "
            "This is below average. Add more relevant skills — most competitive resumes list 8-15 skills. "
            "Include both technical skills (Python, SQL) and tools (Power BI, Git)."
        )
    elif skill_count < 10:
        skills_feedback = (
            f"Good skill set with {skill_count} skills detected: {', '.join(skills[:8])}. "
            "Consider adding a few more skills to reach 10-15. Make sure to include skills "
            "that are specifically mentioned in job descriptions you're targeting."
        )
    else:
        skills_feedback = (
            f"Excellent skill coverage with {skill_count} skills: {', '.join(skills[:8])}{'...' if skill_count > 8 else ''}. "
            "Your skills section is strong. Consider organizing skills by category "
            "(Languages, Frameworks, Tools, Databases) for better readability."
        )

    # --- Projects Section Feedback ---
    project_count = len(projects)
    if project_count == 0:
        projects_feedback = (
            "No projects were found on your resume. Projects are crucial for demonstrating practical skills, "
            "especially for entry-level candidates. Add 2-4 relevant projects with clear descriptions "
            "of what you built, technologies used, and measurable outcomes."
        )
    elif project_count < 3:
        projects_feedback = (
            f"{project_count} project(s) found: {', '.join(projects[:3])}. "
            "Consider adding more projects to reach 3-4 total. For each project, include: "
            "the problem you solved, tools/technologies used, and any quantifiable results."
        )
    else:
        projects_feedback = (
            f"Strong project section with {project_count} project(s). "
            "Make sure each project description includes the tech stack used, "
            "your specific contributions, and measurable outcomes (e.g., 'Improved accuracy by 15%')."
        )

    # --- Education Section Feedback ---
    if not education:
        education_feedback = (
            "No formal education was detected. Ensure your education section includes "
            "your degree, field of study, institution name, and graduation year. "
            "This is a mandatory section for most ATS systems."
        )
    else:
        highest = education[0].get("degree", "Unknown")
        field = education[0].get("field", "")
        education_feedback = (
            f"Education detected: {highest}"
            f"{' in ' + field if field else ''}. "
            "Consider adding your GPA if it's above 3.0/4.0 (or equivalent), "
            "relevant coursework, and any academic honors or achievements."
        )

    # --- Experience Section Feedback ---
    exp_years = parsed_resume.get("experience_years", 0)
    if not experience and exp_years == 0:
        experience_feedback = (
            "No work experience detected. For entry-level candidates, include: "
            "internships, part-time jobs, volunteer work, freelance projects, and teaching assistant roles. "
            "Any professional experience demonstrates workplace readiness."
        )
    elif exp_years < 1:
        experience_feedback = (
            f"{len(experience)} position(s) found with less than 1 year of experience. "
            "For each role, use action verbs to describe your contributions and include "
            "specific achievements. Even short internships can be described impactfully."
        )
    else:
        experience_feedback = (
            f"{len(experience)} position(s) found with approximately {exp_years} year(s) of experience. "
            "Ensure each position includes specific achievements with numbers "
            "(e.g., 'Reduced processing time by 30%'). Quantified results make a strong impression."
        )

    # --- Formatting Feedback ---
    formatting_parts = []
    if word_count < 200:
        formatting_parts.append(f"Resume is too brief ({word_count} words). Expand to 400-800 words.")
    elif word_count > 1500:
        formatting_parts.append(f"Resume is too long ({word_count} words). Trim to 600-800 words for a 1-page format.")
    else:
        formatting_parts.append(f"Word count ({word_count}) is appropriate.")

    essential = ["education", "skills", "projects", "experience"]
    present_sections = [s for s in essential if s in sections]
    missing_sections = [s for s in essential if s not in sections]

    if missing_sections:
        formatting_parts.append(f"Missing sections: {', '.join(s.title() for s in missing_sections)}.")
    else:
        formatting_parts.append("All essential sections are present.")

    if not parsed_resume.get("email") or not parsed_resume.get("phone"):
        formatting_parts.append("Ensure complete contact info (email, phone, LinkedIn).")

    formatting = " ".join(formatting_parts)

    # --- Actionable Tips ---
    tips = []

    if skill_count < 8:
        tips.append(f"Add {8 - skill_count} more relevant technical skills to your Skills section.")
    if project_count < 3:
        tips.append(f"Add {3 - project_count} more project(s) with clear descriptions and tech stacks.")
    if not certs:
        tips.append("Earn at least one industry certification (e.g., Google Data Analytics on Coursera).")
    if not parsed_resume.get("linkedin"):
        tips.append("Add your LinkedIn profile URL to your resume header.")

    # Keyword-related tips
    keyword_score = breakdown.get("keywords", {}).get("score", 0)
    if keyword_score < 8:
        tips.append("Use more action verbs (developed, implemented, analyzed, optimized) to describe achievements.")
        tips.append("Quantify your accomplishments with numbers and percentages wherever possible.")

    if "summary" not in sections and "objective" not in sections:
        tips.append("Add a 2-3 sentence Professional Summary at the top highlighting your key strengths.")

    tips.append("Tailor your resume for each application by matching keywords from the job description.")

    # Ensure we have 5-7 tips
    generic_tips = [
        "Use a clean, ATS-friendly format: single column, standard fonts, clear section headers.",
        "Proofread carefully — spelling and grammar errors create a negative first impression.",
        "Include relevant coursework or online courses in your Education section.",
        "Add links to your GitHub profile or project demos for technical roles.",
        "Keep your resume to 1 page if you have less than 5 years of experience.",
    ]

    while len(tips) < 5:
        for gt in generic_tips:
            if gt not in tips:
                tips.append(gt)
                break
        else:
            break

    return {
        "overall": overall,
        "skills_section": skills_feedback,
        "projects_section": projects_feedback,
        "education_section": education_feedback,
        "experience_section": experience_feedback,
        "formatting": formatting,
        "tips": tips[:7]
    }


# ============================================================================
# Career Advice
# ============================================================================

def generate_career_advice(parsed_resume, recommendations):
    """
    Generates comprehensive career advice based on resume and internship matches.

    Acts as a virtual career coach, identifying the best-fit role,
    suggesting a career path, summarizing strengths, and providing
    specific action items.

    Args:
        parsed_resume (dict): Parsed resume from nlp_engine.parse_resume.
        recommendations (list[dict]): Internship recommendations from
            recommender.recommend_internships.

    Returns:
        dict: Career advice with keys:
            - best_fit_role (str): Title of best matching role
            - career_path (list[str]): Suggested career progression
            - strengths_summary (str): Summary of candidate's strengths
            - growth_areas (str): Areas for improvement
            - action_items (list[str]): Specific action items
    """
    skills = parsed_resume.get("skills", [])
    education = parsed_resume.get("education", [])
    experience = parsed_resume.get("experience", [])
    projects = parsed_resume.get("projects", [])
    certs = parsed_resume.get("certifications", [])
    exp_years = parsed_resume.get("experience_years", 0)

    # --- Best Fit Role ---
    best_fit_role = "Data Analyst Intern"  # Default
    best_match_pct = 0.0
    if recommendations:
        top = recommendations[0]
        best_fit_role = top.get("title", "Data Analyst Intern")
        best_match_pct = top.get("match_percentage", 0)

    # --- Career Path ---
    role_key = _match_role_key(best_fit_role)
    career_path = CAREER_PATHS.get(role_key, CAREER_PATHS["data analyst"])

    # --- Strengths Summary ---
    strength_parts = []

    skill_count = len(skills)
    if skill_count >= 8:
        strength_parts.append(f"a diverse technical skill set with {skill_count} skills including {', '.join(skills[:5])}")
    elif skill_count >= 4:
        strength_parts.append(f"a developing skill set with {skill_count} skills")

    if education:
        highest = education[0].get("degree", "")
        if highest:
            strength_parts.append(f"a {highest} education background")

    if len(projects) >= 3:
        strength_parts.append(f"hands-on project experience ({len(projects)} projects)")
    elif len(projects) >= 1:
        strength_parts.append(f"some project experience ({len(projects)} project(s))")

    if certs:
        strength_parts.append(f"{len(certs)} professional certification(s)")

    if exp_years > 0:
        strength_parts.append(f"approximately {exp_years} year(s) of experience")

    if strength_parts:
        strengths_summary = (
            f"You bring {' and '.join(strength_parts[:2])} to the table. "
            f"{'Additionally, you have ' + ' and '.join(strength_parts[2:]) + '. ' if len(strength_parts) > 2 else ''}"
            f"{'Your profile shows a strong foundation for a {best_fit_role} position.'.format(best_fit_role=best_fit_role) if best_match_pct >= 60 else 'Building on these strengths will help you become a strong candidate.'}"
        )
    else:
        strengths_summary = (
            "Your resume is at an early stage. The good news is that every expert started as a beginner. "
            "Focus on building foundational skills and gaining practical experience through projects."
        )

    # --- Growth Areas ---
    missing_core = get_missing_skills(skills)
    growth_parts = []

    if len(missing_core) > 5:
        growth_parts.append(
            f"Building technical skills is your top priority — you're missing {len(missing_core)} core skills including {', '.join(missing_core[:4])}"
        )
    elif missing_core:
        growth_parts.append(
            f"Adding a few more skills like {', '.join(missing_core[:3])} would strengthen your profile"
        )

    if len(projects) < 3:
        growth_parts.append("Building 2-3 more practical projects would significantly demonstrate your capabilities")

    if not certs:
        growth_parts.append("Earning industry certifications would validate your skills to employers")

    if growth_parts:
        growth_areas = ". ".join(growth_parts) + ". Focus on these areas systematically — even 30 minutes of daily practice adds up quickly."
    else:
        growth_areas = (
            "You're in great shape! To keep growing, focus on advanced specialization, "
            "building a public portfolio, and contributing to open-source projects."
        )

    # --- Action Items ---
    action_items = []

    if missing_core:
        top_skill = missing_core[0]
        action_items.append(f"Start learning {top_skill} this week — dedicate 1 hour daily to an online course or tutorial.")

    if len(projects) < 3:
        action_items.append(
            f"Build a new project this month: Choose one from the project recommendations for {best_fit_role}."
        )

    if not certs:
        action_items.append("Enroll in the Google Data Analytics Professional Certificate on Coursera within the next 7 days.")

    if not parsed_resume.get("linkedin"):
        action_items.append("Create or update your LinkedIn profile today — add a professional photo, headline, and summary.")

    action_items.append(f"Apply to at least 3 {best_fit_role} positions this month on LinkedIn, Internshala, or company career pages.")

    if not parsed_resume.get("email") or not parsed_resume.get("phone"):
        action_items.append("Update your resume with complete contact information (email, phone, LinkedIn URL).")

    action_items.append("Join relevant online communities (r/datascience, Kaggle, Discord servers) to network and learn.")

    # Ensure 5-7 items
    if len(action_items) < 5:
        extras = [
            "Set up a GitHub profile and push your project code with clear README files.",
            "Practice coding challenges on LeetCode or HackerRank for 30 minutes daily.",
            "Attend one virtual tech meetup or webinar this month for networking.",
            "Write a blog post about a recent project or learning to build your personal brand.",
        ]
        for extra in extras:
            if extra not in action_items and len(action_items) < 7:
                action_items.append(extra)

    return {
        "best_fit_role": best_fit_role,
        "career_path": career_path,
        "strengths_summary": strengths_summary,
        "growth_areas": growth_areas,
        "action_items": action_items[:7]
    }


# ============================================================================
# Internal Helper Functions
# ============================================================================

def _match_role_key(role_title):
    """
    Matches a role title string to one of the predefined role keys.

    Performs case-insensitive partial matching against known role patterns.

    Args:
        role_title (str): The role title to match.

    Returns:
        str: Matched role key, or 'data analyst' as default.
    """
    if not role_title:
        return "data analyst"

    role_lower = role_title.lower()

    # Pattern matching order (more specific first)
    role_patterns = {
        "ml intern": ["ml", "machine learning"],
        "data science intern": ["data science", "data scientist"],
        "python developer": ["python developer", "python dev", "software developer", "backend developer"],
        "business analyst": ["business analyst", "business analysis", "ba "],
        "data analyst": ["data analyst", "data analysis", "analytics"],
    }

    for role_key, patterns in role_patterns.items():
        for pattern in patterns:
            if pattern in role_lower:
                return role_key

    return "data analyst"
