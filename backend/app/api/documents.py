import uuid
import shutil
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.db_models import Document, DocumentStatus
from app.models.schemas import DocumentOut
from app.services.parser import parse_file, ALLOWED_EXTENSIONS

router = APIRouter(prefix = "/documents", tags = ["documents"])

#Post/documents/upload

@router.post("/upload", response_model = DocumentOut)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Only accept: {','.join(ALLOWED_EXTENSIONS)}")
    
    doc_id = str(uuid.uuid4())
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    save_path = settings.UPLOAD_DIR / f"{doc_id}{ext}"

    size = 0 
    with save_path.open("wb") as f:
        while chunk := await file.read(1024 * 1024):  # đọc từng 1MB
            size += len(chunk)
            if size > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                save_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=413,
                    detail=f"File vượt quá {settings.MAX_FILE_SIZE_MB}MB"
                )
            f.write(chunk)

    # 3. Lưu metadata vào SQL Server
    doc = Document(
        id=doc_id,
        original_name=file.filename,
        file_path=str(save_path),
        file_type=ext,
        file_size=size,
        status=DocumentStatus.UPLOADED,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 4. Parse + embed chạy nền (không block response)
    background_tasks.add_task(_process_document, doc_id, save_path, file.filename)

    return doc


# ─────────────────────────────────────────
# GET /documents/
# ─────────────────────────────────────────
@router.get("/", response_model=list[DocumentOut])
def list_documents(db: Session = Depends(get_db)):
    return (
        db.query(Document)
        .order_by(Document.uploaded_at.desc())
        .all()
    )


# ─────────────────────────────────────────
# GET /documents/{doc_id}
# ─────────────────────────────────────────
@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")
    return doc


# ─────────────────────────────────────────
# DELETE /documents/{doc_id}
# ─────────────────────────────────────────
@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.get(Document, doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài liệu")

    # Xóa file vật lý
    Path(doc.file_path).unlink(missing_ok=True)

    # Xóa record trong DB
    db.delete(doc)
    db.commit()

    return {"message": f"Đã xóa '{doc.original_name}'", "id": doc_id}


# ─────────────────────────────────────────
# Background task: parse → (embed sau)
# ─────────────────────────────────────────
def _process_document(doc_id: str, file_path: Path, doc_name: str):
    """
    Chạy nền sau khi upload xong.
    Bước 1: parse file → lấy text       (làm ở đây)
    Bước 2: chunk + embed → Qdrant       (làm khi có ai_service)
    """
    # Tạo session DB riêng cho background task
    from app.core.database import SessionLocal

    db = SessionLocal()
    try:
        doc = db.get(Document, doc_id)
        if not doc:
            return

        # Parse
        doc.status = DocumentStatus.PARSING
        db.commit()

        text = parse_file(file_path)

        # TODO: gọi embed ở đây khi viết xong ai_service.py
        # from app.services.ai_service import chunk_and_embed
        # doc.status = DocumentStatus.INDEXING
        # db.commit()
        # count = chunk_and_embed(doc_id, doc_name, text)
        # doc.chunk_count = count
        # doc.indexed_at = datetime.utcnow()

        # Tạm thời mark indexed luôn sau khi parse xong
        doc.status = DocumentStatus.INDEXED
        doc.indexed_at = datetime.utcnow()
        db.commit()

        print(f"[OK] Parse xong: {doc_name} — {len(text)} ký tự")

    except Exception as e:
        doc = db.get(Document, doc_id)
        if doc:
            doc.status = DocumentStatus.FAILED
            db.commit()
        print(f"[ERROR] {doc_id}: {e}")
    finally:
        db.close()