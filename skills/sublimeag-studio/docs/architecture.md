# Arquitectura del MVP

La arquitectura mantiene tres capas independientes:

1. **Generación/edición:** `$imagegen` crea o edita una base fotográfica sin textos críticos. Un futuro adaptador ComfyUI debe producir el mismo contrato de archivo y metadatos, pero no forma parte del MVP.
2. **Composición:** `compose_publication.py` agrega el logo raster original y los textos exactos. También puede guardar una versión limpia y metadatos con hashes.
3. **Procesamiento y control:** `export_image.py` adapta dimensiones; `validate_image.py` verifica archivo, formato, tamaño, transparencia y procedencia del logo. La revisión visual sigue siendo necesaria.

Esta separación permite cambiar el motor de imagen sin cambiar las reglas de marca ni el proceso de exportación.

## Flujo de archivos

```text
assets/inputs + assets/references
             |
             v
      imagegen integrado
             |
             v
 output/generated/*-limpia.png
             |
             +--> export_image.py
             |
             +--> compose_publication.py + assets/brand
                            |
                            v
               output/composed/*.png + *.json
                            |
                            v
                 validate_image.py + view_image
```

Nunca se considera terminada una generación si no existe el archivo en el proyecto. Los objetos de ambientación no se traducen automáticamente en afirmaciones comerciales.
