import json
import math
from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.ANTHROPIC_API_KEY)

def cosine_similarity(text1: str, text2: str) -> float:
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    return len(intersection) / math.sqrt(len(words1) * len(words2))

PROMPT = """You are an expert HR analyst.
Analyze this resume against the job description and return ONLY valid JSON, no markdown.

JOB DESCRIPTION:
{jd}

RESUME ({filename}):
{resume}

Return this exact JSON:
{{
  "name": "Full Name",
  "email": "email or N/A",
  "overallScore": 78,
  "skillsScore": 80,
  "experienceScore": 75,
  "educationScore": 70,
  "embeddingScore": {similarity_pct},
  "matchedSkills": ["React", "Python"],
  "missingSkills": ["Docker", "AWS"],
  "experience": "5 years at Company X",
  "education": "B.Sc Computer Science",
  "strengths": ["Strong Python skills"],
  "improvements": ["Missing cloud skills"],
  "summary": "A strong candidate."
}}"""

async def analyze_resume(resume_text: str, job_description: str, filename: str) -> dict:
    similarity = cosine_similarity(resume_text, job_description)
    similarity_pct = round(similarity * 100)
    prompt = PROMPT.format(
        jd=job_description,
        resume=resume_text[:3000],
        filename=filename,
        similarity_pct=similarity_pct
    )
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
    result = json.loads(raw)
    result["fileName"] = filename
    result["embeddingScore"] = similarity_pct
    return result

async def analyze_multiple(resumes: list, job_description: str) -> list:
    results = []
    for r in resumes:
        try:
            analysis = await analyze_resume(r["text"], job_description, r["filename"])
            results.append(analysis)
        except Exception as e:
            results.append({"fileName": r["filename"], "name": "Error", "overallScore": 0, "error": str(e)})
    results.sort(key=lambda x: x.get("overallScore", 0), reverse=True)
    return results