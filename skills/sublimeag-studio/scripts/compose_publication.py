#!/usr/bin/env python3
"""Compose exact brand assets and copy over a prepared product image."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFont

from common import (
    SKILL_ROOT,
    ensure_input_image,
    ensure_output_path,
    fit_image,
    load_json,
    resolve_dimensions,
    save_png,
    sha256_file,
    write_json_atomic,
)


DEFAULT_STYLE = SKILL_ROOT / "assets" / "templates" / "premium-default.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agrega logo y textos exactos a una publicación.")
    parser.add_argument("input", type=Path, help="Imagen base PNG/JPG")
    parser.add_argument("output", type=Path, help="Publicación PNG final")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--preset", choices=["feed_vertical", "story", "catalog_square"])
    group.add_argument("--size", help="Tamaño personalizado ANCHOxALTO")
    parser.add_argument("--fit", choices=["cover", "contain"], default="cover")
    parser.add_argument("--background", default="#F3E8D8")
    parser.add_argument("--logo", type=Path, help="Logo original PNG/JPG")
    parser.add_argument("--logo-position", choices=["top-left", "top-right"], default="top-right")
    parser.add_argument("--title", default="")
    parser.add_argument("--subtitle", default="")
    parser.add_argument("--price", default="")
    parser.add_argument("--font", type=Path, help="Fuente TTF/OTF regular")
    parser.add_argument("--font-bold", type=Path, help="Fuente TTF/OTF para título/precio")
    parser.add_argument("--style", type=Path, default=DEFAULT_STYLE)
    parser.add_argument("--clean-output", type=Path, help="Guarda la base dimensionada sin logo ni texto")
    parser.add_argument("--metadata", type=Path, help="Guarda procedencia y hashes en JSON")
    parser.add_argument(
        "--representation",
        choices=["real", "mockup", "conceptual", "unspecified"],
        default="unspecified",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser


def load_font(path: Path | None, size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates: list[Path | str] = []
    if path:
        candidates.append(path)
    candidates.extend(
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        ]
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(str(candidate), size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> str:
    wrapped: list[str] = []
    for paragraph in text.splitlines() or [""]:
        words = paragraph.split()
        if not words:
            wrapped.append("")
            continue
        line = words[0]
        for word in words[1:]:
            candidate = f"{line} {word}"
            if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
                line = candidate
            else:
                wrapped.append(line)
                line = word
        wrapped.append(line)
    return "\n".join(wrapped)


def scaled_logo(logo: Image.Image, max_width: int, max_height: int) -> Image.Image:
    result = logo.convert("RGBA")
    result.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    return result


def main() -> int:
    args = build_parser().parse_args()
    try:
        ensure_input_image(args.input)
        if args.logo:
            ensure_input_image(args.logo)
        if args.font and not args.font.is_file():
            raise FileNotFoundError(f"No existe la fuente: {args.font}")
        if args.font_bold and not args.font_bold.is_file():
            raise FileNotFoundError(f"No existe la fuente: {args.font_bold}")
        if not args.style.is_file():
            raise FileNotFoundError(f"No existe el estilo: {args.style}")
        if args.clean_output and args.clean_output.resolve() == args.output.resolve():
            raise ValueError("--clean-output debe ser distinto de output.")

        ensure_output_path(args.output, overwrite=args.overwrite)
        if args.clean_output:
            ensure_output_path(args.clean_output, overwrite=args.overwrite)
        if args.metadata:
            if args.metadata.suffix.lower() != ".json":
                raise ValueError("--metadata debe terminar en .json")
            if args.metadata.exists() and not args.overwrite:
                raise FileExistsError(f"El metadato ya existe: {args.metadata}")

        width, height, safe = resolve_dimensions(args.preset, args.size)
        style = load_json(args.style)
        with Image.open(args.input) as source:
            clean = fit_image(source, (width, height), args.fit, args.background)
        if args.clean_output:
            save_png(clean, args.clean_output, overwrite=args.overwrite)

        canvas = clean.copy()
        logo_sha256: str | None = None
        logo_box: list[int] | None = None
        if args.logo:
            logo_sha256 = sha256_file(args.logo)
            with Image.open(args.logo) as logo_source:
                logo = scaled_logo(
                    logo_source,
                    round(width * float(style["logo_max_width_ratio"])),
                    round(height * float(style["logo_max_height_ratio"])),
                )
            x = safe["left"] if args.logo_position == "top-left" else width - safe["right"] - logo.width
            y = safe["top"]
            canvas.alpha_composite(logo, (x, y))
            logo_box = [x, y, x + logo.width, y + logo.height]

        has_copy = bool(args.title or args.subtitle or args.price)
        if has_copy:
            overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            panel_rgb = ImageColor.getrgb(str(style["panel"]))
            panel_alpha = int(style["panel_opacity"])
            panel_top = round(height * 0.66)
            panel_box = (safe["left"], panel_top, width - safe["right"], height - safe["bottom"])
            radius = max(18, round(min(width, height) * 0.025))
            overlay_draw.rounded_rectangle(panel_box, radius=radius, fill=(*panel_rgb, panel_alpha))
            canvas = Image.alpha_composite(canvas, overlay)

            draw = ImageDraw.Draw(canvas)
            text_color = ImageColor.getrgb(str(style["text"]))
            accent_color = ImageColor.getrgb(str(style["accent"]))
            title_font = load_font(args.font_bold or args.font, max(22, round(height * float(style["title_size_ratio"]))), bold=True)
            subtitle_font = load_font(args.font, max(16, round(height * float(style["subtitle_size_ratio"]))))
            price_font = load_font(args.font_bold or args.font, max(22, round(height * float(style["price_size_ratio"]))), bold=True)
            x = safe["left"] + round(width * 0.04)
            y = panel_top + round(height * 0.035)
            max_text_width = width - safe["left"] - safe["right"] - round(width * 0.08)

            if args.title:
                title = wrap_text(draw, args.title, title_font, max_text_width)
                draw.multiline_text((x, y), title, font=title_font, fill=text_color, spacing=8)
                box = draw.multiline_textbbox((x, y), title, font=title_font, spacing=8)
                y = box[3] + round(height * 0.015)
            if args.subtitle:
                subtitle = wrap_text(draw, args.subtitle, subtitle_font, max_text_width)
                draw.multiline_text((x, y), subtitle, font=subtitle_font, fill=text_color, spacing=6)
                box = draw.multiline_textbbox((x, y), subtitle, font=subtitle_font, spacing=6)
                y = box[3] + round(height * 0.018)
            if args.price:
                draw.text((x, y), args.price, font=price_font, fill=accent_color)
                box = draw.textbbox((x, y), args.price, font=price_font)
                y = box[3]
            if y > panel_box[3] - round(height * 0.025):
                raise ValueError("El texto no entra en la zona segura. Acortalo o usá otro formato.")

        save_png(canvas, args.output, overwrite=args.overwrite)
        metadata = {
            "schema_version": 1,
            "representation": args.representation,
            "preset": args.preset,
            "width": width,
            "height": height,
            "source": str(args.input.resolve()),
            "source_sha256": sha256_file(args.input),
            "clean_output": str(args.clean_output.resolve()) if args.clean_output else None,
            "clean_sha256": sha256_file(args.clean_output) if args.clean_output else None,
            "output": str(args.output.resolve()),
            "output_sha256": sha256_file(args.output),
            "logo_source": str(args.logo.resolve()) if args.logo else None,
            "logo_sha256": logo_sha256,
            "logo_box": logo_box,
            "text": {"title": args.title, "subtitle": args.subtitle, "price": args.price},
            "style": str(args.style.resolve()),
        }
        if args.metadata:
            write_json_atomic(args.metadata, metadata, overwrite=args.overwrite)
        print(json.dumps({"ok": True, **metadata}, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
