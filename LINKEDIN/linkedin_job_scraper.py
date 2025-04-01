import pandas as pd
import asyncio
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
import time
from time import sleep
import html2text
from LLMS.gemni_call import GeminiLLM
from rich.console import Console
from rich.progress import Progress
from rich.console import Console
from rich.table import Table
from rich.panel import Panel 
from rich.prompt import Prompt
from random import randint
import json
import re
import os
import csv  # new import
import config  # new import to load configuration
import smtplib
import zipfile
import fitz
from email.message import EmailMessage

gemini = GeminiLLM()

class ResumeConverter:
    def __init__(self, cv_filename):
        self.cv_filename = cv_filename
        self.gemini = GeminiLLM()
    
    def pdf_to_markdown(self, pdf_path):
        pdf_document = fitz.open(pdf_path)
        markdown_text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text = page.get_text("text")
            markdown_text += f"# Page {page_num + 1}\n\n{text}\n\n"
        return markdown_text
    
    def convert(self):
        markdown_text = self.pdf_to_markdown(self.cv_filename)
        atr_ready_converter_prompt = f"""
            # CV to ATS-Compliant Resume Conversion

            ## Objective
            Convert the following markdown CV into an ATS-compliant resume. The output must be in clean markdown format and follow the structure and guidelines below.

            ## Input Markdown CV
            {markdown_text}

            ## Conversion Guidelines

            ### Structure
            1. **Header**  
            - Full name  
            - Contact information

            2. **Professional Summary**  
            - A brief overview of professional background and core strengths.

            3. **Core Competencies**  
            - A categorized list of technical skills.

            4. **Professional Experience**  
            - List positions in reverse chronological order.  
            - Use bullet points with quantifiable achievements and active language.

            5. **Education**  
            - Include degrees, institutions, and dates.

            6. **Certifications**  
            - List relevant certifications with dates.

            7. **Additional Sections**  
            - Include languages and organizational skills if applicable.

            ### Key Requirements
            - Use standard ATS-friendly headers (e.g., "Professional Experience" instead of "EXPERIENCE").  
            - Emphasize quantifiable metrics (e.g., "Reduced test execution time by 35%").  
            - Consolidate technical skills into a keyword-rich list.  
            - Remove icons, special characters, and extraneous details.  
            - Ensure consistent date formats (e.g., "Dec 2021 – Present").  
            - Prioritize active verbs and concise phrasing.

            ### Instructions
            - Retain all technical details, tools, and achievements from the original CV.
            - Optimize for readability and ATS parsing.
            - Provide the final resume in markdown format only.
            """
        converted_md = self.gemini.run(atr_ready_converter_prompt)
        return converted_md

