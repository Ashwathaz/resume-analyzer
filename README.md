<div align="center">
  <h1>🚀 Smart Resume AI</h1>
  <p>An intelligent, AI-powered document analysis system designed to help job seekers optimize their resumes for Applicant Tracking Systems (ATS).</p>
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Streamlit-Framework-FF4B4B.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/AI-Google%20Gemini%20Pro-orange.svg" alt="Gemini">
  <img src="https://img.shields.io/badge/Database-PostgreSQL-336791.svg" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-Supported-2496ED.svg" alt="Docker">
</div>

---

## 📖 Table of Contents
1. [Project Overview](#-project-overview)
2. [What It Does](#-what-it-does)
3. [Key Features](#-key-features)
4. [Technology Stack](#-technology-stack)
5. [Prerequisites](#-prerequisites)
6. [Installation & Setup](#-installation--setup)
7. [Environment Variables](#-environment-variables)
8. [How to Run](#-how-to-run)
9. [Usage Guide](#-usage-guide)
10. [Admin Portal](#-admin-portal)
11. [Project Structure](#-project-structure)
12. [Troubleshooting](#-troubleshooting)

---

## 🌟 Project Overview
Smart Resume AI is a comprehensive, full-stack application built to mimic and outsmart modern Applicant Tracking Systems (ATS). Using large language models (Google's Gemini Pro & Groq Llama 3 fallback) and deep NLP text processing, the application acts as an expert recruiter. It provides detailed feedback, algorithmic scoring, job-to-resume matching, and actionable recommendations to dramatically improve a candidate's hiring chances.

Designed for high performance and premium aesthetics, the app features a sleek dark mode UI with interactive topographic backgrounds and fluid animations.

---

## 🎯 What It Does
1. **Parses Resumes:** Extracts text seamlessly from PDFs, Word documents (.docx), and images (via OCR), regardless of complex formatting.
2. **Evaluates against Job Descriptions:** Calculates cosine similarity and semantic matching between your resume and a target job description.
3. **Generates an ATS Score:** Mimics the filtration logic used by Fortune 500 companies to grade your resume on a 0-100 scale.
4. **Highlights Skill Gaps:** Identifies missing keywords and suggests critical skills to add based on industry standards.
5. **Provides AI Feedback:** Delivers structured, bulleted advice on formatting, tone, grammar, and impact (quantifying achievements).
6. **Exports Reports:** Generates a downloadable, professional PDF scorecard of your resume analysis.

---

## ✨ Key Features
- **Multi-Model AI Analysis**: Harnesses Google Gemini Pro for deep insights, with Groq acting as an ultra-fast fallback to ensure 100% uptime.
- **Advanced Document Processing**: Utilizes `pdfplumber`, `python-docx`, and OCR (`pytesseract`/`Poppler`) to handle any document variation.
- **Interactive Visualizations**: Dynamic ATS score gauges, radar charts for skills, and visual data breakdowns using Plotly.
- **Admin Dashboard**: Secure backend portal for administrators to review user metrics, view historical data, and manage application settings.
- **Seamless Export**: One-click generation of beautifully formatted PDF analysis reports via `ReportLab`.
- **Responsive & Premium UI**: Custom Vanilla CSS injected into Streamlit to create a native-app feel with glassmorphism and subtle animations (Lottie).
- **Persistent Storage**: Containerized PostgreSQL integration via SQLAlchemy ORM for scalable user data storage (with SQLite fallback for local dev).

---

## 🛠️ Technology Stack

### Frontend & UI
- **Framework:** Streamlit
- **Styling:** Vanilla CSS3, Custom HTML Injection
- **Visuals:** Plotly, Lottie-Web, Streamlit-Extras

### AI & Natural Language Processing
- **LLMs:** Google Gemini Pro API, Groq API (Llama 3)
- **NLP Utilities:** spaCy (NER), NLTK (Tokenization/Keyword Density)
- **Machine Learning:** Scikit-Learn (TF-IDF, Cosine Similarity)

### Document Processing
- **PDFs:** pdfplumber, pypdf
- **Word Docs:** python-docx, docx2txt
- **OCR:** pytesseract, pdf2image (Requires Poppler)

### Backend & Infrastructure
- **Language:** Python 3.11+
- **Database:** PostgreSQL (Production) / SQLite (Local)
- **ORM:** SQLAlchemy
- **Containerization:** Docker, Docker Compose

---

## 📋 Prerequisites
Before you begin, ensure you have the following installed on your machine:
- **Python 3.11** or higher
- **Git**
- **Docker & Docker Compose** (Optional, but recommended for database and containerized deployment)
- **Poppler** (Required for PDF to Image conversion/OCR. Installation varies by OS):
  - *Windows:* Download binaries and add to PATH.
  - *macOS:* `brew install poppler`
  - *Linux:* `sudo apt-get install poppler-utils`
- **Tesseract OCR** (Required for parsing image-based resumes)

---

## ⚙️ Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Ashwathaz/AI_RESUME-ANALYZER.git
   cd AI_RESUME-ANALYZER
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run NLP Setup Scripts** (If NLTK/spaCy models are missing)
   ```bash
   python -m spacy download en_core_web_sm
   ```

---

## 🔐 Environment Variables
Create a `.env` file in the root directory. Use `.env.example` as a template.

```env
# Google GenAI API Key (Primary AI)
GOOGLE_API_KEY=your_google_gemini_api_key

# Groq API Key (Fallback AI)
GROQ_API_KEY=your_groq_api_key

# Database Connection (Leave default for local SQLite, change for Postgres)
DATABASE_URL=sqlite:///resume_data.db
# For Docker Postgres: postgresql://admin:password@localhost:5432/resume_db

# (Optional) Admin Credentials Secret
ADMIN_PASS=your_custom_admin_password
```

---

## 🚀 How to Run

### Method 1: Local Development (Streamlit)
Ideal for testing and active development.

```bash
# Ensure your virtual environment is active
streamlit run app.py
```
The application will launch in your default web browser at `http://localhost:8501`.

### Method 2: Docker Compose (Production Environment)
Ideal for a clean, completely containerized setup with the PostgreSQL database.

```bash
# Build and start the containers in detached mode
docker-compose up --build -d
```
The app will be accessible at `http://localhost:8501`. Use `docker-compose logs -f` to view live output.

---

## 💡 Usage Guide

1. **Navigate to the App:** Open the URL provided by Streamlit.
2. **Select Mode:** Choose between Standard Analyzer or JD Matcher from the sidebar.
3. **Upload Resume:** Drag and drop your `.pdf`, `.docx`, or `.png/.jpg` resume.
4. **Paste Job Description (Optional):** If using the Matcher, paste the JD text.
5. **Analyze:** Click the Analyze button.
6. **Review Results:** Review your ATS score, read the AI's suggestions, view key skills identified, and check the formatting feedback.
7. **Download Report:** Click "Download PDF Report" to save a local copy of your personalized feedback.

---

## 🛡️ Admin Portal

A secure dashboard exists to monitor application usage, user metrics, and stored resume data.
- **Access Route:** Navigate to the "Admin Portal" via the sidebar menu.
- **Default Credentials:** 
  - **Username:** `supadmin1`
  - **Password:** `ZEUS999+`
*(Note: It is highly recommended to change these credentials in a production environment via your DB or environment variables).*

---

## 📂 Project Structure

```text
AI_RESUME-ANALYZER/
│
├── app.py                   # Main Streamlit application entry point
├── ui_components.py         # Custom UI, cards, and rendering functions
├── create_test_resume.py    # Utility script for testing
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container blueprint for the Python app
├── docker-compose.yml       # Multi-container orchestration (App + DB)
├── README.md                # Project documentation
├── TECHSTACK.md             # Detailed technology stack breakdown
│
├── assets/                  # Images, Lottie animations, and static media
├── config/                  # Configuration files and constants
├── dashboard/               # Admin portal logic and layout
├── database/                # SQLite/Postgres connection and SQLAlchemy models
├── jobs/                    # Pre-defined job templates and data
├── style/                   # CSS stylesheets for the UI
└── utils/                   # Helper functions (PDF extraction, AI prompt logic)
```

---

## 🔧 Troubleshooting

- **PDF Upload Errors:** Ensure `poppler` is correctly installed and added to your system PATH.
- **AI Analysis Failing:** Check your `.env` file to ensure your `GOOGLE_API_KEY` is valid and has sufficient quota.
- **Database Connection Refused:** If using Docker, ensure the PostgreSQL container is running (`docker ps`). If running locally without Docker, ensure `DATABASE_URL` is set to `sqlite:///resume_data.db`.
- **Streamlit App Blank:** Hard refresh the browser (Ctrl+F5 or Cmd+Shift+R) to clear out cached custom CSS.

---

<div align="center">
  <p>Built with ❤️ by Ashwath & Anand.</p>
</div>
