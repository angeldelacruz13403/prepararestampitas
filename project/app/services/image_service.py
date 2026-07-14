from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_PIXELS = 40_000_000
MAX_DIMENSION = 2400
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


def _is_allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_and_optimize_image(upload_dir: str, file: FileStorage) -> tuple[str, str | None]:
    if not file.filename:
        raise ValueError("Archivo vacío")
    if not _is_allowed(file.filename):
        raise ValueError("Formato no permitido")

    upload_path = Path(upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)

    safe = secure_filename(file.filename)
    ext = safe.rsplit(".", 1)[1].lower()
    base = f"{uuid4().hex}"
    original_name = f"{base}.{ext}"
    original_file = upload_path / original_name
    file.save(original_file)

    webp_name = f"{base}.webp"
    webp_file = upload_path / webp_name

    with Image.open(original_file) as image:
        if image.width * image.height > MAX_PIXELS:
            raise ValueError("Imagen demasiado grande")
        processed = image.convert("RGB") if image.mode not in ("RGB", "RGBA") else image.copy()
        processed.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
        processed.save(original_file, optimize=True, quality=85)
        processed.save(webp_file, format="WEBP", quality=82, method=6)

    return original_name, webp_name
