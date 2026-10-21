# Cámara anterior y carrera — 19 de octubre de 2026

A petición del usuario, se revierte el cambio de apariencia de la cámara de la intervención anterior.

- Vuelven sus distancias, encuadre, suavizado, desfase de hombro, campo de visión y rango de inclinación anteriores. Se retiran el desplazamiento vertical adicional, la ocultación del protagonista al acercarse y el bloqueo de cámara añadido a los NPC.
- Se conserva la orientación corregida del personaje, la separación entre WASD y ratón, el montaje rápido y los demás cambios.
- La velocidad de carrera pasa de 390 a 650 cm/s (6,5 m/s). Caminar sigue a 140 cm/s.
- Se reimporta explícitamente el clip de carrera de Mixamo «Unarmed Run Forward», adaptado al personaje voxel. AN_Run_Mixamo usa cadencia1,5 y el Blueprint ajusta su reproducción respecto a650 cm/s. Se evita confundir la carrera con el antiguo recurso llamado AN_MixamoWalk.
- No se modifican las animaciones de los viejitos.

Las seis comprobaciones centradas en este cambio pasaron: caminar normal, velocidad real de carrera y clase de animación, cadencia normalizada, encuadre y suavizado anteriores, rango anterior de cámara y regreso a caminar al soltar Shift. Se midieron650 cm/s. No hubo errores Accessed None en esta ejecución.

Registro: work/CameraRollbackSprintRuntime.log. La captura CAMERA_RESTORED_RUN00000.png se tomó en una plataforma aislada fuera del cielo del mapa; el fondo negro y su aviso corresponden a esa ubicación de prueba.

Todo el comportamiento continúa en Blueprints. Sin cambios en GitHub. Este ajuste reemplaza los límites y el encuadre de cámara descritos en ANIMACIONES_CONTROLES_CAMARA_20261019.md. No constituye una nueva medición general de FPS.
