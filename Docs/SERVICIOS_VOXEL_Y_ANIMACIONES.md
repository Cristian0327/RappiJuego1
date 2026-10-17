# Policías, motos y animaciones — 16 de octubre de 2026

Hay cuatro modelos de policías: dos hombres y dos mujeres, con distintos rostros y cabellos. El mapa tiene 24 policías a pie, repartidos por los bloques de la ciudad: 12 hombres y 12 mujeres. Sus recorridos son fijos; solo se desvían si el jugador bloquea el paso.

Circulan 13 motos civiles, seis motos policiales y cinco patrullas. Las motos civiles tienen seis variantes de pintura y equipamiento; las policiales, dos. Hay conductores de ambos sexos. Las seis motos policiales se reparten entre tres hombres y tres mujeres; las patrullas también llevan conductores visibles.

Los trece modelos editables están en `../../outputs/DeliveryArt/Services/`. Conservan la geometría voxel y las texturas de rostros originales. El atlas de color tiene filtrado de vecino más cercano. Las patrullas tienen cabina, asientos, volante y cristales transparentes. Su espacio interior se amplió manteniendo la cuadrícula de cuatro centímetros, sin reducir al personaje.

Se rehizo el conjunto de 29 recursos de animación utilizados o conservados como compatibilidad: reposo, caminata, carrera, salto, pedaleo, conducción de moto y carro, entrada y salida de carro, caminata con bastón, desplazamiento de andén de estación y los gestos de trabajo o espera de los ocho tipos de comerciantes y clientes. Las fuentes están en `../../outputs/DeliveryArt/AnimationRebuild/`; las animaciones de locomoción y entrada o reposo sentado parten de Mixamo, adaptadas en Blender. El pedaleo, los agarres y los gestos de trabajo se ajustaron en Blender a los modelos voxel.

La adaptación utiliza la postura de reposo del esqueleto, no el primer fotograma de la caminata anterior. Se revisó la dirección de las rodillas, se eliminó el desplazamiento vertical duplicado del salto y se sincronizó la reproducción con la velocidad de apoyo de los pies. Los pies del ciclista y de los motociclistas se alinearon con sus pedales y estribos en todos los fotogramas. También se comprobaron los 193 fotogramas de conducción de cada una de las cuatro variantes de policías bajo el techo de la patrulla.

Las rutas nuevas, la detección de obstáculos, el desvío alrededor de estacionados, la comprobación del tráfico trasero y el registro compartido de obstáculos funcionan con Blueprints derivados de clases de Unreal. El registro ignora personajes de interiores situados bajo el mapa para evitar falsas obstrucciones en la calzada.

## Validación

- Pasaron 65 comprobaciones de regresión de peatones, vehículos, clima y controles.
- Pasaron las 16 comprobaciones reales de caminar y volver a reposo o trabajo de los ocho tipos de comerciantes y clientes.
- En la prueba de 90 segundos, los 24 vehículos nuevos recorrieron entre 341 y 579 metros cada uno. Las motos que antes se quedaban detenidas junto a estacionados continuaron su recorrido.
- Las comprobaciones de esos recorridos no registraron errores de Blueprint. Los policías a pie permanecieron a la altura del suelo.
- Se revisaron en Unreal el pedaleo y la conducción de moto del protagonista, además del encaje del conductor en Blender.

Los informes detallados están en `variaciones_y_animaciones_2026-10-16.json`, `sincronizacion_animaciones.json` y `validacion_servicios_y_animaciones_blueprints.json`. Las capturas y los registros de las pruebas se conservan junto al proyecto, en `../../work/`.

## Trabajo que continúa pendiente

La migración completa a Blueprints sigue en curso: permanecen siete Blueprints con bases propias de C++, además de otros sistemas nativos del proyecto. No se eliminaron las clases que el juego todavía necesita. El protagonista conserva por ahora su base de animación anterior, aunque sus recursos de animación ya fueron reemplazados. Los ocho tipos de comerciantes y clientes sí heredan directamente de AnimInstance.

Este trabajo no da por terminados los pasajeros visibles de TransMilenio, el ciclo completo de taxis, las direccionales o el ciclo automático completo de las puertas. No se afirma que el proyecto completo esté libre de C++.

La clave `PUERTAS` permite inspeccionar puertas de vehículos detenidos en modo desarrollador. Pasaron nueve casos de apertura, cierre y seguridad con carro y TransMilenio. Las instrucciones están en `PRUEBA_PUERTAS_DESARROLLADOR.md`. Esta herramienta no sustituye el embarque automático pendiente.
