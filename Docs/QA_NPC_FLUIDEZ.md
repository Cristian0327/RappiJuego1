# Fluidez de NPC y acorralamiento

## Cambios

Los peatones continúan tomando decisiones a 15 Hz, pero su posición y orientación visibles se interpolan en cada imagen renderizada. Los saltos de simulación no se muestran como colocaciones directas del modelo. La creación o recuperación de una posición inválida reinicia el historial visual para evitar interpolaciones desde el origen o desde una altura errónea.

Se desactivó la reducción de frecuencia de animación en los NPC visibles y en los personajes de locales. Los personajes fuera de vista conservan la gestión de visibilidad del motor.

La evasión ahora comprueba el límite de la calzada además de las paredes. La separación entre peatones también respeta ese límite. Un peatón acorralado no es empujado hacia los carros: si no existe espacio físico para pasar, cede el paso sin girar de forma errática. Puede retroceder si el jugador está demasiado cerca y vuelve a caminar cuando se libera el paso.

## Pruebas

La prueba de interpolación usa 120 imágenes a 60 Hz y decisiones a 15 Hz. El resultado esperado es al menos 114 imágenes con desplazamiento, sin escalones de más de 4 cm; se conserva el tiempo pendiente ante un retraso artificial de 200 ms. Esta prueba evalúa el movimiento mostrado, no garantiza un rendimiento de 60 FPS del equipo.

Se construyen dos aceras estrechas, una a cada lado de una calle, con una pared y un jugador bloqueando el paso. Cada escenario contiene seis peatones. Se comprueba que cedan el paso sin invadir la carretera, que no oscilen mientras esperan y que todos avancen tras retirar al jugador.

Los comandos se prueban mediante el sistema real de consola del jugador: modo desarrollador, lluvia inmediata, clima automático, entrada y salida de particulares, taxis, buses y estacionados, conducción por entradas de Blueprint, freno ante paredes y peatones, salida bloqueada y restauración del saldo. También se prueba un vehículo perpendicular a la ruta de otro auto.

La medición de movimiento en una sesión renderizada y las capturas de cámara se guardan junto con los resultados finales. La regresión independiente del mapa ejecuta otros 600 segundos con 864 peatones y 100 vehículos.

Resultados: `validacion_npc_desarrollador.json` y `validacion_mapa_clima.json`.

Reproducción con un perfil temporal separado de la partida personal:

```text
UnrealEditor.exe BogotaVoxel.uproject -game /Game/Maps/Bogota -NpcDeveloperTest -RenderOffscreen -unattended -UserDir="CARPETA_QA"
```

Se guarda `Saved/npc_developer_validation.json` y la sesión termina. La prueba de cámara y cadencia real usa `-DeveloperCarVisualCheck` y genera dos capturas y `Saved/npc_live_render_validation.json`.

## Cámara y coherencia vial

La cámara del conductor ignora únicamente el volumen del propio vehículo; mantiene la detección del escenario. Antes podía retraerse hasta quedar dentro del modelo. Se comprueba tanto esa exclusión al subir como su restauración al bajar.

Los circuitos de particulares y buses y la orientación de estacionados se corrigieron para circular por la derecha. La auditoría mide el lado de la vía en los segmentos rectos de los circuitos, además de comprobar contactos y progreso durante diez minutos simulados.

## Resultado final: PASS (15 de octubre de 2026)

Pasaron los 25 controles de comandos, conducción y seguridad. En interpolación se movió el modelo en 116 de 120 imágenes, con un máximo de 1,87 cm por imagen. En la sesión renderizada se detectó movimiento en 699 de 701 imágenes rastreadas; esta proporción mide continuidad, no los FPS del equipo.

Ambos escenarios de acorralamiento cedieron el paso y retomaron el recorrido, sin invadir la calle ni girar mientras esperaban. La separación mínima del jugador fue de 143,56 cm. La cámara de conducción se mantuvo a más de 10 metros del punto del conductor.

La regresión de 600 segundos con 864 peatones y 100 vehículos pasó sus 21 controles; completó 113 cruces sin infracciones y no registró contactos, peatones en paredes o en el aire ni bloqueos prolongados.

Capturas revisadas: [conducción](../Capturas/Developer_Carro.png) y [conducción con lluvia](../Capturas/Developer_Carro_Lluvia.png). Las pruebas usan el mapa y la distribución actuales; cambios futuros requieren repetirlas.
