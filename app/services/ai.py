import json
import logging
import math
import uuid

import pymupdf as fitz
import requests
from groq import Groq
from sqlmodel import Session

from app.config import setting
from app.core.database import get_engine
from app.crud.application import update_application_match

logger = logging.getLogger(__name__)



def extract_text_from_bytes(file_bytes: bytes, content_type: str) -> str:
    if content_type == "application/pdf":
        doc = None
        try:
            # Attempt to open the PDF stream
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            
            text = ""
            for page in doc:
                text += str(page.get_text())
                
            return text
            
        except Exception as e:
            # Handle corrupt, password-protected, or malformed PDFs
            raise RuntimeError(f"Failed to parse PDF bytes: {e}") from e
            
        finally:
            # Ensure the document resource is properly closed if it was opened
            if doc is not None:
                doc.close()

    
    elif content_type == "text/plain":
        # simple decode
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            # Fallback for alternative encodings if utf-8 fails
            return file_bytes.decode("latin-1")

    else:
        raise ValueError(f"Unsupported file type: {content_type}")




def parse_resume(resume_text: str) -> dict:
    client = Groq(api_key=setting.GROQ_API_KEY)
    
    prompt = """You are an expert at extracting structured resume data.
 Always respond with valid JSON matching this exact structure: {
  "skills": [string] or [],
  "certificates": [string] or [],
  "education": [
    {
      "institution": string or null,
      "degree": string (e.g "B.Sc. Educational Technology") or null,
      "year": string or null
    }
  ] or [],
  "experience": [
    {
      "company": string or null,
      "role": string or null,
      "duration": string or null (e.g "2023 - Present"),
      "description": string or null
    }
  ] or [],
  "contact": {
    "email": string or null,
    "phone": string or null
  } or null          
} Return only the JSON object. No explanation, no markdown, no extra text."""
    
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "system", "content": prompt},             {
                "role": "user",
                "content": f"Extract the required fields from this text:\n\n{resume_text}"
            } ],
            
        response_format={"type": "json_object"},
        temperature=0.0

    )
    
    raw_output = response.choices[0].message.content

    if not raw_output:                                       # ← guard here, before the try
        raise ValueError("Groq returned an empty response")

    try:
        parsed = json.loads(raw_output)                      #  Pylance now knows it's str
        if not isinstance(parsed, dict):
            raise ValueError(f"Expected dict, got {type(parsed)}")  # noqa: TRY004
        
        return parsed
    
    except Exception as e:  # noqa: BLE001
        raise ValueError(f"LLM returned invalid structure: {e}\nRaw: {raw_output}")
    


def generate_embedding(text: str) -> list[float]:
    
    response = requests.post(
    "https://openrouter.ai/api/v1/embeddings",
    headers={
    "Authorization": f"Bearer {setting.OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    },
    json={
    "model": "openai/text-embedding-3-small",
    "input": text
    }
    )

    if response.status_code != 200:
        raise ValueError(f"HTTP error {response.status_code}: {response.text}")

    data = response.json()

    if "error" in data:
        error_msg = data["error"].get("message", "Unknown OpenRouter error")
        raise ValueError(f"OpenRouter API Error: {error_msg} | Raw JSON: {data}")

    try:
            return data["data"][0]["embedding"]
    except (KeyError, IndexError, TypeError)  as e:
            raise ValueError(f"Unexpected response structure: {e} | Raw JSON: {data}")


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))

    magnitude_a = math.sqrt(sum(a ** 2 for a in vec_a))
    magnitude_b = math.sqrt(sum(b ** 2 for b in vec_a))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
        

    return dot_product / (magnitude_a * magnitude_b)




def scale_match_score(raw_score: float, floor: float = setting.MATCH_SCORE_FLOOR , ceiling: float = setting.MATCH_SCORE_CEILING) -> float:
    clamped = max(floor, min(raw_score, ceiling))
    scaled = (clamped - floor) / (ceiling - floor) * 100
    return round(scaled, 1)


def resume_to_text(parsed_data: dict) -> str:
    skills = ", ".join(parsed_data.get("skills", []))
    
    experience_parts = []
    for exp in parsed_data.get("experience", []):
        role = exp.get("role") or ""
        company = exp.get("company") or ""
        description = exp.get("description") or ""

        experience_parts.append(f"{role} at {company}: {description}")
    experience_text = " ".join(experience_parts)

    education_part = []
    for edu in parsed_data.get("education", []):
        degree = edu.get("degree") or ""

        education_part.append(f"degree: {degree}")
    education_text = " ".join(education_part)

    certificates_part = []
    for cert in parsed_data.get("certificates", []):
        certificates_part.append(f"certificates: {cert}")
    certificates_text = " ".join(certificates_part)
    
    return f"Skills: {skills}\nExperience: {experience_text}\nEducation: {education_text}\nCertifcates{certificates_text}"





def generate_match_assessment(parsed_resume_data: dict, job_description: str) -> dict:
    client = Groq(api_key=setting.GROQ_API_KEY)



    prompt = """You are an expert at assessing resume data against a job description.
  Always respond with an accurate match score (0-100) and a detailed explanation for such match score with no sugarcoating. Return only a JSON object of the schema structure below.
   Scoring rnage (0-100): [Strictly follow this range and return a match base on the provided]:
-(0-30): Complete mismatch: Unrelated skillset or different industry
-(31-50): (Minimal match): lack of required tech stack or lacking basic skillsets or essential seniority level or required degree
-(51-70): (Moderate match): Matches standard core requirements or Less years of experience required   or Lack of specialised certificates
-(71-90): High alignment. Matches all mandatory criteria, key skills, and experience parameters. Demonstrates clear competency across almost all dimensions.
- [91 - 100]: Near-perfect alignment. Exceeds standard expectations. Fully satisfies all required and highly preferred specifications, stack tools, leadership depth, and domain-specific challenges.
   [Output schema]: {
    "match_score": float or null,
    "match_explanation": string or null
        }"""


    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "system", "content": prompt},             {
                    "role": "user",
                    "content": f"Assess this candidate resume:\n\n{parsed_resume_data} against this description:\n\n{job_description}"
                } ],
                
            response_format={"type": "json_object"},
            temperature=0.0

        )

        raw_output = response.choices[0].message.content

        if not raw_output:                                       # ← guard here, before the try
            raise ValueError("Groq returned an empty response")


        parsed = json.loads(raw_output)
        if not isinstance(parsed, dict):
            raise ValueError(f"Expected dict, got {type(parsed)}")  # noqa: TRY004
            
        return parsed
        
    except Exception as e:  # noqa: BLE001
        try:

            resume_text = resume_to_text(parsed_resume_data)
            resume_embedding = generate_embedding(resume_text)
            jd_embedding = generate_embedding(job_description)
            raw_score = cosine_similarity(resume_embedding, jd_embedding)
            scaled = scale_match_score(raw_score)

            return {
            "match_score": scaled,
            "match_explanation": "Fallback; Calculated manually via embedding, due to LLM timeout or extraction failure"
        }
        except Exception as fallbackerror:  # noqa: BLE001
            raise RuntimeError(f"Failed to generate fallback assessment: {fallbackerror}")  # noqa: TRY004
        

def process_application_scoring(application_id: uuid.UUID, user_id: int, parsed_resume_data: dict, job_description: str):
    engine = get_engine()
    with Session(engine) as session:
        assessment = generate_match_assessment(parsed_resume_data, job_description)
        update_application_match(session, application_id, user_id, assessment["match_score"], assessment["match_explanation"])


      