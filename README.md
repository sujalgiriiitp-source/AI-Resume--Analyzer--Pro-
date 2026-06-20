# 🤖 AI Resume Analyzer Pro

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-6C63FF?style=for-the-badge)](LICENSE)

> **AI-powered resume analysis and internship recommendation platform** — parse PDF resumes, calculate ATS compatibility scores, identify skill gaps, get personalised internship matches, and receive actionable career improvement feedback.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **PDF Resume Parsing** | Upload PDF resumes and extract structured text automatically |
| 📊 **ATS Score Calculation** | Industry-aligned scoring across skills, format, experience & education |
| 🔍 **Skill Gap Analysis** | Detect present skills and surface missing ones from a curated taxonomy |
| 🎯 **Internship Matching** | Smart matching against a database of internship roles with % compatibility |
| 💡 **Improvement Suggestions** | Actionable, personalised recommendations to boost your resume |
| 📈 **Visual Analytics** | Interactive Plotly charts — radar, bar, and pie — for instant insight |
| 📥 **PDF & CSV Reports** | Download professional reports for offline review |
| 🗄️ **SQLite Persistence** | Track students and analysis history across sessions |

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io) with custom CSS theming
- **Language**: Python 3.9+
- **Data Processing**: Pandas, NumPy
- **NLP / ML**: NLTK, Scikit-Learn
- **PDF Parsing**: PyPDF2
- **Visualisation**: Plotly, Matplotlib
- **Report Generation**: fpdf2 (PDF), csv (CSV)
- **Database**: SQLite 3

---

## 📸 Screenshots

> *Screenshots will be added once the UI is finalised.*

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/ai-resume-analyzer-pro.git
cd ai-resume-analyzer-pro

# 2. (Recommended) Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app will open at **http://localhost:8501** in your default browser.

---

## ☁️ Deploy to Streamlit Cloud

1. Push your code to a **public GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select your repo, branch (`main`), and set the main file to `app.py`.
4. Streamlit Cloud will automatically detect `requirements.txt` and install dependencies.
5. Click **Deploy** — your app will be live within minutes! 🎉

---

## 📂 Project Structure

```
ai-resume-analyzer-pro/
├── .streamlit/
│   └── config.toml          # Streamlit theme & server config
├── assets/
│   └── styles.css           # Custom premium CSS
├── data/
│   ├── skills_db.json       # Master skill taxonomy
│   └── internships_db.json  # Internship definitions
├── database/
│   ├── __init__.py
│   ├── schema.sql           # SQLite table definitions
│   └── db.py                # CRUD operations
├── models/
│   └── __init__.py           # ML / analysis models
├── pages/
│   └── __init__.py           # Streamlit multi-page modules
├── reports/
│   ├── __init__.py
│   ├── pdf_report.py        # fpdf2-based PDF generation
│   └── csv_report.py        # CSV report generation
├── utils/
│   ├── __init__.py
│   └── helpers.py           # Score mapping & formatting helpers
├── app.py                   # Main Streamlit entry point
├── requirements.txt         # Python dependencies
└── README.md                # ← You are here
```

---

## 📝 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 AI Resume Analyzer Pro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 👤 Author

**Sujal Giri**

- GitHub: [@sujalgiriiitp](https://github.com/sujalgiriiitp)

---

> Built with ❤️ using Python & Streamlit
