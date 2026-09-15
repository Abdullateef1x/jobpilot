# # from app.services.ai import cosine_similarity, generate_embedding, scale_match_score

# # test_text = "Experienced backend engineer skilled in Python, FastAPI, and PostgreSQL."


# # job_description = "Looking for a backend engineer with Python and PostgreSQL experience"

# # embedding = generate_embedding(test_text)

# # embedding_resume = generate_embedding(test_text)
# # embedding_job = generate_embedding(job_description)

# # similarity = cosine_similarity(embedding_resume, embedding_job)

# # score = scale_match_score(0.8008)

# # print(f"Type: {type(embedding)}")
# # print(f"Length: {len(embedding)}")
# # print(f"First 5 values: {embedding[:5]}")
# # print(f"Match Similarity Score: {similarity:.4f}")
# # print(f"Scale match score: {score}")


# import json

from app.services.ai import (
    cosine_similarity,
    generate_embedding,
    resume_to_text,
    scale_match_score,
)

# Your parsed resume data from the earlier test — paste the actual dict you got back
resume_data = {
    "skills": ["Python", "FastAPI", "SQLModel", "PostgreSQL", "JWT", "Cloudflare R2", "Git", "REST API design"],
    # ... rest of the parsed_data from your earlier successful test
}

resume_text = resume_to_text(resume_data)
resume_embedding = generate_embedding(resume_text)

# Paste the nurse job description text directly as a string here
nurse_jd = """Registered Nurse - Emergency Department
We are seeking a compassionate and skilled Registered Nurse to join our Emergency
Department team. The ideal candidate will provide direct patient care in a fast-paced
environment, triage incoming patients, administer medications, and collaborate with
physicians on treatment plans.

Requirements:
- Active RN license
- BLS and ACLS certification required
- 2+ years of emergency or critical care nursing experience
- Strong communication and patient assessment skills
- Ability to work rotating shifts including nights and weekends

Responsibilities include monitoring vital signs, wound care, IV insertion, patient
education, and maintaining accurate medical records in compliance with hospital
policy and HIPAA regulations."""

# Paste the detailed backend job description text directly as a string here
backend_jd = """Senior Backend Engineer - Python / FastAPI
We're looking for a Senior Backend Engineer to design and build scalable, secure
backend systems for our growing platform. You'll work primarily in Python, using
FastAPI to build REST APIs, and PostgreSQL for our core data layer.

Responsibilities:
- Design and implement RESTful APIs using Python and FastAPI
- Build and maintain data models and schemas using SQLModel or SQLAlchemy with
  PostgreSQL
- Implement secure authentication and authorization flows (JWT-based auth,
  role-based access control)
- Integrate third-party services (cloud storage such as S3/R2, AI/LLM APIs)
- Write clean, well-tested, maintainable code and participate in code review
- Debug and resolve issues across the backend stack
- Collaborate with frontend engineers on API design and contracts

Requirements:
- Strong proficiency in Python
- Experience with FastAPI, Flask, or Django
- Solid understanding of relational databases (PostgreSQL preferred) and ORM tools
- Experience designing and securing REST APIs, including authentication (JWT/OAuth2)
- Familiarity with cloud object storage (S3-compatible services) is a plus
- Experience integrating with external APIs, including AI/LLM providers, is a plus
- Comfortable working independently and following software engineering best
  practices (version control, testing, code review)

Nice to have:
- Experience with vector embeddings, semantic search, or AI-powered features
- Familiarity with deployment on platforms like Render, Railway, or similar"""

for label, jd_text in [("Nurse JD (mismatch)", nurse_jd), ("Backend JD (strong match)", backend_jd)]:
    jd_embedding = generate_embedding(jd_text)
    raw_score = cosine_similarity(resume_embedding, jd_embedding)
    scaled = scale_match_score(raw_score)
    print(f"{label}: raw={raw_score:.4f}, scaled={scaled}%")
