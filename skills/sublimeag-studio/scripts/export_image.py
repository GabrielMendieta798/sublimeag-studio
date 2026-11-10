#!/usr/bin/env python3
"""Resize and export an image to a deterministic PNG canvas."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

from common import ensure_input_image, fit_image, resolve_dimensions, save_png, sha256_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Exporta una imagen PNG con dimensiones exactas.")
    parser.add_argument("input", type=Path, help="PNG/JPG de entrada")
    parser.add_argument("output", type=Path, help="PNG de salida")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preset", choices=["feed_vertical", "story", "catalog_square"])
    group.add_argument("--size", help="Tamaño personalizado ANCHOxALTO")
    parser.add_argument("--fit", choices=["cover", "contain"], default="cover")
    parser.add_argument("--background", default="#F3E8D8", help="Color para contain o 'transparent'")
    parser.add_argument("--overwrite", action="store_true", help="Permite reemplazar la salida")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        ensure_input_image(args.input)
        width, height, _safe = resolve_dimensions(args.preset, args.size)
        with Image.open(args.input) as source:
            result = fit_image(source, (width, height), args.fit, args.background)
        save_png(result, args.output, overwrite=args.overwrite)
        payload = {
            "ok": True,
            "input": str(args.input.resolve()),
            "input_sha256": sha256_file(args.input),
            "output": str(args.output.resolve()),
            "output_sha256": sha256_file(args.output),
            "width": width,
            "height": height,
            "fit": args.fit,
        }
        print(json.dumps(payload, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
