# Cicla, caminata y patrullas — 19 de octubre de 2026

Cambios guardados en el proyecto del escritorio, mapa `Bogota_Blueprint_Integration`:

- Las cinco patrullas del mapa ya no muestran un policía dentro. Su clase también queda sin conductor visible. Los policías de la calle y las motos permanecen.
- Los vidrios de las patrullas usan el material voxel opaco y su atlas de píxeles original.
- El protagonista usa la caminata equivalente a los NPC, con la misma escala de reproducción y la misma regla de cadencia según velocidad. La velocidad normal es 140 cm/s y la de sprint 390 cm/s. Los ancianos no cambian.
- La cicla aparece al iniciar una partida, en un punto de suelo validado. Se conserva la interacción real de subir y bajar con F; no es una decoración.
- El muestreo de pedaleo del protagonista y los ciclistas avanza en el sentido físico correcto. Las bielas de los NPC giran en el mismo sentido; los ciclistas inicialmente detenidos no pedalean solos.

Prueba final renderizada: ocho comprobaciones correctas, incluyendo aparición, tipo de bicicleta, caminata, subida con F, reproducción de pedaleo del protagonista y NPC, pie delantero bajando y bajada con F dejando la cicla estacionada. El sentido del pie se verificó con sus posiciones animadas: puntuación -1286,60; un valor negativo corresponde a pedalear hacia adelante. Sin errores «Accessed None».

Evidencia: `work/BikePatrolCorrectionsFinalRuntime.log`, `work/bicycle_walk_patrol_patch.json` y `work/PureIntegratedVisualQA/BICYCLE_FIX00001.png`.

Todo el comportamiento modificado queda en Blueprints. No se añadieron módulos C++ ni se hicieron cambios en GitHub. El objetivo previo de un mínimo constante de 60 FPS sigue registrado como pendiente; esta prueba se centró en las cuatro correcciones solicitadas.
