#!/usr/bin/env python3
"""Validate exported assets and emit a machine-readable quality report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image

from common import (
    has_transparent_pixels,
    load_json,
    parse_size,
    preset_data,
    sha256_file,
    write_json_atomic,
)


SUPPORTED = {".png", ".jpg", ".jpeg"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Valida archivo, dimensiones, transparencia y hashes de marca.")
    parser.add_argument("image", type=Path)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--preset", choices=["feed_vertical", "story", "catalog_square"])
    group.add_argument("--size", help="Dimensión esperada ANCHOxALTO")
    parser.add_argument("--require-alpha", action="store_true", help="Exige píxeles realmente transparentes")
    parser.add_argument("--metadata", type=Path, help="JSON creado por compose_publication.py")
    parser.add_argument("--logo-source", type=Path, help="Logo original usado en la composición")
    parser.add_argument("--brand-manifest", type=Path, help="Manifiesto para verificar el logo registrado")
    parser.add_argument("--mode", choices=["producto-real", "mockup", "producto-generico", "publicacion"])
    parser.add_argument("--report", type=Path, help="Ruta del reporte JSON")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def add_check(checks: list[dict[str, Any]], name: str, passed: bool, detail: str) -> None:
    checks.append({"name": name, "passed": bool(passed), "detail": detail})


def expected_size(args: argparse.Namespace) -> tuple[int, int] | None:
    if args.preset:
        data = preset_data(args.preset)
        return int(data["width"]), int(data["height"])
    if args.size:
        return parse_size(args.size)
    return None


def find_registered_logo(manifest: dict[str, Any], logo: Path, manifest_path: Path) -> dict[str, Any] | None:
    assets = manifest.get("assets", {})
    if not isinstance(assets, dict):
        return None
    resolved = logo.resolve()
    for record in assets.values():
        if not isinstance(record, dict) or "file" not in record:
            continue
        candidate = (manifest_path.parent / str(record["file"])).resolve()
        if candidate == resolved or candidate.name == resolved.name:
            return record
    return None


def manual_checks(mode: str | None) -> list[str]:
    shared = [
        "Comparar forma, color, bordes, perspectiva, sombras y reflejos con la entrada.",
        "Comprobar que logo y textos sean exactos, legibles y estén dentro de la zona segura.",
        "Confirmar que la utilería no parezca incluida en la venta sin autorización.",
    ]
    if mode == "producto-real":
        shared.insert(0, "Comparar estampado, ilustraciones y frases píxel a píxel cuando sean críticos.")
    elif mode == "mockup":
        shared.insert(0, "Revisar escala, curvatura, perspectiva, pliegues y legibilidad del diseño aplicado.")
    elif mode == "producto-generico":
        shared.insert(0, "Confirmar que el resultado esté identificado como conceptual y no afirme componentes.")
    return shared


def main() -> int:
    args = build_parser().parse_args()
    checks: list[dict[str, Any]] = []
    try:
        exists = args.image.is_file()
        add_check(checks, "file_exists", exists, str(args.image.resolve()))
        if not exists:
            raise FileNotFoundError(args.image)

        suffix_ok = args.image.suffix.lower() in SUPPORTED
        add_check(checks, "supported_extension", suffix_ok, args.image.suffix.lower())
        nonempty = args.image.stat().st_size > 0
        add_check(checks, "nonempty", nonempty, f"{args.image.stat().st_size} bytes")

        readable = True
        try:
            with Image.open(args.image) as probe:
                probe.verify()
        except Exception as exc:
            readable = False
            add_check(checks, "image_readable", False, str(exc))
        if readable:
            add_check(checks, "image_readable", True, "Pillow verify OK")
            with Image.open(args.image) as image:
                actual_size = image.size
                transparent = has_transparent_pixels(image)
                image_format = image.format
            wanted = expected_size(args)
            if wanted:
                add_check(checks, "dimensions", actual_size == wanted, f"actual={actual_size}, expected={wanted}")
            else:
                add_check(checks, "dimensions", True, f"actual={actual_size}, sin dimensión exigida")
            if args.require_alpha:
                add_check(checks, "transparent_pixels", transparent, f"transparent={transparent}")
            add_check(checks, "decoded_format", image_format in {"PNG", "JPEG"}, str(image_format))

        image_hash = sha256_file(args.image)
        metadata: dict[str, Any] | None = None
        if args.metadata:
            metadata_exists = args.metadata.is_file()
            add_check(checks, "metadata_exists", metadata_exists, str(args.metadata))
            if metadata_exists:
                metadata = load_json(args.metadata)
                expected_hash = metadata.get("output_sha256")
                add_check(
                    checks,
                    "output_hash_matches_metadata",
                    expected_hash == image_hash,
                    f"actual={image_hash}, metadata={expected_hash}",
                )

        if args.logo_source:
            logo_exists = args.logo_source.is_file()
            add_check(checks, "logo_exists", logo_exists, str(args.logo_source))
            if logo_exists:
                logo_hash = sha256_file(args.logo_source)
                if metadata:
                    expected_logo_hash = metadata.get("logo_sha256")
                    add_check(
                        checks,
                        "logo_hash_matches_metadata",
                        logo_hash == expected_logo_hash,
                        f"actual={logo_hash}, metadata={expected_logo_hash}",
                    )
                manifest_path = args.brand_manifest
                if manifest_path:
                    manifest_exists = manifest_path.is_file()
                    add_check(checks, "brand_manifest_exists", manifest_exists, str(manifest_path))
                    if manifest_exists:
                        manifest = load_json(manifest_path)
                        record = find_registered_logo(manifest, args.logo_source, manifest_path)
                        add_check(checks, "logo_registered", record is not None, args.logo_source.name)
                        if record:
                            add_check(
                                checks,
                                "logo_hash_matches_manifest",
                                logo_hash == record.get("sha256"),
                                f"actual={logo_hash}, manifest={record.get('sha256')}",
                            )

        ok = all(check["passed"] for check in checks)
        report = {
            "schema_version": 1,
            "ok": ok,
            "image": str(args.image.resolve()),
            "image_sha256": image_hash,
            "checks": checks,
            "manual_review_required": True,
            "manual_checks": manual_checks(args.mode),
            "limitations": [
                "Las pruebas automáticas no demuestran fidelidad visual del producto.",
                "Las pruebas automáticas no verifican derechos o licencias comerciales.",
            ],
        }
        if args.report:
            write_json_atomic(args.report, report, overwrite=args.overwrite)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if ok else 1
    except Exception as exc:
        report = {"schema_version": 1, "ok": False, "image": str(args.image), "checks": checks, "error": str(exc)}
        if args.report:
            try:
                write_json_atomic(args.report, report, overwrite=args.overwrite)
            except Exception as report_exc:
                report["report_error"] = str(report_exc)
        print(json.dumps(report, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
