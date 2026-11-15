# Estado de reanudación — 23 de octubre de 2026

Origen verificado: BogotaVoxel, rama test, commit 5cab1acffb4c46087e8387df448f2301a28fadb3 (Michaelxd). Git status inicial limpio.

Las carpetas ModulelessRuntime y BlueprintAuthoring son copias físicas de Content y Config. No son junctions. El descriptor original sigue sin módulos propios. La copia de autoría utiliza las herramientas incluidas (BuildId 55116800, igual al motor instalado).

Las partidas personales originales permanecen en BogotaVoxel/Saved/SaveGames. Sus SHA-256 iniciales están en personal_save_hashes.json. Los ensayos usan TestUser o DiagnosticUser mediante -UserDir y no contienen copias de las partidas personales.

Primer arranque renderizado: traffic_resume_baseline.log. Se detuvo deliberadamente antes de comenzar el ensayo, por presión de memoria durante la preparación de recursos. No representa una prueba de tráfico ni un cierre espontáneo.

Se adaptaron las rutas absolutas de copias de los scripts bajo scripts/. No se ejecutó la secuencia histórica de reparaciones.

build_resume_diagnostics.py amplía el actor QA con State, RouteIndex, Goal, TrafficSpeedLimit, MaxWalkSpeed, MovementMode, posición, velocidad y actor/componente/punto del impacto de la sonda estática. Compilación correcta: build_resume_diagnostics2.log, marcadores V2_TRAFFIC_PROBE_READY y RESUME_DETAILED_PROBE_READY. El primer intento falló por GetMovementName no expuesto; se sustituyó por lectura de MovementMode. No se promovieron cambios al proyecto original.

Ensayo diagnóstico actual: traffic_resume_v10.log, 365 segundos de simulación previstos, nullrhi para reducir memoria de renderizado. Requiere análisis posterior; no aprobado. analyze_resume.py utiliza solo la biblioteca estándar y filtra los 90 vehículos principales; mide desplazamiento muestreado y duración de inmovilidad por vehículo. El desplazamiento entre muestras no sustituye una medición exacta por arco ni la revisión de colisiones.

Equipo: aproximadamente 7 GB de RAM utilizable. Se ejecuta una instancia de Unreal cada vez. Los límites de compilación asíncrona solo se añadieron a Config de las copias aisladas.
Resultado v10: cerró normalmente a 365.20727 segundos de simulación. Último muestreo 10/90 moviéndose; 58 vehículos con inmovilidad continua muestreada >=110 segundos. Bloqueos de sonda persistentes: ciclistas 3/8 contra StationShell de estación 2, ciclista 7 contra estación 4, ciclista 1 contra Pole de semáforo 17, ciclistas 0/10 contra StaticMeshActor_47/_7. No aprobado. El primer análisis de carrocerías no encontró solapamientos; repetir sobre el registro completo.
