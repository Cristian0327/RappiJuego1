# Movimiento y rendimiento — 19 de octubre de 2026

Proyecto: `BogotaVoxel.uproject`, carpeta `RappiJuego1` del escritorio. Mapa principal: `/Game/Maps/Bogota_Blueprint_Integration`.

## Correcciones comprobadas

- El protagonista utiliza la misma caminata de Mixamo que los NPC, adaptada a su esqueleto: `AN_Walk_InPlace`. Conserva los estados de reposo, salto y vehículos. La animación de los ancianos permanece intacta. Prueba en ejecución: personaje en movimiento, estado de caminata activo e instancia de animación Blueprint correctos (3/3).
- El corrector de orientación de motociclistas y ciclistas vuelve a estar conectado al mapa principal. Cuatro pilotos de la prueba aislada mantuvieron alineación frontal 1.0 en rectas y curvas.
- Los ciclistas prueban ambos lados de un obstáculo y detectan las cápsulas de los peatones. Superaron tres escenarios: peatón quieto, lado preferido bloqueado y dos peatones. Los semáforos conservan prioridad.
- Los obstáculos invisibles de peatones lejanos dejan de consumir movimiento físico y controladores constantemente. La prueba posterior conserva adelantamiento al anciano, evasión del jugador quieto y altura del suelo (3/3).
- El tráfico usa una cuadrícula espacial de 30 m, limpia solamente celdas ocupadas y guarda geometría y direcciones reutilizadas. La búsqueda de intersecciones coincide con la referencia en 2302 posiciones. Cien vehículos completaron 120 segundos simulados: todos avanzaron, sin solapamientos ni detenciones indefinidas.

## Optimización aplicada

Cien modelos esqueléticos disponen de tres niveles de detalle. La simulación y la animación visible mantienen actualización fluida cerca del jugador; los personajes lejanos reciben un presupuesto menor. La posición visual de los coches sigue interpolándose cada fotograma; solamente las ruedas lejanas reducen su frecuencia a 15 Hz. Se evitan cambios de visibilidad e iluminación repetidos innecesariamente. Resolución de render al 100%, sin reducir la imagen al 85%.

El proyecto jugable no contiene módulos personalizados ni carpeta Source. Los cambios de ejecución son Blueprints y componentes estándar de Unreal. Las herramientas de autoría y recuperación están fuera de la carpeta del juego. GitHub no se modificó.

## Rendimiento medido y límite pendiente

Prueba del mapa completo con 864 peatones y 100 vehículos, en este equipo, en modo Development, resolución efectiva 1920 × 1080 comprobada mediante captura.

| Medición | Resultado |
|---|---:|
| Observador:600 fotogramas tras calentamiento |63,91 FPS de media|
| Ventana CSV de500 fotogramas |66,31 FPS de media|
| Percentil95 del tiempo de fotograma |26,80ms|
| Percentil99 |33,68ms|
| Peor fotograma de la ventana |43,05ms|
| Fotogramas por encima de 16,667 ms |136/500|

La media supera 60 FPS, pero **no se ha alcanzado un mínimo constante de 60 FPS**. Persisten picos de CPU. Tampoco se puede garantizar 60 FPS en cualquier ordenador. Las cifras anteriores obtenidas con una ventana de 888 × 500 quedan descartadas como referencia 1080p.

## Evidencia

- `work/SharedHeroWalkRuntime.log`
- `work/CyclistAvoidanceRuntime.log`
- `work/OptimizedProxyCrowdRuntime.log`
- `work/CachedJunctionAndWalkValidation.log`
- `work/TrafficSnapshotCacheRegression.log`
- `work/Performance60FinalMovementRuntime.log`
- `work/performance60_final_csv_summary.json`

El rendimiento pendiente se registra explícitamente; este informe no afirma que el juego esté libre de todos los posibles errores.

