from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, resumes

app = FastAPI(title="AI Resume Analyzer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["resumes"])

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Resume Analyzer is running!"}