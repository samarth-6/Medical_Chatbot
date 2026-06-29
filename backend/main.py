import os
import asyncio
from contextlib import asynccontextmanager

print("MAIN.PY STARTED")
print("PORT =", os.getenv("PORT"))
print("DATABASE_URL EXISTS =", bool(os.getenv("DATABASE_URL")))
print("GEMINI_API_KEY EXISTS =", bool(os.getenv("GEMINI_API_KEY")))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException

from backend.models import ChatResponse
from backend.services.chat_orchestrator import ChatOrchestrator
from backend.db.document_repository import DocumentRepository
from backend.services.upload_service import UploadService
from backend.rag.indexer import DocumentIndexer
from backend.logger import logger

orchestrator = None
indexer = None
_startup_done = False
_startup_error = None


async def _init_services():
    global orchestrator, indexer, _startup_done, _startup_error
    try:
        print("Initializing ChatOrchestrator...")
        orchestrator = ChatOrchestrator()
        print("Initializing DocumentIndexer...")
        indexer = DocumentIndexer()
        print("Startup complete")
        _startup_done = True
    except Exception as e:
        _startup_error = str(e)
        print(f"STARTUP FAILED: {e}")
        import traceback
        traceback.print_exc()


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(_init_services())
    yield


app = FastAPI(title="Medical Multi-Agent Chatbot", lifespan=lifespan)
print("CREATING FASTAPI APP")


def _check_ready():
    if _startup_error:
        raise HTTPException(status_code=500, detail=f"Service failed to start: {_startup_error}")
    if not _startup_done:
        raise HTTPException(status_code=503, detail="Service is still starting up, please retry in a moment")


@app.get("/")
async def health():
    return {"status": "ok", "ready": _startup_done, "startup_error": _startup_error}


@app.get("/ready")
async def readiness():
    if _startup_error:
        raise HTTPException(status_code=500, detail=_startup_error)
    if not _startup_done:
        raise HTTPException(status_code=503, detail="Still initializing")
    return {"status": "ready"}


@app.get("/documents/{session_id}")
async def list_documents(session_id: str):
    return DocumentRepository.list_documents(session_id)


@app.post("/chat", response_model=ChatResponse)
async def chat(
    query: str = Form(...),
    mode: str = Form(...),
    session_id: str = Form(...),
):
    _check_ready()
    try:
        result = await orchestrator.chat(query=query, mode=mode, session_id=session_id)
        return result
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


async def _process_one_file(file: UploadFile, session_id: str) -> str:
    """Save + index a single file. Returns a status string."""
    if DocumentRepository.exists(session_id=session_id, filename=file.filename):
        return f"{file.filename} (already exists)"

    path = await UploadService.save_file(file, session_id)

    # index_file_async is fully async — no blocking the event loop
    await indexer.index_file_async(session_id=session_id, file_path=path)

    DocumentRepository.create(
        session_id=session_id,
        filename=file.filename,
        filepath=path,
    )

    return file.filename


@app.post("/upload")
async def upload_documents(
    session_id: str = Form(...),
    files: list[UploadFile] = File(...),
):
    _check_ready()

    print("UPLOAD HIT")
    print("SESSION:", session_id)
    print("FILES:", len(files))

    try:
        results = await asyncio.gather(
            *[_process_one_file(f, session_id) for f in files],
            return_exceptions=True,
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))

    uploaded = []
    errors = []
    for r in results:
        if isinstance(r, Exception):
            errors.append(str(r))
        else:
            uploaded.append(r)

    if errors:
        logger.error(f"Upload errors: {errors}")
        # Return partial success so the frontend knows what made it
        return {"uploaded": uploaded, "errors": errors}

    return {"uploaded": uploaded}


@app.delete("/documents/{session_id}/{filename}")
async def delete_document(session_id: str, filename: str):
    filepath = DocumentRepository.get_document(session_id, filename)

    if not filepath:
        raise HTTPException(status_code=404, detail="Document not found")

    DocumentRepository.delete_chunks(session_id, filename)
    DocumentRepository.delete(session_id, filename)

    loop = asyncio.get_event_loop()
    if os.path.exists(filepath):
        await loop.run_in_executor(None, os.remove, filepath)

    return {"status": "deleted"}
