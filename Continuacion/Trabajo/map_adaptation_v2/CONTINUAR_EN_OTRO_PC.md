# Continuación de BogotaVoxel — pausa solicitada por el usuario

Estado guardado el 22 de octubre de 2026. Rama de destino: `test` del repositorio https://github.com/Cristian0327/RappiJuego1. Mensaje de commit solicitado: `Michaelxd`.

**Este es un punto de continuación del desarrollo, no una versión terminada.** El usuario pidió detener todas las iteraciones, subir los cambios actuales a test y preparar un RAR para otro PC. No continuar modificando el juego durante esta entrega. No fusionar a main ni considerar aprobado el tráfico.

## Objetivo original

Adaptar completamente las mecánicas al nuevo mapa de Bogotá: reproducir las 14 calles secundarias del Blender original; apoyar autos y bicicletas en el suelo; restaurar teléfono, navegación, productos, recogida y entrega; corregir policía/motos hacia atrás, estaciones de TransMilenio, cruces, semáforos, atascos, carros que se atraviesan y subida al andén en bicicleta.

El usuario reportó específicamente que al entrar en tiendas no aparecían productos. También pidió abrir Unreal para revisar el resultado; esa apertura queda pendiente al reanudar porque ahora pidió pausar todo.

## Abrir en el otro PC

1. Instalar Unreal Engine 5.8 para Windows de 64 bits. Se utilizó UE 5.8 de Epic Games Launcher.
2. Extraer TODO el RAR. Abrir `BogotaVoxel/BogotaVoxel.uproject`, esperar la preparación inicial y abrir `/Game/Maps/MapaCompleto_Integration` si no se abre automáticamente.
3. El proyecto principal es moduleless y utiliza Blueprints. No sustituir su descriptor por el de autoría con módulos C++.
4. El RAR conserva la partida personal bajo `Saved/SaveGames`; no publicar esos archivos en GitHub. Git ignora las partidas y los directorios de caché. Las pruebas deben utilizar un UserDir independiente para no alterar el progreso del usuario.
5. El repositorio dentro del RAR conserva `.git`. Comprobar `git branch --show-current`, `git log -1` y `git status` antes de trabajar. El último commit entregado debe ser Michaelxd en test.
6. Las herramientas opcionales de autoría están en `Continuacion/Herramientas_Autoria`: descriptor, DLLs de UE5.8 y fuentes recuperadas de la herramienta. El juego normal no las necesita. Para ejecutar los scripts que usan `unreal.DeliveryEditorLibrary`, preparar OTRA copia del proyecto con esas herramientas. Los binarios dependen de la versión del motor y puede ser necesario recompilarlos en el nuevo PC.
7. Los scripts conservan rutas absolutas del equipo original. Antes de ejecutarlos, adaptar esas rutas o preparar un entorno equivalente. No ejecutar todo el directorio indiscriminadamente: contiene intentos históricos y operaciones no idempotentes.

## Organización de la entrega

- `Content`: estado más reciente guardado de la copia aislada, incluidos mapas QA para reproducir pruebas.
- `Fuentes_Blender`: mapa editable corregido, estación compacta y datos de calles/tiendas/viviendas. Los Blender incluidos se comprobaron sin bibliotecas ni imágenes externas necesarias. Se retiraron únicamente referencias rotas que no usaba ningún material; una era una antigua imagen de fondo en un Empty.
- `Continuacion/Trabajo`: scripts, especificaciones, resultados, capturas y registros relevantes del trabajo. `map_adaptation_v2` es la iteración actual. Los demás directorios conservan la procedencia y las herramientas que invocan sus scripts.
- `Continuacion/Herramientas_Grafos`: `blueprint_graph.py` y herramientas auxiliares de creación de gráficos.
- `Continuacion/Herramientas_Autoria`: herramientas opcionales para editar gráficos por Python.
- `Continuacion/EVIDENCIAS_ESTADO.json`: resumen automático de las pruebas disponibles y del ensayo interrumpido.
- `Respaldo_antes_pausa`, fuera de BogotaVoxel en el RAR: respaldo de los archivos originales reemplazados al consolidar este estado de desarrollo.

## Hecho y comprobado

### Calles, terreno y tiendas

