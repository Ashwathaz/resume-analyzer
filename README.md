# Smart Resume AI

**Developed by: Ashwath & Anand**

---

## Project Overview
Smart Resume AI is an intelligent, AI-powered document analysis system designed to help job seekers optimize their resumes for Applicant Tracking Systems (ATS). Using Google's Gemini Pro model and Groq fallback, the application provides detailed feedback, scoring, and actionable recommendations to improve hiring chances.

## Key Features
-   **AI-Powered Analysis**: Instant feedback on resume content, formatting, and keyword matching.
-   **ATS Scoring**: Specific scoring algorithms to mimic real-world recruitment systems.
-   **Resume Builder**: Guided tool to create professional, ATS-friendly resumes.
-   **Interactive Dashboard**: Track improvements and submission history.
-   **Featured Companies**: Integrated database of top tech companies and giants.
-   **Admin Portal**: Secure management system for reviewing user submissions.
-   **Dynamic UI**: Premium dark mode interface with topographic backgrounds.

## Tech Stack
-   **Frontend**: Streamlit, HTML5, Vanilla CSS3 (Modern UI)
-   **Backend**: Python 3.11+, Pandas
-   **AI Engines**: Google Gemini Pro & Groq API (Fallback)
-   **Database**: PostgreSQL (Containerized) / SQLite (Local)
-   **DevOps**: Docker & Docker Compose

## Admin Access
To access the administrative dashboard, use the following default credentials (configurable via database):
-   **Email**: `supadmin1`
-   **Password**: `ZEUS999+`

## Setup Instructions

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Ashwathaz/AI_RESUME-ANALYZER
    cd AI_RESUME-ANALYZER
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    -   Create a `.env` file in the root directory.
    -   Add your API Keys:
        -   `GOOGLE_API_KEY=your_key`
        -   `GROQ_API_KEY=your_key`
        -   `DATABASE_URL=postgresql://admin:password@localhost:5432/resume_db`

4.  **Run the Application**
    ```bash
    # Local Development
    streamlit run app.py

    # Using Docker
    docker-compose up -d
    ```

