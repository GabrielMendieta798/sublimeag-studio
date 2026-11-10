# Motores de imagen

Leé este archivo solamente para configurar o extender el motor.

## Estado actual

La ruta operativa prioritaria es la herramienta integrada de `$imagegen`. Genera o edita la base fotográfica; los scripts locales se ocupan de exportación, logo, texto y validación. No existe en este MVP un wrapper propio de API ni una integración ComfyUI.

Si la herramienta integrada no está disponible, no fabriques un archivo de salida ni declares éxito. Se pueden probar `export_image.py`, `compose_publication.py` y `validate_image.py` con una imagen local. El fallback CLI de `$imagegen` solo se usa por pedido explícito y con su propia documentación; no copies ni modifiques su script.

## Contrato para un motor futuro

Una futura integración debe quedar separada de composición y procesamiento. Como mínimo debe recibir:

- operación `generate` o `edit`;
- prompt normalizado e invariantes;
- rutas o identificadores de entradas con su rol;
- destino solicitado y metadatos de modo;
- configuración explícita del motor.

Debe devolver solamente después de verificar el archivo:

- ruta real del PNG generado;
- motor, modelo y parámetros efectivamente usados;
- hashes de entradas y salida;
- advertencias o errores.

## ComfyUI futuro

Antes de implementarlo, el usuario debe autorizar instalación, modelos, licencias y recursos. Confirmá la API real de la instancia; no supongas URL, nodos, checkpoints ni workflows. Los workflows deben versionarse como archivos separados, declarar licencias de modelos y producir un PNG que atraviese el mismo pipeline determinista y el mismo control visual.