- Se reconstruyeron las 14 curvas de calles secundarias del Blender original, manteniendo su trazado. Calzada secundaria de 480 cm y andenes de 140 cm.
- Se generaron 134 variantes de fachadas para despejar calles sin recortar arquitectura alta. Se ajustaron aproximadamente 255 elementos pequeños y seis tiendas, conservando IDs y temas de las veinte tiendas.
- Pavimento conectado; se eliminaron tapas de andén en intersecciones. Hay adaptación de terreno, incluidas pendientes de hasta 20% en el acceso elevado.
- Auditoría física de Unreal: 793 muestras de calles, entradas de veinte tiendas y destinos residenciales; cero errores en `physical_street_audit.json`.
- El mapa editable completo está en `Fuentes_Blender/Mapa_Bogota_Calles_Completas.blend`. La vista `unreal_map_complete00001.png` muestra las calles nuevas; la orientación de la cámara de esa captura difiere de la referencia, no del nivel.

### Productos y pedidos

- Se corrigió un error de coordenadas de producto: se trataban posiciones mundiales como relativas, aplicando dos veces la rotación de la tienda.
- `BP_DeliveryStore`: construcción propia mediante EnsureStoreBuilt, actualización al comenzar y presentar pedidos, transformación inversa correcta, visibilidad/movilidad de productos y conservación de lo ya recogido.
- `BPC_DeliveryDataCore.ApplyInsideStore`: refresca los productos al entrar sin vaciar la cesta.
- Comprobación de veinte tiendas, temas y orientaciones: posición inicial sin error y productos visibles (`store_product_checks.json`).
- Prueba real renderizada en floristería: entrar, recoger tres productos, pasar por caja y entregar al destinatario; completada.
- Prueba real renderizada de comida: producto visible en el mostrador, recogida, confirmación en caja, navegación y entrega completada; estado final del pedido 0. Evidencia en `visual_acceptance.log` y `food_shot_product00000.png`.
- Estos dos activos de producto ya se habían aplicado antes al proyecto original; la consolidación de esta pausa incorpora además el resto del trabajo actual.

### Navegación y teléfono

- Red del nuevo mapa con 2.325 nodos y 2.381 conexiones, una componente conectada, veinte tiendas y 99 viviendas válidas; 1.980 combinaciones tienda/vivienda. Se retiró un destino físicamente bloqueado.
- Las posiciones se basan en actores reales e IDs existentes. No utilizar `new_map_audit/integration_plan.json` para volver a posicionar el mundo: era una propuesta pendiente, no el estado físico implantado.
- Proyección del mapa del teléfono e inversa del clic adaptadas a las dimensiones reales; incluye las catorce calles, edificios y marcadores.
- La prueba abrió páginas de pedidos, mapa, tienda, carga, catálogo y pedido activo. Una ruta del ensayo de comida tenía 132 puntos y el pedido se completó.
- `navigation_report.json` conserva un conteo histórico de 100 viviendas: para el estado final usar `homes.json` (99) y la evidencia de 1.980 rutas. No interpretar ese archivo histórico como una regresión.

### Contacto, bicicleta y estaciones

- Se conservaron correcciones de apoyo visual de vehículos y bicicleta y la orientación visual de la patrulla. Se hornearon alturas de carril desde el pavimento real, evitando techos de estaciones y fórmulas del mapa antiguo.
- La bicicleta del jugador superó una prueba física real de andén: `CURB_CLIMBED=true`, subida medida de 15,70 cm. Conserva step height de 55 cm. Ver `physics_shot_curb00000.png`.
- Estación 2: se compactaron extremos de la carcasa conservando centro, puertas y colas. Se corrigió una importación inicial con unidades equivocadas; no repetir escalado adicional.
- Estación 4: se movió 45 m a lo largo de su orientación y se sincronizaron pasajeros, puente de acceso, cruces y parada del bus. La comprobación geométrica de las siete estaciones dio cero solapamientos con buses (`station_bus_overlap_after.json`).
- Se despejó una farola frente a la tienda 8 y se sincronizó su luz. Los accesos físicos pasaron la auditoría.

## Tráfico: cambios realizados, pero pendiente de resolver

Se trabajó sobre carriles reales, cruces por arco, ocupación y compatibilidad de movimientos. Hay ocho zonas de conflicto, 57 movimientos y una matriz de compatibilidad de barrido de carrocería. Se actualizaron semáforos y líneas de detención; entradas reservan sitio para la salida. Los carriles duplicados 0/4 y 1/5 comparten seguimiento. La población se redujo de 150 a 90 vehículos principales, manteniendo los diez buses; hay además 36 motos, patrullas y ciclistas de servicio.

