import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
import docx
import fitz  # PyMuPDF
import re
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

# Helper Functions to clean text and read resume
def clean_text(text):
    text = re.sub(r'<[^>]*?>', '', text)
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def read_resume_from_docx(file):
    doc = docx.Document(file)
    resume_text = "\n".join([para.text for para in doc.paragraphs if para.text])
    return resume_text

def read_resume_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    resume_text = ""
    for page_num in range(doc.page_count):
        page = doc[page_num]
        resume_text += page.get_text("text")
    return resume_text

def extract_name_from_resume(resume_text):
    lines = resume_text.split("\n")
    return lines[0].strip()

def extract_education(resume_text):
    # Extract education section by identifying relevant keywords
    edu_keywords = ["education", "degree", "bachelor", "master", "MSc", "BE", "MBA"]
    for line in resume_text.split("\n"):
        if any(keyword.lower() in line.lower() for keyword in edu_keywords):
            return line.strip()
    return "Education details not found."

def extract_experience(resume_text):
    # Extract experience based on key phrases or section headers
    exp_keywords = ["experience", "intern", "work", "professional", "project"]
    experiences = []
    for line in resume_text.split("\n"):
        if any(keyword.lower() in line.lower() for keyword in exp_keywords):
            experiences.append(line.strip())
    return "\n".join(experiences[:5]) if experiences else "Experience details not found."

def extract_skills(resume_text):
    # Extract skills section by identifying relevant keywords
    skill_keywords = ["skills", "technologies", "tools", "programming", "languages"]
    skills = []
    start_extracting = False
    for line in resume_text.split("\n"):
        if any(keyword.lower() in line.lower() for keyword in skill_keywords):
            start_extracting = True
        if start_extracting:
            if line.strip():
                skills.append(line.strip())
            else:
                break
    return ", ".join(skills) if skills else "Skills not found."

# Function to scrape job posting webpage using BeautifulSoup
def scrape_job_posting(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # Get all visible text from the page
    page_text = soup.get_text(separator="\n")
    return clean_text(page_text)

# Chain class to handle LLM-based job extraction and cover letter generation
class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-70b-versatile")

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills`, and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_cover_letter(self, job, name, education, experience, skills):
        prompt_cover_letter = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### INSTRUCTION:
            Write a personalized cover letter for the given job role using my resume details:
            - Name: {name}
            - Education: {education}
            - Experience: {experience}
            - Skills: {skills}
            The cover letter should highlight my qualifications for the job role, explaining why I am a good fit for the position. Be sure to connect my experience and skills with the job requirements.
            ### COVER LETTER (NO PREAMBLE):
            """
        )
        chain_cover_letter = prompt_cover_letter | self.llm
        res = chain_cover_letter.invoke({
            "job_description": str(job),
            "name": name,
            "education": education,
            "experience": experience,
            "skills": skills
        })
        return res.content

# Streamlit UI setup
def create_streamlit_app():
    st.title("📄 Cover Letter Generator")

    # Upload resume
    uploaded_file = st.file_uploader("Upload your resume (.docx or .pdf)", type=["docx", "pdf"])
    url_input = st.text_input("Enter a Job Posting URL:")
    submit_button = st.button("Generate Cover Letter")

    if submit_button and uploaded_file and url_input:
        try:
            # Read Resume
            if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                resume_text = read_resume_from_docx(uploaded_file)
            elif uploaded_file.type == "application/pdf":
                resume_text = read_resume_from_pdf(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a .docx or .pdf file.")
                return

            # Extract relevant information from the resume
            name = extract_name_from_resume(resume_text)
            education = extract_education(resume_text)
            experience = extract_experience(resume_text)
            skills = extract_skills(resume_text)

            # Scrape job posting using BeautifulSoup
            job_posting_data = scrape_job_posting(url_input)

            # Extract job info
            chain = Chain()
            jobs = chain.extract_jobs(job_posting_data)
            
            # Generate cover letter for each job
            for job in jobs:
                cover_letter = chain.write_cover_letter(job, name, education, experience, skills)
                st.text_area("Generated Cover Letter", cover_letter, height=400)

        except Exception as e:
            st.error(f"An Error Occurred: {e}")
    elif not uploaded_file:
        st.warning("Please upload your resume to proceed.")
    elif not url_input:
        st.warning("Please enter the job posting URL.")

if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Cover Letter Generator", page_icon="📄")
    create_streamlit_app()
