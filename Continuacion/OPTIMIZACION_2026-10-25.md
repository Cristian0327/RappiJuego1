# Optimización de BogotaVoxel

Objetivo de rendimiento: 60 FPS, equivalente a 16,67 ms por cuadro. Es un objetivo que requiere mediciones por hardware y escena; un límite de 60 FPS no demuestra que el juego pueda mantenerlo.

## Controles

F10 abre gráficos durante Play. Hay perfiles mínima, baja, media, alta y máxima. Cada ajuste puede modificarse por separado, formando una configuración personalizada. APLICAR Y GUARDAR conserva los cambios usando GameUserSettings de Unreal. VOLVER AL JUEGO cierra el menú. Escape y F10 también lo cierran.

Resolución interna cambia el coste del renderizado sin reducir la resolución de los textos del menú. Priorizar 60 FPS limita a 60 cuadros y establece una resolución interna del 55 % como alternativa compatible con DX11. También guarda la preferencia de resolución dinámica, cuyo soporte en PC requiere DX12 o Vulkan; en este portátil con DX11 no se promete adaptación automática. No corrige por sí sola un cuello de botella de CPU, navegación o falta de RAM.

Pantalla permite elegir 720p o la resolución nativa del escritorio. Modo permite ventana o sin bordes. El menú pausa la partida mientras está abierto.

## Cambios implementados

La auditoría encontró 220 mallas estáticas con un solo LOD, incluyendo fachadas de más de 400.000 triángulos. Se generaron cuatro LOD para 132 mallas: modelo base completo y objetivos aproximados del 50 %, 18 % y 6 % para la distancia. Se verificaron los triángulos y vértices del modelo base y la modalidad de colisión. Un recurso antiguo de estación con una escala inconsistente se conservó intacto; el mapa utiliza su reemplazo corregido, que sí tiene LOD. La reducción realmente alcanzada se registra por recurso.

Se preservan los LOD esqueléticos existentes, los controles de población lejana y el presupuesto de servicios previamente implementados. No se detiene el tráfico solo por quedar fuera de cámara: eso alteraría la simulación y podría crear bloqueos al volver a mirarlo.

Unreal ya descarta el dibujo fuera del campo de visión y usa consultas de oclusión. Esto evita dibujar; no descarga automáticamente el mapa de la RAM. La carga por sectores, World Partition y HLOD requieren una reorganización del mapa y no se consideran implementados solo por activar una variable.

Se configuraron distancias de dibujo para 134 componentes de interiores y fachadas, 102 luces limitadas por distancia y actualización de pose visible en 195 componentes esqueléticos. Se preservaron los LOD de 100 mallas esqueléticas y se habilitó su política de streaming. Los servicios y multitudes ajustan su actividad cercana según la calidad; las multitudes reparten las comprobaciones en lotes de 32. Los perfiles controlan texturas, sombras, resolución, reflejos, efectos y distancia. Se eliminaron restricciones globales que impedían que las preferencias del usuario controlasen las opciones gráficas.

La caché DDC conserva datos derivados del editor. La primera preparación de recursos modificados sigue siendo costosa. PSO precaching trabaja con estados de renderizado; no equivale a cargar todas las texturas. Un indicador de PSO debe mostrar únicamente trabajo pendiente real del motor. No hay porcentajes ni esperas simuladas.

El streaming de LOD de mallas tiene limitaciones importantes en el editor y con contenido sin cocinar. Epic indica que su comprobación de memoria debe hacerse con datos de una versión empaquetada; no se presupone esa misma liberación de RAM en PIE. En este trabajo se configura la política de streaming y se prueban los LOD de renderizado dentro de Unreal, sin generar un ejecutable. Véase la [respuesta técnica de Epic sobre streaming de mallas](https://forums.unrealengine.com/t/staticmesh/2506968).

## Validación

Los resultados por recurso, comprobaciones del menú y capturas de tiempos de cuadro quedan en isolated_repair, fuera del proyecto principal. Los cinco perfiles pasaron la prueba en ejecución de calidad efectiva y el guardado de ajustes personalizados. La captura `graphics_settings_preview00001.png` verifica el menú a 1280×720 y la etiqueta MÍNIMA. Los ocho Blueprint de optimización compilan y la revisión de dependencias no encontró llamadas al módulo nativo del proyecto en los recursos utilizados.

La prueba de ciudad del 25 de octubre ejecutó los cinco perfiles consecutivamente en DX11 a 1280×720, sin límite de FPS. Cada captura comienza después de la preparación inicial de navegación y PSO. Se usó la misma ubicación inicial, con la simulación de ciudad activa; no representa una certificación de todo el mapa y el estado del tráfico cambia entre capturas.

| Perfil | FPS promedio | FPS al percentil 99 de tiempo de cuadro |
| --- | ---: | ---: |
| Mínima | 4,41 | 2,72 |
| Baja | 2,72 | 1,34 |
| Media | 1,91 | 0,48 |
| Alta | 2,17 | 0,93 |
| Máxima | 1,68 | 0,60 |

**El objetivo de 60 FPS no se alcanzó.** En mínima, el hilo de juego consumió aproximadamente 220 ms por cuadro, de los cuales 142 ms corresponden a TickActors; el hilo de renderizado consumió aproximadamente 9,7 ms. Esto apunta principalmente al coste de simulación y Blueprint, con presión de memoria durante la carga. El mapa tardó unos 213 segundos en la primera carga medida. Reducir resolución o sombras no basta para corregir este cuello de botella. Las mediciones GPU de esta captura DX11 son inconsistentes con los tiempos de cuadro y se excluyen del diagnóstico.

La siguiente fase requiere perfilar y simplificar la simulación de actores, reducir trabajo repetido en Blueprint y organizar la carga del mundo por sectores. World Partition/HLOD no están implementados en esta entrega. El tráfico conserva sus limitaciones documentadas previamente; estos cambios no certifican su comportamiento como terminado.

Resultados: `isolated_repair/optimization_matrix_results.json`, cinco CSV bajo `OptimizationMatrixUser/Saved/Profiling/CSV`, `optimization_asset_validation.json` y manifiesto de los 243 archivos incorporados al original `optimization_original_manifest.json`. Los originales se respaldaron en `optimization_backup_20261025_164026`. No se generó un ejecutable.

Equipo local: Ryzen 5 2500U, Radeon Vega 8 con 1 GB de memoria gráfica, 8 GB de RAM. La apertura del editor tiene un coste adicional al juego. Las pruebas se ejecutan con Unreal, sin generar un ejecutable del juego.

Actualización del 26 de octubre: la prueba automática adicional de PIE falló en el script de arranque al intentar acceder a una clase de preferencias no expuesta a Python. No produjo una captura válida de PIE y no se cuenta como prueba aprobada. Las cinco capturas anteriores sí se realizaron con `UnrealEditor -game`, contenido sin cocinar y descriptor original sin módulo nativo. Se inició después el editor normalmente con el mapa principal, sin script de arranque. El registro de apertura es `isolated_repair/optimization_original_editor.log`.