Se reconstruyeron call sites de la cuadrícula espacial y `BP_TrafficCell.ClearanceFor`, usando CurrentGap. Fue un cambio importante: las llamadas viejas no ejecutaban de forma fiable la lógica recién sustituida. Después se añadieron las entidades de servicio a la misma cuadrícula mediante proxies ocultos que representan sus posiciones reales.

Se sustituyó la envolvente antigua por un cálculo de barrido de cajas orientadas. Se verificaron sesenta casos numéricos en la VM de Blueprints, con error menor de 0,1 cm. Se corrigió el seguimiento para exigir coincidencia física con el carril y no solo una referencia común.

Se eliminaron cúspides de las uniones de los carriles 0/1 y sus duplicados 4/5; se comprobó que cada segmento resultante seguía dentro del pavimento. Se regeneraron zonas, recorridos de servicio, semáforos y posiciones iniciales. Datos actuales en `actual_lanes.json`, respaldo anterior en `lanes_before_cusp_fix.json`.

Último cambio: se detectó que los ciclistas aún tenían reglas del antiguo mapa cuadriculado y sobrescribían MaxWalkSpeed. `unify_service_controllers.py` reconstruye sus ticks conservando aparcar/caminar, añade TrafficSpeedLimit y filtra obstáculos estáticos; `fix_service_braking.py` pasa el límite actual al ciclista y protege la raíz cuadrada de valores negativos. También se mantiene la orientación real de motos/patrullas. La compilación de esta iteración terminó sin errores en `unified_finish_pipeline4.log`.

**Ensayo v9: interrumpido por la pausa del usuario, aproximadamente a 205 segundos de los 245 previstos.** En los fotogramas registrados no se detectaron solapamientos de carrocería entre los 90 vehículos principales ni marcha atrás de servicios; eso NO significa que el tráfico esté resuelto. Al último muestreo solo circulaban 4 de 90 vehículos principales; 86 estaban detenidos. Las colas persisten y varios servicios permanecen inmóviles. Los ensayos anteriores v7/v8 también acumularon atascos. No declarar aprobado, no ocultar esta limitación y no tomar un arranque con vehículos moviéndose como prueba suficiente.

La pausa detuvo la prueba de forma explícita; su registro no tiene cierre normal y no debe interpretarse como fallo espontáneo de Unreal. No se realizaron más iteraciones después de la solicitud de pausa.

## Qué investigar primero al retomar

1. Reproducir `Content/QA/AdaptationTraffic` en una copia aislada y guardar un registro nuevo. Separar UserDir de la partida del usuario. Completar más de dos ciclos de 110 segundos y comprobar avance por vehículo, no solo velocidad inicial.
2. Identificar por qué servicios con `NearbyTrafficClearance` y permiso de cruce aparentemente libres siguen sin velocidad real. En v9 los ciclistas 3 y 8 aún se detenían cerca de la zona 5. Registrar State, RouteIndex, Goal, TrafficSpeedLimit, MaxWalkSpeed, MovementMode y el actor/componente que golpea la sonda estática o la cápsula. El proxy Speed es 0 porque no simula movimiento: para servicio usar GetVelocity del personaje real.
3. Revisar dependencias mutuas entre la sonda de peatones de los autos (`ExternalPawnClearance`), cápsulas de servicios y seguimiento por arco. No resolverlo desactivando colisiones de forma general ni haciendo atravesar carros.
4. Validar que los límites de SVC se mantienen durante el tick del actor y que no queda otra regla antigua imponiendo paradas o desvíos. El cambio nuevo eliminó una interferencia, pero no ha demostrado resolver todas las causas.
5. Revisar reservas/compatibilidad al pasar de una zona a la siguiente, espacio real después de las salidas y equidad de acceso. Hay zonas de 70–185 m: una reserva retenida por un servicio parado puede bloquear muchas entradas.
6. Los semáforos de cruces usan la misma fase global de 110 s (A 0–36, B 44–80, fase de peatones en el resto). Se observan pausas globales. **No se implementaron desfases.** Si se añaden, sincronizar luces visibles, permiso de vehículos, cruces de peatones y estaciones; no cambiar solo la autorización de autos.
7. Repetir verificación de carrocerías orientadas, motos hacia atrás y estaciones con la solución final. El ensayo v7 tuvo un solapamiento en la unión del carril 1; v8 y el tramo de v9 no lo reprodujeron después de corregir la cúspide.
8. Tras resolver tráfico, repetir pedidos de al menos comida y compra múltiple, mapa/clic/ruta, entrada/salida de tiendas, contacto de ruedas, bicicleta/andén y recuperación de partida. Revisar visualmente el nivel y abrir Unreal para el usuario.

