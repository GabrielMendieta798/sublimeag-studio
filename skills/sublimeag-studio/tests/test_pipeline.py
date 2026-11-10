from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_script(name: str, *args: object) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPTS / name), *(str(arg) for arg in args)]
    return subprocess.run(command, text=True, capture_output=True, check=False)


class PipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.work = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def make_photo(self, path: Path) -> None:
        image = Image.new("RGB", (800, 600), "#D9C5AA")
        draw = ImageDraw.Draw(image)
        draw.rectangle((250, 120, 550, 520), fill="#FFF9F1", outline="#3C3028", width=8)
        image.save(path)

    def make_logo(self, path: Path) -> None:
        image = Image.new("RGBA", (320, 100), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((4, 4, 316, 96), radius=24, fill="#3C3028")
        draw.text((38, 34), "SUBLIME AG", fill="#FFF9F1")
        image.save(path)

    def assert_success(self, result: subprocess.CompletedProcess[str]) -> None:
        self.assertEqual(result.returncode, 0, msg=f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")

    def test_export_and_validate_feed_dimensions(self) -> None:
        source = self.work / "source.jpg"
        output = self.work / "feed.png"
        report = self.work / "feed.validation.json"
        self.make_photo(source)

        exported = run_script("export_image.py", source, output, "--preset", "feed_vertical", "--fit", "cover")
        self.assert_success(exported)
        with Image.open(output) as image:
            self.assertEqual(image.size, (1080, 1350))
            self.assertEqual(image.format, "PNG")

        validated = run_script(
            "validate_image.py",
            output,
            "--preset",
            "feed_vertical",
            "--mode",
            "publicacion",
            "--report",
            report,
        )
        self.assert_success(validated)
        self.assertTrue(json.loads(report.read_text(encoding="utf-8"))["ok"])

    def test_composition_keeps_logo_source_unchanged(self) -> None:
        source = self.work / "source.png"
        logo = self.work / "logo.png"
        clean = self.work / "clean.png"
        output = self.work / "publication.png"
        metadata = self.work / "publication.json"
        self.make_photo(source)
        self.make_logo(logo)
        original_logo_hash = file_hash(logo)

        composed = run_script(
            "compose_publication.py",
            source,
            output,
            "--preset",
            "catalog_square",
            "--logo",
            logo,
            "--title",
            "Hecho para vos",
            "--price",
            "$ 12.500",
            "--clean-output",
            clean,
            "--metadata",
            metadata,
            "--representation",
            "real",
        )
        self.assert_success(composed)
        self.assertEqual(file_hash(logo), original_logo_hash)
        data = json.loads(metadata.read_text(encoding="utf-8"))
        self.assertEqual(data["logo_sha256"], original_logo_hash)
        self.assertEqual(data["text"]["title"], "Hecho para vos")
        self.assertEqual(data["text"]["price"], "$ 12.500")
        with Image.open(output) as image:
            self.assertEqual(image.size, (1080, 1080))
        with Image.open(clean) as image:
            self.assertEqual(image.size, (1080, 1080))

        validated = run_script(
            "validate_image.py",
            output,
            "--preset",
            "catalog_square",
            "--metadata",
            metadata,
            "--logo-source",
            logo,
        )
        self.assert_success(validated)

    def test_brand_registration_and_hash_check(self) -> None:
        source = self.work / "source-logo.png"
        manifest = self.work / "brand" / "manifest.json"
        self.make_logo(source)

        registered = run_script(
            "brand_assets.py",
            "--manifest",
            manifest,
            "add",
            source,
            "--name",
            "logo-principal",
        )
        self.assert_success(registered)
        copied = manifest.parent / "logo-principal.png"
        self.assertTrue(copied.is_file())
        self.assertEqual(file_hash(source), file_hash(copied))

        checked = run_script("brand_assets.py", "--manifest", manifest, "check")
        self.assert_success(checked)

    def test_existing_output_is_not_overwritten_by_default(self) -> None:
        source = self.work / "source.jpg"
        output = self.work / "feed.png"
        self.make_photo(source)
        first = run_script("export_image.py", source, output, "--preset", "feed_vertical")
        self.assert_success(first)
        initial_hash = file_hash(output)

        second = run_script("export_image.py", source, output, "--preset", "story")
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual(file_hash(output), initial_hash)

    def test_transparent_contain_export(self) -> None:
        source = self.work / "source.png"
        output = self.work / "transparent-story.png"
        self.make_photo(source)

        exported = run_script(
            "export_image.py",
            source,
            output,
            "--preset",
            "story",
            "--fit",
            "contain",
            "--background",
            "transparent",
        )
        self.assert_success(exported)
        validated = run_script(
            "validate_image.py",
            output,
            "--preset",
            "story",
            "--require-alpha",
        )
        self.assert_success(validated)


if __name__ == "__main__":
    unittest.main()
