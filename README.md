# Watermark Remover (Photo + Video)

Aplikasi Python untuk menghapus watermark pada gambar dan video, dijalankan sebagai webserver FastAPI via **uvicorn**.

## Fitur
- Upload gambar (`jpg/png/webp/...`) dan hapus watermark dengan inpainting.
- Upload video (`mp4/mov/mkv/...`) dan hapus watermark frame-by-frame.
- Untuk video, deteksi watermark dibuat agar bisa mengikuti watermark bergerak dan blink/animasi menggunakan:
  - deteksi kandidat teks di tiap frame,
  - tracking antar frame berbasis IoU + prediksi velocity,
  - toleransi `missed frames` agar tetap melacak saat watermark sempat hilang (blink).

> Catatan: ini pendekatan heuristik (best effort), hasil tergantung kompleksitas video.

## Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Buka `http://localhost:8000`.

## Endpoint API
- `GET /` halaman upload.
- `POST /remove` multipart form-data file upload, response file hasil cleaning.
