from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router  # ✅ Now imports correctly
import uvicorn

app = FastAPI(
    title="🔍 Advanced Internet Plagiarism Detector",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000", "*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router, prefix="/api/v1")  # ✅ Routes now work!

@app.get("/")
async def root():
    return {
        "🚀": "Plagiarism Detector API v2.0 ✅",
        "📤": "POST /api/v1/detect-plagiarism",
        "📊": "Streamlit: http://localhost:8501",
        "📖": "Docs: /docs",
        "✅": "ALL ROUTES LOADED!"
    }

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

    