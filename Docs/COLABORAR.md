# Probar y colaborar

1. Clona el repositorio con GitHub Desktop o descarga y extrae el ZIP completo.
2. Abre el `.uproject` en Unreal Engine 5.8.2. Pulsa Play en el mapa Bogotá.
3. En GitHub Desktop crea una rama, por ejemplo `pruebas-npc` o `mejora-tienda`.
4. Modifica los assets o Blueprints en Unreal. Guarda los cambios y compruébalos con Play.
5. Revisa y confirma únicamente los archivos del proyecto. Las carpetas temporales y las partidas están excluidas.
6. Publica tu rama y abre un pull request explicando el cambio y cómo lo probaste.

Los `.uasset` y `.umap` son binarios: coordina quién edita un mismo mapa o Blueprint para evitar cambios simultáneos difíciles de fusionar. El código y los catálogos de datos sí se pueden revisar como texto.

## Reportar un error

Abre un Issue con los pasos para reproducirlo, el resultado esperado, el resultado observado y una captura. Indica tu versión de Unreal y si estabas jugando en editor.

## Comprobaciones antes de un pull request

- El proyecto abre sin módulos faltantes y el mapa inicial carga.
- El celular se abre, permite elegir rutas y conserva su forma original.
- No se acepta un pedido sin seleccionarlo.
- La compra de mejoras respeta saldo y requisitos.
- El cambio funciona en Play y no crea errores en el registro.
