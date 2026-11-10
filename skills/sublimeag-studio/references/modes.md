# Modos de trabajo

Leé solamente la sección del modo activo; PUBLICACIÓN puede combinarse con cualquiera de las otras tres.

## PRODUCTO REAL

Clasificá la foto original como `objetivo de edición`. Registrá visualmente estos invariantes antes de editar: silueta, proporciones, color, orientación, material, diseño estampado, ilustraciones, frases, logos y detalles distintivos.

Usá edición controlada con el producto como zona protegida. Si el cambio puede resolverse con recorte, extracción, fondo nuevo o composición, preferí ese camino a regenerar el objeto. En el prompt, indicá qué puede cambiar y repetí expresamente lo que debe permanecer idéntico. Compará original y resultado con `view_image`.

Si el modelo altera un texto o una ilustración importante, esa variante no es apta como producto real. No la corrijas inventando píxeles; volvé a una composición más controlada o informá el límite.

## MOCKUP

Clasificá el PNG como `diseño` y la base como `plantilla` u `objetivo de edición`. El PNG ideal tiene fondo transparente y resolución suficiente.

Aplicá el diseño sin reescribirlo. Ajustá perspectiva, curvatura, oclusiones, mezcla de luz y textura del soporte; conservá la relación de aspecto salvo que la plantilla defina un área de impresión distinta. Para tazas, respetá la curvatura cilíndrica; para remeras y bolsas, seguí pliegues y trama sin deformar letras de manera ilegible.

Preferí plantillas autorizadas y reutilizables de `assets/templates/`. Documentá qué plantilla y diseño se usaron. No llames fotografía real al resultado.

## PRODUCTO GENÉRICO

Usá generación cuando no exista fotografía. Describí el producto como genérico y evitá marcas, estampados o especificaciones no proporcionadas. Podés generar, por ejemplo, una taza blanca sublimable, una bolsa lisa o un box conceptual.

Nombrá archivos con `concepto` o registrá `representation: conceptual` en su metadato. Los chocolates, flores, cintas y demás elementos de escena son utilería, a menos que el usuario confirme que integran la venta. En la entrega incluí: "Imagen conceptual; confirmar componentes y terminaciones antes de publicar" cuando corresponda.

## PUBLICACIÓN

Elegí un preset:

| Preset | Dimensiones | Uso |
| --- | ---: | --- |
| `feed_vertical` | 1080×1350 | Feed vertical 4:5 |
| `story` | 1080×1920 | Historia 9:16 |
| `catalog_square` | 1080×1080 | Catálogo o feed cuadrado |

Generá o prepará una base sin textos. Después agregá logo, título, precio y texto proporcionados con `compose_publication.py`. Mantené elementos importantes dentro de las zonas seguras definidas en `assets/templates/formats.json`.

No inventes datos comerciales. Si falta precio, omitilo. Si falta una llamada a la acción, podés usar una neutra como "Consultanos para personalizar el tuyo", sin prometer disponibilidad ni plazo.
