# Estado vigente para continuar en el PC principal

Fecha: 26 de octubre de 2026. Este documento reemplaza las instrucciones de estado de la entrega del 22 de octubre. Los informes antiguos se conservan como historial; no describen por sí solos la versión actual.

## Abrir el proyecto

1. Instalar Unreal Engine **5.8 para Windows de 64 bits** desde Epic Games Launcher. Este portátil usa exactamente **5.8.4, changelist 58902052**; preferir esa revisión, especialmente para las herramientas opcionales de autoría. El motor completo no está incluido en el RAR. Los plugins habilitados en el proyecto pertenecen al motor; no se necesita un módulo C++ propio para jugar.
2. Extraer TODO el archivo a una carpeta local corta, por ejemplo `C:\Proyectos\BogotaVoxelTraslado`. No abrirlo dentro de WinRAR ni trabajar sobre una carpeta sincronizada mientras carga.
3. Abrir `BogotaVoxel/BogotaVoxel.uproject` o `BogotaVoxel/Abrir_Proyecto.bat`. El proyecto correcto es el de esa carpeta. No abrir el descriptor de `isolated_repair/BlueprintAuthoring`: es una herramienta opcional de desarrollo.
4. Abrir `/Game/Maps/MapaCompleto_Integration` si no aparece el nivel. Esperar la preparación de shaders/recursos inicial; las cachés se regeneran en este equipo. Pulsar Play dentro del editor. No hay un juego empaquetado ni se requiere un ejecutable del juego.
5. F10 abre las opciones gráficas: mínima, baja, media, alta, máxima y ajustes personalizados. Empieza con mínima para establecer una referencia y mide después cada perfil en el PC principal. El proyecto conserva un arranque ligero en DX11; no confundir ese valor inicial con un límite de calidad. `Abrir_Editor_PC_Ligero.bat` limita tareas de preparación para el portátil; usar el lanzador normal en el PC principal.
6. No aceptar una conversión a otra versión del motor sobre la única copia. Conservar el RAR original. El primer arranque y las primeras vistas pueden tardar más por preparación de recursos.

## Qué quedó incorporado al proyecto principal

- Optimización de 132 mallas estáticas con cuatro niveles de detalle (100/50/18/6 %), conservando geometría base y colisión de nivel 0. Se mantienen los tres niveles existentes de 100 mallas esqueléticas y se habilitaron sus opciones de streaming. El editor sin cocinar no reproduce todas las ventajas del streaming del juego final.
- Distancias de actividad/visibilidad para 134 interiores y fachadas y 102 luces; actualización de pose visible en 195 componentes esqueléticos. Presupuestos de población y actividad según calidad.
- Menú gráfico con cinco perfiles y personalización; aplicación y guardado mediante GameUserSettings. En DX11, la prioridad de 60 FPS usa escala fija de 55 % cuando la resolución dinámica nativa no está disponible. Un límite de 60 no garantiza conseguir 60.
- Corrección de QA-01: ya no se puede cobrar una entrega cuya mercancía no esté pagada, ni por CompleteOrder ni por el destinatario. Se conservó el circuito normal de recogida, caja y entrega.
- El teléfono reutiliza su disposición mientras no cambien apertura, tamaño, página o modo de moto; el HUD sigue actualizándose. Ayuda ampliada de 11 a 16 puntos. Esta versión pasó la regresión renderizada antes de copiarse al proyecto principal.
- Se mantienen las correcciones anteriores de productos, navegación, calzadas, puertas y adaptación al mapa. Consultar los informes del 24 y 25 para el detalle histórico y los límites del tráfico.

Los tres activos de la revisión del 26 están promovidos y comprobados por SHA-256: BPC_DeliveryDataCore, BP_DeliveryRecipient y WBP_BlueprintPhone. Manifiestos en `isolated_repair/AdversarialQA_20261026/promotion_original-*.json`. El descriptor principal no recibe el experimento de desactivación masiva de plugins.

## Pruebas realizadas y alcance

- 278 comprobaciones de datos, tiendas, ofertas, mejoras, compras y persistencia; aceptación/capacidad en pruebas adicionales.
- Circuito de pedidos: 34 comprobaciones normales aprobadas, rechazos por fase incorrecta/destino incorrecto/sin pago y 100 secuencias de identificadores inválidos.
- Puertas de 23 modelos, incluidos cierres por movimiento y puertas traseras de taxi; cinco puntos del mapa y metadatos de siete carriles aprobados en los casos actuales.
- Comportamiento actual del repartidor: 28 comprobaciones y cinco valores de paso temporal; caminar, correr, bicicleta, freno e interferencia del teléfono.
- Prueba renderizada del teléfono: 13 comprobaciones aprobadas y siete capturas de páginas. La primera captura vacía del mapa era un defecto del escenario QA, al que le faltaba BP_MapNavigation; el escenario se corrigió y la captura final contiene las calles. No se presenta como un fallo corregido del mapa principal.
- Hay captura del mapa real y diagnósticos de CPU. Las pruebas automatizadas de funciones y widgets no equivalen a recorrer todo el juego con teclado y ratón. La herramienta de control de ventanas falló tres veces; esa cobertura física queda pendiente.

