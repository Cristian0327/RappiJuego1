# Entrada a carros y cruce del jugador

- Animación de entrada de Mixamo ajustada en Blender: gira hacia la puerta y termina mirando al frente; salida reproducida en sentido inverso.
- Postura sentada continua al terminar; asiento proporcional al ancho y largo del carro. Restauración explícita de la posición y orientación de la malla al salir.
- El tráfico comprueba la posición del jugador, su aproximación lateral, la altura y la distancia al frente del carro; reduce velocidad, limita el avance antes del peatón y reanuda al quedar libre.
- Conserva WASD, cámara, caminata y carrera anteriores. Lógica del juego en Blueprints; no se añadió C++ de ejecución ni se publicó en GitHub.

Validación: 7/7 comprobaciones en el juego real. Resultados: work/car_entry_yield_final.json. Registro: work/CarEntryYieldRuntime2.log.
La prueba usa un carro de referencia; no representa una auditoría visual individual de cada modelo de vehículo.
