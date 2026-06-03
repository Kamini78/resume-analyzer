from fastapi import APIRouter, File, Form, UploadFile
from typing import Annotated
from app.services.extractor import extract_text
from app.services.analyzer import analyze_multiple

router = APIRouter()

@router.post("/analyze")
async def analyze_resumes(
    job_description: Annotated[str, Form()],
    resumes: Annotated[list[UploadFile], File()],
):
    parsed = []
    for upload in resumes:
        content = await upload.read()
        try:
            text = extract_text(content, upload.filename)
            parsed.append({"filename": upload.filename, "text": text})
        except ValueError as e:
            raise Exception(str(e))

    results = await analyze_multiple(parsed, job_description)

    return {
        "total": len(results),
        "averageScore": round(
            sum(r.get("overallScore", 0) for r in results) / len(results), 1
        ),
        "candidates": results
    }