Evidencias actuales: `isolated_repair/AdversarialQA_20261026`, especialmente `delivery_invariants.json`, `final_native_checks.json`, `rider_current_behavior.json`, `runtime_light_cached.log`, `screens_after` y `screens`. Los fallos de expectativas antiguas se conservan en baseline.json; no se cuentan como correcciones del juego.

## Rendimiento real y problemas pendientes

**No se han conseguido ni certificado 60 FPS estables, y el juego no está terminado ni libre de errores.** En el portátil Ryzen 5 2500U/Vega 8/8 GB, la matriz del 25 obtuvo aproximadamente 4,41 / 2,72 / 1,91 / 2,17 / 1,68 FPS de mínima a máxima, según sus condiciones registradas. La presión de memoria fue severa. El diagnóstico del 26 midió aproximadamente 0,43–1,86 FPS al desactivar grupos progresivamente; es un diagnóstico artificial, no un aumento validado del juego completo. Ver cpu_isolation_results.json. Los procesos ajenos al proyecto se dejaron abiertos por instrucción del usuario.

El tráfico sigue pendiente: colas, contactos entre carrocerías y bloqueos requieren ensayos sostenidos. Una prueba histórica de servicios duró 365 segundos sin marcha atrás, pero el apoyo al suelo fue alrededor del 86 % y persistieron contactos. No declarar aprobado el tráfico basándose en una captura o en vehículos moviéndose al arrancar.

Falta revisar visualmente todos los barrios, texturas, personajes y animaciones, hacer rutas completas con teclado/mando, comprobar pausa/menú gráfico/teléfono, distintas resoluciones y persistencia en el equipo principal. No hay una certificación de todas las combinaciones gráficas.

## Qué hacer primero en el PC principal

1. Registrar CPU, GPU, RAM, versión exacta de UE, resolución y perfil. Medir el nivel real tras preparar shaders, separando tiempo de juego, render y GPU. Usar una copia de pruebas y UserDir independiente.
2. Priorizar coste de simulación y widgets con Unreal Insights; el diagnóstico del portátil mostró carga importante de TickActors y UI. No bajar únicamente resolución esperando resolver un cuello de botella de CPU.
3. Completar ensayos de tráfico de varios ciclos, avance individual, colisiones y apoyo al pavimento. Mantener las colisiones y las mecánicas activas durante la validación final.
4. Repetir recogida/pago/entrega, inventario lleno, identificadores inválidos, guardado/carga, teléfono, F10, controles y revisión visual en los cinco perfiles. Adjuntar capturas y mediciones nuevas; los números del portátil no predicen el PC principal.
5. Solo incorporar nuevos experimentos después de probarlos. No ejecutar todos los scripts de desarrollo en bloque.

## Herramientas y experimentos preservados

El repositorio .git y los cambios locales viajan dentro del proyecto. No se creó un commit ni se subió nada para esta entrega. Revisar git status antes de continuar. Hay respaldos anteriores y fuentes Blender.

Los scripts y pruebas recientes están en `isolated_repair/scripts` y `isolated_repair/work`. Algunas rutas absolutas apuntan al portátil y deben adaptarse. `BlueprintAuthoring` conserva descriptor, fuentes y binarios auxiliares; su Content duplicado se omite. Para usar DeliveryEditorLibrary, crear otra copia del proyecto principal y añadir las herramientas siguiendo sus instrucciones; los binarios deben corresponder a la versión exacta del motor y podrían requerir recompilación con SDK de Windows.

NO aplicados al juego principal: perfil experimental de plugins (una versión omitió SkeletalMeshReduction y provocó reconstrucciones; la propuesta posterior no terminó su validación), candidato cull_unseen_wheel_pose.py, ni propuestas no reproducidas de entrada al menú gráfico. Los mapas de aislamiento que desactivan tráfico/población/UI son herramientas diagnósticas; no son una optimización aplicada al nivel del juego.

El archivo incluye los componentes propios del proyecto, herramientas, fuentes y evidencias. Se omiten copias antiguas duplicadas, la copia temporal ModulelessRuntime, Content duplicado de autoría y carpetas de caché/intermedios. Unreal, drivers y SDK no son componentes redistribuidos aquí. El manifiesto SHA-256 permite comprobar los archivos trasladados; la integridad del RAR no certifica ausencia de errores de juego.