## Herramientas principales y precauciones

- Carpeta actual: `Continuacion/Trabajo/map_adaptation_v2`.
- `unified_finish_pipeline.py`: última construcción de controladores; `unified_finish_pipeline4.log` es la ejecución correcta. Los registros 1–3 contienen errores corregidos durante el desarrollo.
- `build_proxy_debug.py` + `build_debug_traffic.py` + `build_traffic_probe.py`: generan el QA actual. La variante debug registra GridVehicles, que incluye proxies; las estadísticas principales deben filtrar IDs < 90.
- `analyze_traffic.py`, `analyze_body_overlaps.py`: analizan registros. Para v7+ el mapeo de modelos usa la selección de 80 privados/taxis más diez buses. No aplicar los primeros 90 índices del antiguo catálogo de 150 sin remapear.
- `find_proxy_deadlock.py` y `find_sweep_deadlock.py` son ayudas aproximadas; no reproducen todos los casos de compatibilidad/proyección de la VM y su mapeo de proxies puede variar al aparcar. Confirmar siempre dentro del juego.
- `rebuild_clearance_callers.py` reconstruye la cuadrícula sin servicios externos. Si se ejecuta, ejecutar después `fix_external_obstacles.py`, y luego el `fix_service_braking.py` actual para no perder el límite del ciclista.
- `fix_exit_capacity.py` ya no debe volver a reducir la flota: solo selecciona si encuentra 150 vehículos. `fleet_before_capacity.json` conserva el catálogo original de 150; `fleet_before_capacity_current.json` es otro estado.
- **No ejecutar otra vez `install_station_move.py` sin volverlo idempotente**: algunas actualizaciones de parada acumulan el desplazamiento.
- No volver a escalar las 134 fachadas ni la estación compacta. Sus unidades finales se comprobaron.
- `fix_manager_instance.py` destruye y recrea el manager del nivel a partir del CDO; puede perder overrides nuevos si se ejecuta sin revisar.
- Los QA deben permanecer fuera del mapa principal; el mapa principal no lleva el actor de prueba.
- No usar snapshots de debug en editor como si fueran el resultado de una partida real. Una prueba congelada de cuadrícula daba libertad ficticia en editor.
- `promote_verified.py` se escribió para una promoción futura de cambios aprobados; NO se ejecutó como validación final. La consolidación de esta pausa tiene otro propósito: guardar todos los cambios de desarrollo en test, con su estado pendiente documentado.

## Rutas del equipo original, solo como referencia

- Workspace: `C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho`.
- Proyecto original/Git test: `C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/RappiJuego1/BogotaVoxel.uproject`.
- Autoría aislada: `workspace/isolated_repair/BlueprintAuthoring/BogotaVoxel.uproject`.
- Runtime aislado: `workspace/isolated_repair/ModulelessRuntime/BogotaVoxel.uproject`.
- Motor: `C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe`.
- Blender utilizado: Blender 5.2.1 LTS, en `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`.
- El `BlueprintAuthoring/Content` del proyecto original era una junction al juego: **no utilizarlo como copia aislada**. Las copias dentro del workspace sí tenían Content real.

## Petición para el siguiente chat

Leer este informe y EVIDENCIAS_ESTADO.json, abrir el proyecto entregado en una copia aislada, comprobar el último commit Michaelxd de test, y continuar por la inmovilidad de servicios y los atascos. Conservar todas las calles y las correcciones de productos. Probar cada solución prolongadamente sin alterar la partida del usuario. No dar el juego por terminado hasta resolver el tráfico y revisar los demás puntos originales. El usuario prefiere que se actúe sin pedir confirmaciones rutinarias y que se expliquen claramente los resultados y las limitaciones.
