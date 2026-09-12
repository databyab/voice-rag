from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import shutil
from pathlib import Path
from app.config import settings
from app.rag.pipeline import rag_service
from app.utils.logging import logger

router = APIRouter(prefix="/api", tags=["Documents"])

class IngestResponse(BaseModel):
    filename: str
    chunks_created: int
    status: str

class DocumentInfo(BaseModel):
    filename: str
    file_type: str
    chunks_count: int
    total_pages: int

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}

@router.post("/documents/upload", response_model=IngestResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename cannot be empty.")

    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file_ext}'. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    os.makedirs(settings.DOCUMENTS_DIR, exist_ok=True)
    target_path = os.path.join(settings.DOCUMENTS_DIR, file.filename)

    try:
        logger.info(f"Saving uploaded file to {target_path}...")
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Ingesting document '{file.filename}' into RAG database...")
        stats = rag_service.ingest_file(target_path)
        return IngestResponse(**stats)
    except Exception as e:
        logger.error(f"Error processing document upload '{file.filename}': {e}")
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {str(e)}")

@router.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    try:
        docs = rag_service.list_indexed_documents()
        return [DocumentInfo(**d) for d in docs]
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=f"Could not retrieve document list: {str(e)}")
