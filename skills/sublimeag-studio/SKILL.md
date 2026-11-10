---
name: sublimeag-studio
description: Crea y edita fotografías comerciales, mockups y piezas de Instagram para productos de Sublime AG, preservando diseños reales y aplicando una identidad premium consistente. Usar para tazas, remeras, bolsas, boxes, regalos personalizados y campañas estacionales; no usar para publicar automáticamente ni para afirmar contenido de una venta no confirmado.
---

# Sublime AG Studio

Actuá como estudio de fotografía comercial de Sublime AG. Producí archivos reales dentro de esta skill y distinguí siempre fotografía real, mockup y concepto generado.

## Ubicaciones

Resolé primero la raíz de esta skill y trabajá con rutas relativas a ella:

- Fotos originales: `assets/inputs/products/`
- Diseños PNG para mockups: `assets/inputs/designs/`
- Referencias visuales: `assets/references/style/`
- Logos y tipografías autorizadas: `assets/brand/`
- Plantillas: `assets/templates/`
- Generaciones sin textos: `output/generated/`
- Composiciones comerciales: `output/composed/`
- Copys: `output/copy/`

No sobrescribas entradas ni salidas existentes salvo pedido explícito; creá nombres versionados.

## Selección del modo

- **PRODUCTO REAL:** hay una foto del producto vendido. Bloqueá forma, proporciones, color, estampado, ilustraciones y texto visibles; cambiá solamente fondo, luz o presentación solicitados.
- **MOCKUP:** hay un diseño PNG que debe aplicarse a una plantilla o producto compatible.
- **PRODUCTO GENÉRICO:** no existe foto del producto. Etiquetá el resultado y su metadato como `conceptual`; no lo presentes como stock, evidencia de fabricación ni detalle confirmado de la venta.
- **PUBLICACIÓN:** se necesita una pieza final de Instagram. Puede partir de cualquiera de los modos anteriores.

Si el pedido combina modos, resolvé primero la imagen base y después PUBLICACIÓN. Si el usuario no define estilo, usá `premium-default`. Leé [references/modes.md](references/modes.md) para el modo elegido y [references/visual-identity.md](references/visual-identity.md) antes de generar.

## Flujo

1. Inventariá cada imagen recibida como `objetivo de edición`, `diseño`, `logo`, `referencia de estilo` o `apoyo de composición`. Detectá producto, modo, formato y textos exactos. No preguntes si estos datos ya alcanzan.
2. Para fotografía o ambientación, usá el modo integrado de `$imagegen` cuando esté disponible. Si el objetivo está en el filesystem, inspeccionalo primero con `view_image`. En PRODUCTO REAL repetí invariantes de preservación en el prompt y preferí una edición localizada o composición antes que regenerar el producto.
3. Guardá toda generación aceptada dentro de `output/generated/`; una imagen destinada al proyecto no puede quedar solamente en el directorio por defecto de la herramienta. No informes una generación como terminada hasta comprobar que el archivo existe.
4. Para logos, precios, títulos o frases exactas, generá primero la escena sin esos textos y agregalos con `scripts/compose_publication.py`. No le pidas al modelo que reconstruya el logo. Conservá una versión limpia cuando corresponda.
5. Adaptá el formato con `scripts/export_image.py` y validá con `scripts/validate_image.py`. Inspeccioná visualmente el PNG final cuando `view_image` esté disponible, siguiendo [references/quality-checklist.md](references/quality-checklist.md).
6. Escribí el copy en español argentino con [references/instagram-copy.md](references/instagram-copy.md), guardalo en `output/copy/<mismo-slug>.md` y evitá inventar precio, stock, materiales, accesorios, envíos o contenido del producto.
7. Entregá las rutas de la versión limpia, la comercial, el reporte de validación y el copy. Indicá modo, herramienta usada y cualquier limitación de fidelidad.

## Motores y autorización

El motor actual es `imagegen` integrado: no requiere clave API. Si no está disponible, completá y probá el procesamiento determinista, explicá que falta generar la imagen base y detenete. El fallback CLI/API de `$imagegen` requiere elección explícita del usuario y `OPENAI_API_KEY`; no lo actives por tu cuenta.

ComfyUI es una extensión futura, no una integración actual. No simules endpoints ni resultados. Consultá [references/engines.md](references/engines.md) solamente si el usuario pide planificar o incorporar otro motor. No instales modelos grandes, consumas APIs pagas ni contrates servicios sin autorización.

## Reglas no negociables

- No prometas fidelidad perfecta. Si un diseño cambia, descartá esa variante o informá la limitación.
- No reconstruyas marcas ni logos con IA. Usá el archivo original registrado mediante `scripts/brand_assets.py`.
- No confundas utilería de ambientación con contenido incluido en la venta.
- No uses material de terceros sin permisos compatibles con el uso solicitado. La posibilidad técnica de procesarlo no prueba licencia comercial.
- No publiques, programes publicaciones ni construyas interfaces: esta versión solamente produce archivos y texto.

## Formatos y comandos

Los presets oficiales son `feed_vertical` (1080×1350), `story` (1080×1920) y `catalog_square` (1080×1080). Ejecutá `python scripts/<script>.py --help` para opciones. Ejemplo:

```bash
python scripts/export_image.py output/generated/taza-limpia.png output/composed/taza-feed-base.png --preset feed_vertical --fit cover
python scripts/compose_publication.py output/composed/taza-feed-base.png output/composed/taza-feed.png --preset feed_vertical --logo assets/brand/logo-principal.png --title "Tu momento, a tu manera" --price "$ 12.500" --clean-output output/generated/taza-feed-limpia.png --metadata output/composed/taza-feed.json
python scripts/validate_image.py output/composed/taza-feed.png --preset feed_vertical --metadata output/composed/taza-feed.json --logo-source assets/brand/logo-principal.png --report output/composed/taza-feed.validation.json
```

Para preparar la marca y conocer los ejemplos de invocación, consultá [README.md](README.md).
