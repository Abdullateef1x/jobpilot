import json

import fitz  # PyMuPDF
from groq import Groq

from app.config import setting


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
    