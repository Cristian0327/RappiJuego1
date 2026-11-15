# Proyecto principal — estado del 27 de octubre de 2026

Última revisión de suelos: se nivelaron 37 parques y plazas y se eliminaron solapamientos en 7.933 piezas de borde. Terreno: 30.432 muestras sin intrusiones; colisiones en Unreal: 5.522 puntos sin fallos. Detalle y fuentes vigentes: `SourceArt/MapaOriginal/ESTADO_SUELOS_UNIFICADOS.md`.

Proyecto único de trabajo: `C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/RappiJuego1/BogotaVoxel.uproject`.

**Nivel vigente: `/Game/Maps/MapaOriginal_Reconstruido`**, en Unreal 5.8.4. Las menciones al nivel de integración y estimaciones del historial inferior son anteriores a la reconstrucción.

Se conserva el mapa original reconstruido, las 14 calles secundarias conectadas y las correcciones previas de circulación y pedidos. La revisión más reciente une el pavimento residencial, nivela las bases de 892 instancias, añade ladrillo bogotano y amplía las estaciones de siete a nueve, con 18 accesos y paradas sincronizadas. Se trasladaron 117 archivos de contenido verificados y se actualizó SourceArt; los módulos auxiliares de autoría permanecen fuera del principal.

Pruebas recientes: 90 vehículos se desplazaron; 63 muestras sin solapamientos de carrocerías; cero errores de ejecución. Suelo: 5.522 puntos sin fallos, repetidos después de unir los accesos. Estas pruebas funcionales no sustituyen la revisión completa de todas las tiendas y pedidos ni un perfil de rendimiento en distintos equipos.

Detalle vigente: `SourceArt/MapaOriginal/ESTADO_ANDENES_ESTACIONES.md`. Fuentes: `SourceArt/MapaOriginal/Mapa_Original_Reconstruido.blend`, manifiestos y planes en la misma carpeta. El Blender original de Downloads no se modificó.

Respaldo anterior a esta revisión: `C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_reconstruction_20261027/pavement_principal_backup`.

## Historial anterior y criterios de rendimiento

# Proyecto de trabajo unificado — 26 de octubre de 2026

El proyecto activo es:

`C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/RappiJuego1/BogotaVoxel.uproject`

Nivel principal: `/Game/Maps/MapaCompleto_Integration`.

Se incorporaron 294 archivos nuevos/modificados del traslado recibido en E, verificados por SHA-256, sin sustituir .git. Ambos estados partían del commit 5cab1ac (test). Los originales reemplazados están respaldados en `E:/BogotaVoxel_Proyecto_Completo_2026-10-26/Respaldo_PC_Principal_20261026/Archivos_reemplazados`.

El traslado de E se conserva como respaldo de entrada. No desarrollar por separado allí. Las antiguas copias de autoría y runtime de este PC se archivaron en el mismo respaldo de E; no son proyectos de trabajo actuales.

Estado vigente: `Continuacion/CONTINUAR_PC_PRINCIPAL_2026-10-26.md`. Herramientas y evidencias recientes del portátil: `Continuacion/Trabajo_PC_Portatil_20261026`. Los documentos del 22–23 son históricos.

No se aplicaron experimentos de desactivación masiva de plugins ni el candidato no validado de poses de ruedas. La integración no certifica el tráfico ni 60 FPS.

La caché compartida de Unreal se reubicó en E conservando un enlace en su ruta original. Se preservaron los archivos y el RAR anterior. No desconectar E durante el uso de Unreal mientras esa caché esté allí.

## Criterio de optimización general

Optimizar el coste del software y mantener el comportamiento del juego: trabajo por actor y cuadro, consultas espaciales, reservas de tráfico, actualizaciones de UI, colisiones, poses, dibujo y uso de memoria. Medir por subsistema y en milisegundos; reducir resolución no arregla un cuello de botella de simulación.

El PC principal (Ryzen 7 5700X, RTX 4060, 32 GB) aporta una medición de referencia, no una definición exclusiva de éxito. Comparar escenarios repetibles, calidad, resolución, población, memoria y tiempos de juego/render/GPU en distintas clases de equipos. Definir hardware mínimo y objetivos por perfil antes de prometer 60 FPS; no es posible asegurar el mismo resultado en cualquier hardware.

El objetivo de 60 FPS equivale a 16,67 ms por cuadro. Separar preparación de shaders/cachés de rendimiento sostenido, y editor de juego empaquetado. No desactivar permanentemente tráfico, colisiones o mecánicas para presentar un resultado artificial.

Estimación orientativa del alcance actual: 65–75% de funcionalidad incorporada, con tráfico/rendimiento/regresión todavía pendientes. 20–40 horas efectivas es un rango preliminar de ingeniería y validación, no una medición automática ni una garantía; revisar después del perfil real y ampliar si hace falta reorganizar la carga del mundo.

Primero se abre el estado integrado para revisión del usuario. Las correcciones pendientes se continúan después de esa revisión.

Unreal actualizado a 5.8.4 (CL 58902052). Motor en E:/Epic Games/UE_5.8, enlazado desde su ruta anterior en C. Acceso del escritorio: BogotaVoxel - Proyecto principal. Mantener E disponible. Se abrió el mapa integrado para revisión; no se aplicaron nuevas correcciones de jugabilidad tras la integración.
Corrección 27/10/2026: se conservaron calles, andenes, modelos y materiales. Se ajustaron 294 ubicaciones de escenario con referencia previa a calles nuevas y reserva vial completa. Verificación al recargar: 779 transformaciones y 124 fachadas. 106 archivos de malla sin cambios de hash. Respaldo: C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/map_adaptation_v2/layout_backup_20261027. Queda excepción de raster en aeropuerto, revisión visual de escenarios y coherencia de rutas/destinos residenciales tras estas ubicaciones; no se certifica tráfico ni colisiones completas.
