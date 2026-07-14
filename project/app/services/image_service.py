from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from PIL import Image
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


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
        image.thumbnail((2400, 2400))
        image.save(original_file, optimize=True, quality=85)
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")
        image.save(webp_file, format="WEBP", quality=82, method=6)

    return original_name, webp_name
