# Sublime AG Studio

Sublime AG Studio is a reusable Codex skill and deterministic image-processing pipeline for producing commercial product imagery, mockups, and Instagram-ready assets. It was designed for Sublime AG, an Argentine small business that creates personalized mugs, apparel, bags, gift boxes, and seasonal products.

The project is also a portfolio case study in AI-assisted automation and DevOps-minded workflow design: generative image work is isolated from deterministic composition, file processing, validation, and brand-integrity controls.

## Problem statement

Small product businesses often need to turn inconsistent source photos and artwork into multiple commercial formats while preserving the product, printed design, logo, price, and copy. Generative image models are useful for lighting and scene creation, but they are not reliable enough for exact typography or identity-sensitive assets.

This project combines AI-assisted generation with deterministic post-processing. The image model handles photography and ambience; Python and Pillow handle exact dimensions, original logo assets, supplied text, metadata, and validation.

## Features

Implemented:

- A discoverable Codex skill with four workflows: real product, mockup, generic product concept, and social publication.
- A consistent premium visual direction with warm, minimal commercial styling.
- Exact Instagram export presets: 1080×1350, 1080×1920, and 1080×1080.
- Deterministic logo and text composition using Pillow.
- Non-destructive output behavior by default.
- SHA-256 registration and integrity checks for local brand assets.
- Validation for file existence, image decoding, dimensions, transparency, metadata, and logo provenance.
- Explicit separation between real product photography, mockups, and conceptual imagery.
- Unit tests that run without network access or paid APIs.

The skill can direct Codex to use its built-in image-generation capability when available. Image generation itself is provided by the host environment; this repository does not implement or emulate a proprietary image model.

## Architecture

```text
Product photos / artwork / style references
                    |
                    v
       Codex skill + built-in image tool
       (generation or controlled editing)
                    |
                    v
          Clean image base (PNG)
                    |
          +---------+---------+
          |                   |
          v                   v
  export_image.py    compose_publication.py
  resize / crop      logo / exact copy / metadata
          |                   |
          +---------+---------+
                    |
                    v
          validate_image.py
   automated checks + manual review checklist
```

Generation, composition, and validation are separate layers. This makes it possible to add another image engine later without changing the deterministic processing contract.

## How it works

1. The skill classifies each input as an edit target, design, logo, style reference, or compositing asset.
2. It selects the appropriate operating mode and reads the relevant visual and quality rules.
3. When available, the host's built-in image tool creates or edits the clean photographic base.
4. Deterministic scripts resize the base and add exact brand assets or supplied copy.
5. The validator produces a machine-readable report and a manual visual-review checklist.
6. Final PNG paths and Argentine Spanish Instagram copy are returned to the user.

The workflow never treats a conceptual image as proof of a manufactured product, and it does not infer that scene props are included in a sale.

## Project structure

```text
.
├── .gitignore
├── README.md
└── skills/
    └── sublimeag-studio/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── assets/
        │   ├── brand/
        │   ├── inputs/
        │   ├── references/
        │   └── templates/
        ├── docs/
        ├── examples/
        ├── output/
        ├── references/
        ├── scripts/
        └── tests/
```

Private photos, customer designs, local brand assets, generated outputs, model files, and local manifests are intentionally excluded by `.gitignore`.

## Tech stack

- Python 3.10+
- Pillow 10+
- Codex Skills (`SKILL.md` and `agents/openai.yaml`)
- Built-in image generation/editing when supplied by the Codex host
- JSON templates and metadata
- SHA-256 integrity checks
- Python `unittest`

## Installation

Create an isolated environment and install the single runtime dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r skills/sublimeag-studio/requirements.txt
```

To install the skill globally for Codex:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R skills/sublimeag-studio "${CODEX_HOME:-$HOME/.codex}/skills/"
```

The deterministic scripts can also be used directly without installing the skill.

## Usage examples

Invoke the skill from Codex:

```text
Use $sublimeag-studio in REAL PRODUCT mode with my mug photo. Preserve the mug, color, print, illustration, and visible text exactly; replace only the background with a warm cream studio scene and produce a 1080×1350 feed image.
```

Register a local logo without replacing an existing asset:

```bash
cd skills/sublimeag-studio
python scripts/brand_assets.py add /path/to/logo.png --name logo-primary
python scripts/brand_assets.py check
```

Export, compose, and validate an existing image:

```bash
python scripts/export_image.py input.jpg output/generated/base.png \
  --preset feed_vertical --fit cover

python scripts/compose_publication.py output/generated/base.png output/composed/feed.png \
  --preset feed_vertical \
  --logo assets/brand/logo-primary.png \
  --title "Made for you" \
  --metadata output/composed/feed.json

python scripts/validate_image.py output/composed/feed.png \
  --preset feed_vertical \
  --metadata output/composed/feed.json \
  --logo-source assets/brand/logo-primary.png \
  --brand-manifest assets/brand/manifest.json
```

## Testing

The test suite covers preset dimensions, transparent exports, non-destructive output behavior, deterministic composition, and brand-asset hash validation:

```bash
python -m unittest discover -s skills/sublimeag-studio/tests -v
```

## Demo / screenshots

No private product photos, customer artwork, real logos, or generated campaign images are included in the public repository. A sanitized public demo set has not been added yet. The test suite generates temporary synthetic fixtures to verify the deterministic pipeline without publishing business data.

## Security considerations

- `.env` files, provider state, private keys, credentials, private inputs, local brand assets, generated outputs, and model weights are ignored.
- The tracked `manifest.example.json` is intentionally empty; the real `manifest.json` is created locally and ignored.
- Scripts refuse to overwrite outputs unless `--overwrite` is explicitly supplied.
- Logo hashes provide integrity checking, not proof of copyright ownership or commercial licensing.
- Generated or third-party material must be reviewed for usage rights before commercial publication.
- Automated image validation does not replace manual visual comparison against the original product.

## Roadmap

- Add a user-authorized ComfyUI adapter with versioned workflows and model-license metadata.
- Add reusable, licensed mockup templates for mugs, apparel, and bags.
- Add sanitized demo assets and screenshots.
- Add CI for tests, skill validation, linting, and secret scanning.
- Expand automated visual regression and template-boundary checks.

ComfyUI is planned only; it is not integrated in the current version.

## Limitations

- Fidelity of AI-edited product artwork cannot be guaranteed and requires manual review.
- There is no web interface, dashboard, automatic social publishing, or inventory integration.
- Mockup deformation and scene generation depend on the host image tool or an authorized external workflow; this repository does not contain a standalone generative engine.
- Exact logo and text placement is deterministic, but aesthetic review remains subjective.
- No public demo media or production customer data is bundled.
