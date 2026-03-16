from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.processing import remove_watermark_from_image, remove_watermark_from_video

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Watermark Remover", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/remove")
async def remove(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    ext = Path(file.filename).suffix.lower()
    input_name = f"{uuid.uuid4().hex}{ext}"
    input_path = UPLOAD_DIR / input_name

    with input_path.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    try:
        if ext in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
            output_path = OUTPUT_DIR / f"cleaned-{input_name.rsplit('.', 1)[0]}.png"
            remove_watermark_from_image(input_path, output_path)
            media_type = "image/png"
        elif ext in {".mp4", ".mov", ".mkv", ".avi", ".webm"}:
            output_path = OUTPUT_DIR / f"cleaned-{input_name.rsplit('.', 1)[0]}.mp4"
            remove_watermark_from_video(input_path, output_path)
            media_type = "video/mp4"
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Processing failed: {exc}") from exc

    return FileResponse(
        output_path,
        filename=output_path.name,
        media_type=media_type,
    )