class LinkedInJobScraper:
    def __init__(self, job_title: str, job_location: str):
        self.job_title = job_title
        self.job_location = job_location
        self.counter = 0
        self.console = Console()
        self.playwright = None
        self.browser = None

    def start_browser(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch()

    def close_browser(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def create_table(self) -> Table:
        table = Table(title=f"{self.job_title} jobs in {self.job_location}")
        table.add_column("Title")
        table.add_column("Location")
        table.add_column("Company")
        table.add_column("Url", overflow="fold")
        return table

    def scrape_page(self):
        page = self.browser.new_page()
        url = (f"https://www.linkedin.com/jobs/search/?&keywords={self.job_title}"
               f"&location={self.job_location}&refresh=true&start={self.counter}")
        page.goto(url)
        job_cards = page.locator("li").all()
        jobs = []
        table = self.create_table()

        for card in job_cards:
            title_locator = card.locator(".base-search-card__title")
            location_locator = card.locator(".job-search-card__location")
            company_locator = card.locator(".base-search-card__subtitle a")
            link_locator = card.locator(".base-card__full-link")

            if (title_locator.count() > 0 and location_locator.count() > 0 and
                company_locator.count() > 0 and link_locator.count() > 0):
                title = title_locator.first.inner_html().strip()
                location = location_locator.first.inner_html().strip()
                company = company_locator.first.inner_html().strip()
                link = link_locator.get_attribute("href")
                jobs.append({
                    "Title": title,
                    "Location": location,
                    "Company": company,
                    "Url": link
                })
                table.add_row(title, location, company, link)

        page.close()
        self.console.print(table)
        return jobs

    def save_to_csv(self, jobs):
        import os
        os.makedirs("CSVS", exist_ok=True)  # ensure CSVS folder exists
        csv_file = os.path.join("CSVS", "linkedin_jobs.csv")
        with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Title", "Location", "Company", "Url"])
            writer.writeheader()
            for job in jobs:
                writer.writerow(job)
        self.console.print(Panel(f"Jobs saved to {csv_file}", title="Success"))

    def run(self):
        self.start_browser()
        all_jobs = []
        try:
            with Progress() as progress:  # new progress indicator
                task = progress.add_task("[green]Scraping pages...", total=3)
                for _ in range(3):
                    jobs = self.scrape_page()
                    all_jobs.extend(jobs)
                    self.counter += 25
                    sleep(randint(1, 10))
                    progress.advance(task)
        finally:
            self.close_browser()
        self.save_to_csv(all_jobs)

class JobMatcher:
    """
    A class to analyze a resume in Markdown format and return a match score,
    statistical insights, and recommendations in JSON format using gemini.run.
    """
    def __init__(self, gemini):
        """
        Initialize the JobMatcher with a gemini object.

        Parameters:
        - gemini: An object or module that provides the `run(prompt: str) -> str` method.
        """
        self.gemini = gemini

    def match_job_json(self, resume_md: str, job_md: str) -> dict:
        # Construct an enhanced prompt that instructs the resume analysis including statistics.
        prompt = f"""
        You are an expert resume analyzer. Given the resume in Markdown format below, analyze the candidate's qualifications for a Cloud Technical Lead role.

        Resume:
        {resume_md}
        
        Job to Match:
        {job_md}
        
        
        
        Your task is to output only a valid JSON (encapsulated in ```json and ```) object with the following exact structure and no additional text:

        {{
        "match_score": <integer from 0 to 100>,
        "statistics": {{
            "total_experience_years": <number of years of professional experience inferred from the resume>,
            "key_skills_count": <number of key competencies mentioned in the 'Core Competencies' section>,
            "automation_experience_percentage": <percentage from 0 to 100 representing the candidate's focus on test automation and QA relative to other areas>
        }},
        "recommendations": "<suggestions for further improvement or enhancement of the candidate's skill set to match the job role>"
        }}

        Use relevant statistical insights from the resume to determine the match score and calculate the values. Do not include any commentary or additional text outside of the JSON object.


        """


        # Call the gemini.run function to process the prompt.
        result = self.gemini.run(prompt)
        Console().print(result)

        # Attempt to parse the result as JSON.
        try:
            ### replace capital JSON to json
            result = re.sub(r"JSON", "json", result)
            ## keep within ```json ... ``` for JSON parsing or ```JSON ... ``` for case-insensitive parsing
            result = re.search(r"```json(.*?)```", result, re.DOTALL).group(1)

            json_result = json.loads(result)
            return json_result
        except json.JSONDecodeError as e:
            return {"match_score": 0, "statistics": {}, "recommendations": "Parsing error: " + str(e)}


class LinkedInJobPageScraper:
    def __init__(self, url: str):
        self.url = url

    async def extract_job_details_md(self, page) -> str:
        # Converted from sync to async calls
        await page.wait_for_selector('.top-card-layout__title')
        job_title = await page.text_content('.top-card-layout__title') or "N/A"
        company = await page.text_content('.topcard__org-name-link') or "N/A"
        location = await page.text_content('.topcard__flavor--bullet') or "N/A"
        posting_date = await page.text_content('.posted-time-ago__text') or "N/A"
        try:
            applicant_count = await page.text_content('.num-applicants__caption') or "N/A"
        except Exception:
            applicant_count = "N/A"
        try:
            experience_temp = await page.text_content('.show-more-less-html__markup p:first-of-type')
            experience = experience_temp if experience_temp else "N/A"
        except Exception:
            experience = "N/A"
        full_description = await page.text_content('.show-more-less-html__markup') or "N/A"

        criteria_elements = await page.query_selector_all('.description__job-criteria-list .description__job-criteria-item')
        criteria_list = []
        for elem in criteria_elements:
            header_elem = await elem.query_selector('h3.description__job-criteria-subheader')
            value_elem = await elem.query_selector('span.description__job-criteria-text')
            header = await header_elem.text_content() if header_elem else ""
            value = await value_elem.text_content() if value_elem else ""
            if header and value:
                criteria_list.append((header.strip(), value.strip()))

        md_lines = [
            f"# {job_title.strip()}",
            "",
            f"**Company:** {company.strip()}",
            f"**Location:** {location.strip()}",
            f"**Posted:** {posting_date.strip()}",
            f"**Applicants:** {applicant_count.strip()}",
            f"**Experience:** {experience.strip()}",
            "",
            "## Job Description",
            full_description.strip(),
            "",
            "## Job Criteria"
        ]
        for header, value in criteria_list:
            md_lines.append(f"- **{header}:** {value}")

        return "\n".join(md_lines)

    async def scrape(self) -> None:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(self.url)
            job_md = await self.extract_job_details_md(page)
            await browser.close()
            return job_md

class LinkedInCrawler:
    def __init__(self, csv_path=os.path.join("CSVS", "linkedin_jobs.csv"), resume_md="./CV/AnupSahoo_GenAI_Automation_1.0.md",job_count=20,location="Europe"):
        # Initialize variables and locators
        self.csv_path = csv_path
        self.resume_md = resume_md
        self.job_count = job_count
        self.location = location
        self.see_more_xpath = '//*[@id="main-content"]/section[1]/div/div/section[1]/div/div/section/button[1]'
        self.close_icon_xpath = '//*[@id="base-contextual-sign-in-modal"]/div/section/button/icon'
        
    def load_urls(self):
        # Open the CSV file and get the "Url" column
        data = pd.read_csv(self.csv_path)
        return data["Url"][0:self.job_count].tolist()

    async def run(self):
        urls = self.load_urls()
        results = []  # initialize the results list to store job md and analysis
        console = Console()
        with Progress() as progress:
            task = progress.add_task("Scraping LinkedIn jobs...", total=len(urls))
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                for url in urls:
                    await page.goto(url)
                    await asyncio.sleep(5)  # Wait for page to load
                    await page.keyboard.press("Escape")
                    
                    if await page.query_selector(self.see_more_xpath):
                        await page.click(self.see_more_xpath)
                        await asyncio.sleep(5)  # Wait for more content to load
                        job_scraper = LinkedInJobPageScraper(url)
                        job_md = await job_scraper.scrape()
                        console.print(job_md)
                        
                        # Extract Company, Location, and Job Description from job_md
                        lines = job_md.splitlines()
                        company_extracted = "N/A"
                        location_extracted = "N/A"
                        job_description_extracted = "N/A"
                        if len(lines) > 3:
                            m_company = re.search(r"\*\*Company:\*\*\s*(.*)", lines[2])
                            if m_company:
                                company_extracted = m_company.group(1).strip()
                            m_location = re.search(r"\*\*Location:\*\*\s*(.*)", lines[3])
                            if m_location:
                                location_extracted = m_location.group(1).strip()
                        try:
                            idx = lines.index("## Job Description")
                            if idx + 1 < len(lines):
                                job_description_extracted = lines[idx + 1].strip()
                        except ValueError:
                            pass
                        
                        # Job Matcher
                        matcher = JobMatcher(gemini)
                        analysis_result = matcher.match_job_json(self.resume_md, job_md)
                        for key, value in analysis_result.items():
                            console.print(f"[bold]{key}[/bold]: {value}")
                        
                        # Save job_md and analysis_result details to results list with additional columns
                        results.append({
                            "url": url,
                            "job_md": job_md,
                            "Company": company_extracted,
                            "Location": location_extracted,
                            "Job Description": job_description_extracted,
                            "match_score": analysis_result.get("match_score"),
                            "total_experience_years": analysis_result.get("statistics", {}).get("total_experience_years"),
                            "key_skills_count": analysis_result.get("statistics", {}).get("key_skills_count"),
                            "automation_experience_percentage": analysis_result.get("statistics", {}).get("automation_experience_percentage"),
                            "recommendations": analysis_result.get("recommendations")
                        })
                    
                    progress.update(task, advance=1)

                await browser.close()
        # Write results to CSV file after processing all URLs.
        os.makedirs("CSVS", exist_ok=True)  # ensure CSVS folder exists for output CSV
        output_path = os.path.join("CSVS", f"job_analysis_results_{self.location}.csv")
        pd.DataFrame(results).to_csv(output_path, index=False)

def zip_csv_files():
    """Zip all CSV files in the CSVS folder into archive 'csv_files.zip'."""
    zip_filename = os.path.join("CSVS", "csv_files.zip")
    with zipfile.ZipFile(zip_filename, "w") as zipf:
        for foldername, _, filenames in os.walk("CSVS"):
            for filename in filenames:
                if filename.endswith(".csv"):
                    filepath = os.path.join(foldername, filename)
                    zipf.write(filepath, arcname=filename)
    return zip_filename

def send_email(zip_file_path):
    """Send an email with the ZIP file as attachment using credentials from config."""
    # Use config.USERNAME and config.PASSWORD for both sender and receiver.
    sender_email = config.USERNAME
    receiver_email = config.USERNAME
    
    msg = EmailMessage()
    msg["Subject"] = "CSV Files Archive"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content("Please find attached the zipped CSV files.")
    
    # Read the ZIP file data and add it as an attachment.
    with open(zip_file_path, "rb") as f:
        zip_data = f.read()
    msg.add_attachment(zip_data, maintype="application", subtype="zip", filename="csv_files.zip")
    
    # Connect to the SMTP server. Example using Gmail.
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(config.USERNAME, config.PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    ## create CSVS folder if not exist, if exist then clear all files
    os.makedirs("CSVS", exist_ok=True)
    for file in os.listdir("CSVS"):
        os.remove(os.path.join("CSVS", file))    
    ## URL EXTRACTION
    resume_pdf = "./CV/AnupSahoo_GenAI_Automation_1.0.pdf"
    resume_md = resume_pdf.replace(".pdf", ".md")
    if not os.path.exists(resume_md):
        ## convert resume
        converter = ResumeConverter(resume_pdf)
        result = converter.convert()
        ## save to file
        with open(resume_md, "w") as f:
            f.write(result)
    else:
        console = Console()
        console.print(f"[yellow]Skipping conversion. File already exists: {resume_md}[/yellow]")
    
    # Use configuration values for job title, locations, and number of jobs
    job_title = config.JOB_TITLE
    locations = config.LOCATIONS
    num_jobs = config.NUM_JOBS

    for job_location in locations:
        scraper = LinkedInJobScraper(job_title, job_location)
        scraper.run()
        
        ## CRAWLER
        scraper = LinkedInCrawler(resume_md=resume_md, job_count=num_jobs, location=job_location)
        asyncio.run(scraper.run())
    
    # Zip CSV files and email them    
    zip_path = zip_csv_files()
    send_email(zip_path)


