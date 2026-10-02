import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from pydantic import BaseModel
from pypdf import PdfReader


# ======================================
# Load environment variables
# ======================================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

model = "openai/gpt-oss-120b"


# ======================================
# FastAPI
# ======================================

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======================================
# Resume Models
# ======================================

class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    description: str | None = None
    skills_used: list[str] = []


class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    total_experience_years: float | None = None

    skills: list[str] = []
    experiences: list[Experience] = []
    education: list[str] = []
    projects: list[str] = []
    certifications: list[str] = []


resume_schema = Resume.model_json_schema()


# ======================================
# Chat Request
# ======================================

class ChatRequest(BaseModel):
    question: str


# ======================================
# Read PDF
# ======================================

def read_pdf(file_path: Path):

    if not file_path.exists():
        raise FileNotFoundError(
            f"Resume file not found: {file_path}"
        )

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    if not text.strip():
        raise ValueError(
            "Could not extract text from the resume PDF."
        )

    return text


# ======================================
# Parse Resume
# ======================================

def parse_resume(resume_text):

    system_prompt = f"""
You are an expert resume parser.

Extract information from the resume based on its meaning,
not only based on exact section headings.

Return ONLY valid JSON matching this schema:

{json.dumps(resume_schema, indent=2)}

Important rules:

1. Do not invent information.
2. If a value is not available, return null.
3. If a list has no information, return an empty list.
4. Include internships inside experiences.
5. Extract skills mentioned across the entire resume.
"""

    user_prompt = f"""
Parse the following resume:

{resume_text}
"""

    response = client.chat.completions.create(
        model=model,

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        response_format={
            "type": "json_object"
        }
    )

    raw_output = response.choices[0].message.content

    print("RESUME PARSER RESPONSE:")
    print(raw_output)

    data = json.loads(raw_output)

    resume = Resume(**data)

    return resume


# ======================================
# Ask Candidate
# ======================================

def ask_candidate(question: str, resume: Resume):

    system_prompt = f"""
You are an AI assistant representing a job candidate.

Below is everything you know about the candidate:

{resume.model_dump_json(indent=2)}

Rules:

1. Answer only using this information.
2. Never hallucinate.
3. If information is unavailable, say:
"I don't have enough information to answer that."
4. Be professional.
5. Answer as if HR is interviewing this candidate.
"""

    response = client.chat.completions.create(

        model=model,

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    answer = response.choices[0].message.content

    print("AI ANSWER:")
    print(answer)

    return answer


# ======================================
# Home
# ======================================

@app.get("/")
def home():

    return {
        "message": "AI Candidate API is running"
    }


# ======================================
# Chat
# ======================================

@app.post("/chat")
def chat(request: ChatRequest):

    try:

        print("\n==============================")
        print("QUESTION:", request.question)
        print("==============================")

        # Find resume relative to this Python file
        resume_path = Path(__file__).parent / "my_resume.pdf"

        print("Resume path:", resume_path)

        # Read PDF
        resume_text = read_pdf(resume_path)

        print("Resume extracted successfully.")

        # Parse resume
        resume = parse_resume(resume_text)

        print("Resume parsed successfully.")

        # Ask AI
        answer = ask_candidate(
            request.question,
            resume
        )

        print("Chat completed successfully.")

        return {
            "answer": answer
        }

    except Exception as e:

        print("\n==============================")
        print("ERROR:")
        print(str(e))
        print("==============================\n")

        return {
            "error": str(e)
        }