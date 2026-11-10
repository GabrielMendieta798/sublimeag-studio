#!/usr/bin/env python3
"""Shared deterministic image utilities for Sublime AG Studio."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageColor, ImageOps


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FORMATS = SKILL_ROOT / "assets" / "templates" / "formats.json"
SUPPORTED_INPUT_SUFFIXES = {".png", ".jpg", ".jpeg"}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Se esperaba un objeto JSON en {path}")
    return data


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ensure_input_image(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"No existe el archivo de entrada: {path}")
    if path.suffix.lower() not in SUPPORTED_INPUT_SUFFIXES:
        raise ValueError(f"Formato no admitido: {path.suffix}. Usá PNG o JPG.")


def ensure_output_path(path: Path, overwrite: bool = False, suffix: str = ".png") -> None:
    if path.suffix.lower() != suffix:
        raise ValueError(f"La salida debe usar extensión {suffix}: {path}")
    if path.exists() and not overwrite:
        raise FileExistsError(f"La salida ya existe: {path}. Elegí otro nombre o usá --overwrite.")
    path.parent.mkdir(parents=True, exist_ok=True)


def parse_size(value: str) -> tuple[int, int]:
    try:
        width_text, height_text = value.lower().split("x", maxsplit=1)
        width, height = int(width_text), int(height_text)
    except (ValueError, AttributeError) as exc:
        raise ValueError("El tamaño debe expresarse como ANCHOxALTO, por ejemplo 1080x1350.") from exc
    if width <= 0 or height <= 0:
        raise ValueError("Las dimensiones deben ser positivas.")
    return width, height


def preset_data(name: str, formats_path: Path = DEFAULT_FORMATS) -> dict[str, Any]:
    formats = load_json(formats_path)
    if name not in formats:
        choices = ", ".join(sorted(formats))
        raise ValueError(f"Preset desconocido: {name}. Opciones: {choices}")
    data = formats[name]
    if not isinstance(data, dict) or not {"width", "height", "safe"} <= data.keys():
        raise ValueError(f"Preset incompleto en {formats_path}: {name}")
    return data


def resolve_dimensions(preset: str | None, size: str | None) -> tuple[int, int, dict[str, int]]:
    if bool(preset) == bool(size):
        raise ValueError("Indicá exactamente uno de --preset o --size.")
    if preset:
        data = preset_data(preset)
        safe = {key: int(value) for key, value in data["safe"].items()}
        return int(data["width"]), int(data["height"]), safe
    width, height = parse_size(size or "")
    margin = max(24, round(min(width, height) * 0.06))
    return width, height, {"top": margin, "right": margin, "bottom": margin, "left": margin}


def _background_rgba(value: str) -> tuple[int, int, int, int]:
    if value.lower() == "transparent":
        return 0, 0, 0, 0
    rgb = ImageColor.getrgb(value)
    return int(rgb[0]), int(rgb[1]), int(rgb[2]), 255


def fit_image(image: Image.Image, size: tuple[int, int], fit: str, background: str) -> Image.Image:
    normalized = ImageOps.exif_transpose(image).convert("RGBA")
    if fit == "cover":
        return ImageOps.fit(normalized, size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    if fit != "contain":
        raise ValueError("--fit debe ser cover o contain.")
    contained = ImageOps.contain(normalized, size, method=Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", size, _background_rgba(background))
    x = (size[0] - contained.width) // 2
    y = (size[1] - contained.height) // 2
    canvas.alpha_composite(contained, (x, y))
    return canvas


def save_png(image: Image.Image, path: Path, overwrite: bool = False) -> None:
    ensure_output_path(path, overwrite=overwrite, suffix=".png")
    image.save(path, format="PNG", optimize=True)
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"No se pudo verificar la salida: {path}")


def write_json_atomic(path: Path, data: dict[str, Any], overwrite: bool = False) -> None:
    if path.suffix.lower() != ".json":
        raise ValueError(f"El reporte debe usar extensión .json: {path}")
    if path.exists() and not overwrite:
        raise FileExistsError(f"El archivo ya existe: {path}. Elegí otro nombre o usá --overwrite.")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent, text=True)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary.replace(path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def has_alpha(image: Image.Image) -> bool:
    return image.mode in {"RGBA", "LA"} or "transparency" in image.info


def has_transparent_pixels(image: Image.Image) -> bool:
    if not has_alpha(image):
        return False
    alpha = image.convert("RGBA").getchannel("A")
    minimum, _maximum = alpha.getextrema()
    return minimum < 255
