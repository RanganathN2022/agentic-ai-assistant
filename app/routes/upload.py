from fastapi import APIRouter, UploadFile, File
import os
from app.services.rag_service import process_document

router = APIRouter(prefix="/upload", tags=["Upload"])

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    result = process_document(file_path, file.filename)

    return {
        "filename": file.filename,
        "message": result
    }