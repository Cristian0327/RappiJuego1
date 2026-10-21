# Abordaje, animaciones por lado y acordeón

- Los NPC vuelven a abordar el Transmilenio: se restauró la consulta de paradas que había quedado fuera de la optimización de tráfico. Espera de18segundos y ventana de abordaje ajustada.
- Subida del jugador a cicla y moto por izquierda o derecha, con animación y desplazamiento correspondientes. Las variantes conservan orientación y velocidad de transición.
- Buses rojo y morado: pliegues del acordeón con pesos graduales entre ambos cuerpos; eje trasero siguiendo el enganche. Límite42grados, recuperación en recta y reinicio seguro tras teletransporte.
- Modo desarrollador: escribir ESOYAM y pulsar F cerca del Transmilenio para subir; F con el vehículo detenido para bajar. Detección por ambos lados y a lo largo del bus.
- Entrada del jugador a carros con variantes por lado, giro hacia la puerta y desplazamiento suave; duración1,3segundos. Cabina cerrada y personaje oculto al conducir conservados.

Validación:43comprobaciones aprobadas,39en ejecución real y4de articulación en la máquina virtual de Blueprints del editor. Incluyen cuatro pasajeros visibles que abordan y bajan, cuatro combinaciones de subida, aproximación corporal por el lado correcto y conducción/salida del bus con F.

Sin cambios en GitHub y sin C++ de ejecución añadido.
