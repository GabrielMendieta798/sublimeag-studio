# Control de calidad

## Comprobaciones automáticas

Ejecutá `scripts/validate_image.py` sobre cada PNG entregable y guardá el reporte JSON. Verificá:

- archivo existente, legible y no vacío;
- extensión PNG/JPG admitida;
- dimensiones exactas del preset;
- transparencia real cuando se exige;
- hash del logo fuente coincidente con el metadato de composición;
- hash del logo registrado coincidente con `assets/brand/manifest.json` cuando se proporciona el manifiesto.

La validación automática no demuestra fidelidad visual ni licencia.

## Inspección visual obligatoria cuando sea posible

Abrí original, base limpia y pieza final con `view_image`. Revisá al 100 % o detalle original:

- silueta, manijas, costuras, asas y bordes;
- color y material del producto;
- orientación, proporción y legibilidad del estampado;
- frases, ilustraciones y logos contra el original;
- sombras de contacto, reflejos, perspectiva y escala;
- recortes, halos, bordes contaminados y objetos flotantes;
- texto comercial exacto y dentro de zona segura;
- logo no reconstruido, estirado ni recortado;
- utilería claramente separada de lo que se vende.

En PRODUCTO REAL, una alteración relevante del diseño invalida la variante. En MOCKUP, una deformación que impide leer el diseño requiere ajustar la plantilla o informar el límite.

## Entrega honesta

No uses "fidelidad garantizada". Informá brevemente cualquier zona no verificable, artefacto menor aceptado o diferencia entre concepto y producto real. Para terceros, confirmá que el usuario aportó o autorizó el material; no deduzcas derechos comerciales por su disponibilidad.
