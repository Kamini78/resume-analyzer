import json
import anthropic
from app.core.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

PROMPT = """You are an expert HR analyst.
Analyze this resume against the job description and return ONLY valid JSON, no markdown, no extra text.

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
  "matchedSkills": ["React", "Python"],
  "missingSkills": ["Docker", "AWS"],
  "experience": "5 years at Company X",
  "education": "B.Sc Computer Science",
  "strengths": ["Strong Python skills", "Good experience"],
  "improvements": ["Missing cloud skills", "No leadership experience"],
  "summary": "A strong candidate with good technical skills."
}}"""

async def analyze_resume(resume_text: str, job_description: str, filename: str) -> dict:
    prompt = PROMPT.format(jd=job_description, resume=resume_text[:3000], filename=filename)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text.replace("```json", "").replace("```", "").strip()
    result = json.loads(raw)
    result["fileName"] = filename
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