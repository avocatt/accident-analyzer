from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import shutil
import tempfile
from datetime import datetime
import uuid
from dotenv import load_dotenv

from services.ai_service import AIService
from services.document_processor import DocumentProcessor
from services.briefing_generator import BriefingGenerator
from models.analysis_result import AnalysisResult

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="LexIntake API",
    description="AI-powered Turkish traffic accident report analyzer",
    version="1.0.0"
)

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
allowed_origins = [
    frontend_url,
    "http://localhost:5173",  # Local development
    "https://lexintake.emreterzi.com",  # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ai_service = AIService()
doc_processor = DocumentProcessor()
briefing_generator = BriefingGenerator()

# Ensure temp directory exists
TEMP_DIR = os.getenv("TEMP_DIR", "/app/temp_uploads")
# For local development, use a local temp directory
if not os.path.exists("/app"):
    TEMP_DIR = os.path.join(os.getcwd(), "temp_uploads")
os.makedirs(TEMP_DIR, exist_ok=True)


class AnalysisRequest(BaseModel):
    session_id: str
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    additional_notes: Optional[str] = None


@app.get("/")
async def root():
    return {
        "message": "LexIntake API is running",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/analyze")
async def analyze_documents(
    accident_report: UploadFile = File(..., description="Kaza Tespit Tutanağı (PDF or Image)"),
    photos: List[UploadFile] = File(None, description="Additional accident photos"),
    client_name: Optional[str] = Form(None),
    client_email: Optional[str] = Form(None),
    additional_notes: Optional[str] = Form(None)
):
    """
    Analyze traffic accident documents and generate attorney briefing
    """
    session_id = str(uuid.uuid4())
    temp_files = []
    
    try:
        # Create session directory
        session_dir = os.path.join(TEMP_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Save main accident report
        report_path = os.path.join(session_dir, f"report_{accident_report.filename}")
        with open(report_path, "wb") as buffer:
            shutil.copyfileobj(accident_report.file, buffer)
        temp_files.append(report_path)
        
        # Save additional photos if provided
        photo_paths = []
        if photos:
            for idx, photo in enumerate(photos):
                if photo.filename:  # Check if file has content
                    photo_path = os.path.join(session_dir, f"photo_{idx}_{photo.filename}")
                    with open(photo_path, "wb") as buffer:
                        shutil.copyfileobj(photo.file, buffer)
                    photo_paths.append(photo_path)
                    temp_files.append(photo_path)
        
        # Process documents
        processed_report = doc_processor.process_document(report_path)
        processed_photos = [doc_processor.process_image(path) for path in photo_paths]
        
        # Analyze with AI
        analysis_result = await ai_service.analyze_accident(
            report_content=processed_report,
            photo_contents=processed_photos,
            additional_context={
                "client_name": client_name,
                "additional_notes": additional_notes
            }
        )
        
        # Generate briefing
        briefing_html = briefing_generator.generate_html_briefing(analysis_result)
        briefing_pdf = briefing_generator.generate_pdf_briefing(analysis_result)
        
        # Prepare response
        response = {
            "session_id": session_id,
            "status": "success",
            "analysis": analysis_result.dict(),
            "briefing_html": briefing_html,
            "briefing_pdf_available": True,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return JSONResponse(content=response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    finally:
        # Clean up temporary files
        try:
            if session_id and os.path.exists(os.path.join(TEMP_DIR, session_id)):
                shutil.rmtree(os.path.join(TEMP_DIR, session_id))
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")


@app.get("/api/briefing/{session_id}/pdf")
async def get_briefing_pdf(session_id: str):
    """
    Retrieve PDF briefing for a session
    """
    # This would retrieve the PDF from temporary storage
    # For MVP, we'll generate it on-demand
    return {"message": "PDF generation endpoint", "session_id": session_id}


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """
    Manually delete session data
    """
    session_dir = os.path.join(TEMP_DIR, session_id)
    if os.path.exists(session_dir):
        shutil.rmtree(session_dir)
        return {"message": "Session data deleted", "session_id": session_id}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)