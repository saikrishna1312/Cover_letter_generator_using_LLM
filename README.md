# Cover Letter Generator
## Project Overview
The Cover Letter Generator is an AI-powered application that dynamically generates personalized cover letters by extracting key information from a resume and a job posting. The project leverages natural language processing (NLP) and large language models (LLaMA via ChatGroq) to automatically match skills, experience, and education from the resume with job requirements.

This tool is designed to streamline the cover letter writing process by automating the generation of high-quality cover letters based on job descriptions and user resumes.

## Features
  - Resume Processing: Extracts key information such as name, education, skills, and experience from .docx or .pdf resumes.
  - Job Posting Scraping: Scrapes job descriptions from a provided job URL using BeautifulSoup.
  - AI-Powered Cover Letter Generation: Uses LLaMA (llama-3.1-70b-versatile) model to generate personalized cover letters based on the extracted resume information and job description.
  - Streamlit UI: Provides an intuitive interface for users to upload their resume and input a job posting URL.

## Technologies Used
  Programming Language: Python
  
## Libraries/Frameworks: 
  - docx, PyMuPDF: Resume parsing and processing
  - BeautifulSoup, requests: Web scraping for job description extraction
  - ChatGroq: Used LLaMa model from ChatGroq for the prompt and cover letter generation
  - Streamlit: Front-end interface for user interaction
  - NLP: Natural Language Processing for text extraction and analysis
  - Environment: Deployed locally with Python and Streamlit

## Note:
Set Up Environment Variables: Create a .env file and add your ChatGroq API key:
GROQ_API_KEY=your_groq_api_key


## Usage
  Run the Streamlit Application: Start the Streamlit application to open the user interface.
  streamlit run cover_letter_generator.py
  
  Upload Resume:
  Upload your resume in .docx or .pdf format.
  
  Enter Job URL:
  Enter the URL of the job posting for which you want to generate a cover letter.
  
  Generate Cover Letter:
  Click the "Generate Cover Letter" button to receive a personalized cover letter based on your resume and job description.
