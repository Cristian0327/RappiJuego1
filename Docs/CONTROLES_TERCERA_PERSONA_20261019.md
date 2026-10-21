# Control de tercera persona — 19 de octubre de 2026

Se sustituye el control que guardaba el rumbo al empezar a pulsar una tecla. Ahora el movimiento a pie utiliza continuamente la orientación horizontal actual de la cámara.

- A pie: W avanza respecto a la cámara; S retrocede respecto a ella; A/D se mueven a izquierda/derecha de la vista. El personaje gira suavemente hacia su avance. Mantener W y girar la cámara cambia la dirección sin tener que soltar la tecla.
- Mirar estando quieto mueve la cámara y mantiene la orientación del personaje. El movimiento usa únicamente el ángulo horizontal de la vista, sin subir o bajar por mirar hacia arriba/abajo.
- Las diagonales mantienen la misma velocidad. Caminar sigue a140 cm/s y correr a650 cm/s con el clip de Mixamo.
- En vehículos: W/S acelera, frena o retrocede; A/D dirige; el ratón permite mirar. La cámara vuelve suavemente detrás del vehículo después de1,5 segundos sin entrada de mirada mientras se conduce, conservando la inclinación elegida.
- Se mantiene el encuadre restaurado en la intervención anterior. El brazo de cámara sigue el giro y la inclinación de la vista, sin heredar giro lateral ni añadir retraso a la rotación del ratón.
- La implementación permanece en Blueprints. Las animaciones, el montaje y los comandos de desarrollador se conservan.

## Comprobación

14/14 casos pasaron en el juego: W con cámara inicial, giro del cuerpo hacia el avance, giro de cámara sin soltar W, órbita en reposo, S con cámara inclinada, A/D relativos a la cámara, velocidad diagonal normalizada, carrera de Mixamo, montaje de bicicleta, mirada sin dirección de vehículo, demora de mirada libre, dirección por teclado y seguimiento suave de cámara.

Registro: work/StandardControlsRuntime.log. Sin errores Accessed None en esa ejecución. Es una comprobación centrada en los controles; no es una medición nueva de FPS ni una auditoría de todo el mapa.

Fuentes de autoría: work/rebuild_standard_third_person_controls.py y work/build_standard_controls_qa.py. Sin cambios en GitHub.
