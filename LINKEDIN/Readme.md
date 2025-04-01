# LinkedIn Job Scraper and Resume Matcher

## Overview

This project automates the process of converting a resume from PDF to an ATS-compliant Markdown format, scraping job postings from LinkedIn based on specified job titles and locations, and analyzing the compatibility of the candidate’s resume with the job descriptions. The results are saved in CSV files, which are then compressed into a ZIP archive and emailed using SMTP.

## Features

- **Resume Conversion**
  - Converts a PDF resume to Markdown.
  - Utilizes an external GeminiLLM module for ATS-compliant formatting.

- **LinkedIn Job Scraping**
  - Employs Playwright for browser automation.
  - Extracts job details such as title, company, location, and URL.
  - Displays extracted job data in a formatted table.
  - Saves job data to CSV files.

- **Job Matching**
  - Analyzes the candidate’s resume against job descriptions.
  - Generates a JSON output containing a match score, experience statistics, and recommendations.

- **CSV Archival and Emailing**
  - Compresses all generated CSV files into a ZIP archive.
  - Sends the ZIP file as an email attachment using credentials specified in a configuration file.

## Dependencies

- Python 3.7 or later
- Required Python packages:
  - `pandas`
  - `asyncio`
  - `playwright`
  - `PyMuPDF` (imported as `fitz`)
  - `html2text`
  - `rich`
  - Standard libraries: `csv`, `smtplib`, `zipfile`, `os`, `json`, `re`
- Custom module: `LLMS.gemni_call` (ensure this module is accessible)
- A configuration file (`config.py`) containing:
  - `JOB_TITLE`
  - `LOCATIONS` (list of locations)
  - `NUM_JOBS`
  - `USERNAME`
  - `PASSWORD`

## Installation

1. **Clone the Repository**
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install Dependencies**
   ```bash
   pip install pandas
   pip install playwright
   pip install html2text
   pip install rich
   pip install PyMuPDF
   ```

## Playwright Setup
   ```bash
   playwright install
   ```

## How to Run

1. **Configuration**
   - Ensure the `config.py` file is properly set up with your job title, locations, number of jobs, and email credentials.

2. **Resume Conversion**
   - Place your PDF resume in the designated directory.
   - Run the resume conversion script to generate the Markdown file.

3. **Script Execution**
   - Execute the main script to start scraping LinkedIn job postings and matching them with your resume.

4. **Output**
   - The results will be saved in CSV files, compressed into a ZIP archive, and emailed to the specified address.

