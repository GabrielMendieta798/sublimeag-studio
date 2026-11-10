#!/usr/bin/env python3
"""Register and verify original Sublime AG brand assets by SHA-256."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from PIL import Image

from common import SKILL_ROOT, has_alpha, load_json, sha256_file, write_json_atomic


DEFAULT_MANIFEST = SKILL_ROOT / "assets" / "brand" / "manifest.json"
VALID_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Registra logos originales y verifica que no hayan cambiado.")
    root.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    sub = root.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Copia y registra un logo PNG/JPG")
    add.add_argument("source", type=Path)
    add.add_argument("--name", required=True, help="Identificador: por ejemplo logo-principal")

    sub.add_parser("list", help="Lista recursos registrados")
    sub.add_parser("check", help="Verifica existencia y hashes")
    return root


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"schema_version": 1, "assets": {}}
    manifest = load_json(path)
    if not isinstance(manifest.get("assets"), dict):
        raise ValueError("El manifiesto no contiene un objeto 'assets'.")
    return manifest


def add_asset(args: argparse.Namespace) -> int:
    source = args.source
    if not source.is_file():
        raise FileNotFoundError(f"No existe: {source}")
    if source.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
        raise ValueError("El logo debe ser PNG o JPG. Para transparencia, usá PNG.")
    if not VALID_NAME.fullmatch(args.name):
        raise ValueError("--name debe usar minúsculas, números y guiones, hasta 63 caracteres.")

    manifest = load_manifest(args.manifest)
    if args.name in manifest["assets"]:
        raise FileExistsError(f"Ya existe un recurso registrado como {args.name}.")
    destination = args.manifest.parent / f"{args.name}{source.suffix.lower()}"
    if destination.exists():
        raise FileExistsError(f"El destino ya existe: {destination}")
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)

    try:
        with Image.open(destination) as image:
            image.verify()
        with Image.open(destination) as image:
            width, height = image.size
            alpha = has_alpha(image)
            image_format = image.format
        manifest["assets"][args.name] = {
            "file": destination.name,
            "sha256": sha256_file(destination),
            "format": image_format,
            "width": width,
            "height": height,
            "has_alpha_channel": alpha,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        write_json_atomic(args.manifest, manifest, overwrite=True)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    print(json.dumps({"ok": True, "name": args.name, "path": str(destination), "sha256": sha256_file(destination)}))
    return 0


def check_assets(args: argparse.Namespace) -> int:
    manifest = load_manifest(args.manifest)
    results: list[dict[str, Any]] = []
    for name, record in sorted(manifest["assets"].items()):
        path = args.manifest.parent / str(record.get("file", ""))
        exists = path.is_file()
        actual_hash = sha256_file(path) if exists else None
        passed = exists and actual_hash == record.get("sha256")
        results.append({"name": name, "path": str(path), "exists": exists, "sha256": actual_hash, "passed": passed})
    ok = all(item["passed"] for item in results)
    print(json.dumps({"ok": ok, "assets": results}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "add":
            return add_asset(args)
        if args.command == "list":
            print(json.dumps(load_manifest(args.manifest), ensure_ascii=False, indent=2))
            return 0
        return check_assets(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
