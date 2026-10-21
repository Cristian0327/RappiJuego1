# Verificación de la migración — 19 de octubre de 2026

La apertura normal del proyecto usa `Bogota_Blueprint_Integration`. El proyecto no declara módulos propios; el código y los binarios anteriores, junto con 26 paquetes dependientes, están en la recuperación fuera de la carpeta del proyecto. No se publicaron cambios en GitHub.

Resultados comprobados:

- La dependencia transitiva del mapa migrado no incluye `/Script/BogotaVoxel`.
- Arranque real sin módulos C++ propios: jugador, pedidos, 864 peatones y 100 vehículos activos.
- Taxis: reserva, puerta trasera, pasajero sentado, viaje y bajada correctos. Doce pasajeros de modelos distintos distribuidos en la ciudad.
- Peatones de cruce: dos pasos diferentes completados y continuación del recorrido. Doce recorridos entre manzanas incorporados.
- Apertura normal del editor en inglés: comprobación del mapa con cero errores y cero advertencias.
- Prueba gráfica integrada a 1280×720: media de 0,033762 segundos por cuadro, unos 29,6 FPS, con 120 cuadros de calentamiento y 180 medidos. La prueba estricta de 30 FPS quedó ligeramente por debajo del objetivo.

Las pruebas dirigidas previas cubren transiciones de conducción, puertas, apoyo sobre bordillos, pasajeros del TransMilenio, recuperación de buses eliminados, pausa, pedidos y persistencia. La animación de caminata con bastón no fue modificada.

Estos resultados comprueban los casos ensayados; no garantizan la ausencia de cualquier fallo posible durante una partida.
