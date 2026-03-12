FROM python:3.11.9

WORKDIR /app

# Install system dependencies including Tesseract OCR
# Install system dependencies
# - tesseract-ocr: For PDF text extraction
# - poppler-utils: For PDF processing
# - chromium & driver: For Selenium (Job Search)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    libpoppler-dev \
    chromium \
    chromium-driver \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLP models (Spacy & NLTK)
RUN python -m spacy download en_core_web_sm
RUN python -m nltk.downloader punkt stopwords wordnet omw-1.4

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
# Configure Selenium to use the installed Chromium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"] 