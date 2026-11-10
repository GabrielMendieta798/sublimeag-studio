# Sublime AG Studio

Skill de Codex para producir fotografías comerciales, mockups y publicaciones de Instagram de Sublime AG. El MVP usa `$imagegen` integrado para crear o editar la escena y Pillow para las operaciones que deben ser exactas: dimensiones, logo, textos y validación de archivos.

## Estado real del MVP

Funciona sin servicios externos para redimensionar, componer y validar PNG/JPG. La generación fotográfica requiere que la herramienta integrada de imagen esté disponible en la sesión de Codex. No hay una API propia, ComfyUI, publicación automática ni interfaz web.

## Estructura

```text
sublimeag-studio/
├── SKILL.md
├── agents/openai.yaml
├── assets/
│   ├── brand/                 # logo y manifiesto SHA-256
│   ├── inputs/designs/        # PNG para mockups
│   ├── inputs/products/       # fotografías originales
│   ├── references/style/      # referencias visuales
│   └── templates/             # formatos y estilos deterministas
├── output/
│   ├── generated/             # bases limpias
│   ├── composed/              # publicaciones finales y reportes
│   └── copy/                  # descripciones de Instagram
├── references/                    # reglas que carga Codex según el modo
├── scripts/                       # procesamiento determinista
├── docs/
├── examples/
└── tests/
```

## Preparación

Pillow 10 o posterior es la única dependencia local:

```bash
python -m pip install -r requirements.txt
```

La herramienta integrada `$imagegen` no requiere `OPENAI_API_KEY`. No uses el fallback CLI/API salvo que lo elijas explícitamente y lo configures por separado.

### Agregar el logo

Usá preferentemente un PNG transparente y de buena resolución:

```bash
python scripts/brand_assets.py add /ruta/al/logo.png --name logo-principal
python scripts/brand_assets.py check
```

El primer comando copia el archivo a `assets/brand/` y registra su hash. Los scripts se niegan a reemplazar un logo existente. La composición redimensiona el archivo original sin pedirle a la IA que lo reconstruya.

### Agregar fotografías y referencias

- Copiá las fotos reales sin editar a `assets/inputs/products/`.
- Copiá diseños transparentes para mockup a `assets/inputs/designs/`.
- Copiá ejemplos de luz, fondo o composición a `assets/references/style/`.

Usá nombres descriptivos y versionados, por ejemplo `taza-dia-madre-frente-v1.jpg`. Conservá los originales; las salidas pertenecen a `output/`.

## Invocación desde Codex

```text
Usá $sublimeag-studio en MODO PRODUCTO REAL con assets/inputs/products/taza-mama-v1.jpg. Cambiá el fondo por un estudio crema con madera clara, mantené exactamente la taza y el estampado, y entregá feed vertical sin precio.
```

```text
Usá $sublimeag-studio en MODO MOCKUP con assets/inputs/designs/navidad-v1.png sobre una taza blanca. Creá una base limpia y una historia 1080x1920 con mi logo, título "Un regalo hecho para vos" y precio "$ 12.500".
```

```text
Usá $sublimeag-studio en MODO PRODUCTO GENÉRICO para crear un concepto premium de una bolsa sublimable lisa. Identificá la imagen como conceptual y no inventes materiales ni accesorios incluidos.
```

Más ejemplos: [examples/invocations.md](examples/invocations.md).

## Scripts

Todos los scripts ofrecen `--help` y evitan sobrescribir por defecto.

```bash
python scripts/export_image.py entrada.jpg salida.png --preset feed_vertical --fit cover
python scripts/compose_publication.py base.png publicacion.png --preset feed_vertical --logo assets/brand/logo-principal.png --title "Hecho para vos" --clean-output base-limpia.png --metadata publicacion.json
python scripts/validate_image.py publicacion.png --preset feed_vertical --metadata publicacion.json --logo-source assets/brand/logo-principal.png --brand-manifest assets/brand/manifest.json --mode publicacion --report publicacion.validation.json
```

## Pruebas

```bash
python -m unittest discover -s tests -v
python /ruta/a/skill-creator/scripts/quick_validate.py .
```

Las pruebas crean imágenes temporales; no llaman APIs ni generan fotografías con IA.
