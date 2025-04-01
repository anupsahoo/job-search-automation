```markdown
## Job Search Automation Tool

Job Search Automation is an advanced tool that leverages Large Language Models (LLMs) to streamline your job search process. It automates scanning job listings, matches your resume against job descriptions, and even curates your resume and cover letter—all in one click. Whether you're overwhelmed by the daily influx of job postings or need a finely tuned ATS-compliant resume, this tool is designed to save you time and effort.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Components](#components)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)

## Features

- **Resume Conversion**  
  Convert your PDF resume into Markdown and optimize it to be ATS-compliant using LLM-based processing.
  
- **Job Scraping**  
  Scrape job listings from LinkedIn based on customizable job titles and locations using Playwright.
  
- **Job Matching & Analysis**  
  Analyze and match your resume against job descriptions to generate a match score, statistical insights, and actionable recommendations.
  
- **Asynchronous Job Page Scraping**  
  Extract detailed job information (title, company, location, description, etc.) from individual job pages asynchronously.
  
- **CSV Reporting & Email Notifications**  
  Save job data and analysis results to CSV files, compress them into a ZIP archive, and automatically email the archive.
  
- **Rich Command Line Interface**  
  Enjoy a visually enhanced CLI experience with progress bars, tables, and panels provided by the Rich library.

## Prerequisites

Before using the tool, ensure you have:

- **Python 3.7+** installed.
- Required Python libraries:
  - `pandas`
  - `asyncio`
  - `playwright`
  - `html2text`
  - `rich`
  - `json`
  - `re`
  - `smtplib`
  - `zipfile`
  - `fitz` (PyMuPDF)
- A valid GeminiLLM integration (or equivalent LLM API) available via the `LLMS.gemni_call` module.
- A configured `config.py` file with your SMTP credentials, job title, locations, and the number of jobs to scrape.

## Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd job-search-automation
   ```

2. **Install Dependencies**  
   It is recommended to create a virtual environment first.
   ```bash
   pip install -r requirements.txt
   ```
   *Ensure that `requirements.txt` lists all the necessary libraries mentioned above.*

3. **Set Up Configuration**  
   Create a `config.py` file in the project root with your specific settings. For example:
   ```python
   USERNAME = "your_email@gmail.com"
   PASSWORD = "your_email_password"
   JOB_TITLE = "Cloud Technical Lead"
   LOCATIONS = ["Europe", "USA", "Asia"]
   NUM_JOBS = 20
   ```

## Usage

1. **Prepare Your Resume**
   - Place your PDF resume in the `CV` directory.
   - On the first run, the tool will convert your PDF resume into a Markdown file and optimize it for ATS compliance. If the Markdown version already exists, the conversion will be skipped.

2. **Run the Automation Script**
   Execute the main script:
   ```bash
   python your_script.py
   ```
   The script will:
   - Convert your PDF resume to an ATS-compliant Markdown format.
   - Scrape LinkedIn for job listings based on your job title and specified locations.
   - Extract detailed job information and analyze it against your resume.
   - Save all results in CSV files under the `CSVS` directory.
   - Zip the CSV files and send them via email using your SMTP settings.

## Components

- **ResumeConverter**  
  Converts a PDF resume to Markdown and then to an ATS-compliant resume using GeminiLLM.

- **LinkedInJobScraper**  
  Scrapes job listings from LinkedIn and displays them in a formatted table using the Rich library.

- **JobMatcher**  
  Matches the ATS-compliant resume against job descriptions, outputting a JSON with match scores, statistics, and recommendations.

- **LinkedInJobPageScraper & LinkedInCrawler**  
  Extract detailed job descriptions and criteria asynchronously from individual job pages and compile the data.

- **Utility Functions**  
  - `zip_csv_files()`: Zips all CSV files in the `CSVS` folder.
  - `send_email()`: Sends the ZIP archive via email using your SMTP credentials.

## Customization

- **LLM Prompts**  
  Modify the conversion and job matching prompts in the code to better suit your needs.
  
- **Scraping Parameters**  
  Adjust the job title, location, and number of jobs in `config.py` or directly in the code to customize your search.
  
- **Output Formats**  
  Extend the functionality to support additional output formats or integrate with other systems as needed.

## Troubleshooting

- **Playwright Issues**  
  Ensure Playwright is installed and that the required browsers are set up:
  ```bash
  playwright install
  ```

- **LLM API Errors**  
  Verify that your GeminiLLM integration is active and that any required API keys or credentials are correctly configured.

- **Email Sending Problems**  
  Double-check the SMTP credentials in `config.py` and ensure your email provider supports SMTP access.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

Contributions are welcome! Fork the repository and submit a pull request with your improvements.

## Acknowledgments

- [Playwright](https://playwright.dev/python/) for browser automation.
- [Rich](https://github.com/willmcgugan/rich) for enhancing the CLI experience.
- GeminiLLM and other open-source tools that have made this project possible.

---

Happy job hunting and best of luck with your applications!
```

