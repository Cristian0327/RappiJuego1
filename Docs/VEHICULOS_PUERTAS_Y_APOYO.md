# Apoyo de ruedas y puertas

El carro consulta el suelo bajo las cuatro ruedas. La carrocería se inclina según ese plano de apoyo y converge suavemente para evitar saltos. Cada rueda tiene hasta 18 cm de recorrido visual para adaptarse al terreno irregular. Al estacionar, la inclinación del terreno se mantiene. Si faltan apoyos o la pendiente es excesiva, la conducción de pruebas detiene el avance.

Los carros particulares y taxis tienen dos bisagras. El NPC se acerca, alcanza la puerta, espera su apertura, entra y la cierra. Al salir se abre antes de que abandone el carro. La puerta del lado de la acera es la que se usa.

Los TransMilenio tienen dos hojas corredizas en la puerta de abordaje. Se abren con el bus detenido y alineado en una estación. El pasajero espera la apertura, camina por la plataforma y atraviesa la puerta; al llegar a la siguiente estación sale caminando. Se conserva la espera del bus durante el cruce de pasajeros y se impide que arranque con la puerta abierta. Las puertas del lado de la plataforma son las utilizadas.

El abordaje respeta las paredes de la estación y la posición del jugador. Si alguien bloquea el paso, el pasajero espera y el bus mantiene la parada para no cerrar sobre él.

Los modelos mantienen sus huesos de ruedas y articulación. Se añadieron door_L y door_R a carros y taxis, y bus_door_a y bus_door_b a los TransMilenio rojo y morado. La pintura por instancia y la forma corregida del Escarabajo se conservan.

La ruta dentro de la estación pasa por un lateral del pilar central antes de alinearse con la puerta. Las hojas del TransMilenio se orientaron hacia el lado de la plataforma al convertir las coordenadas de Blender a Unreal. Las bisagras de los particulares también se seleccionan por su lado real en el modelo importado.

Para reconstruir los modelos desde las fuentes, se ejecutan build_vehicle_doors.py, texture_traffic_pixel.py, prepare_traffic_paint_mask.py y mirror_bus_platform_side.py, en ese orden, antes de importar. Las texturas y la máscara de pintura deben exportarse junto con las puertas. Las fuentes previas de geometría se conservan en outputs/VehicleDoorBases.

Las aberturas de las mamparas de todas las estaciones se alinearon a ±380 cm del centro, con huecos de 360 cm. Se retiran los tramos anteriores para evitar que quede vidrio delante de una puerta abierta.

## Resultado de validación

PASS: 40 controles generales y 13 controles de apoyo, puertas y abordaje. Se comprobó una pendiente transversal de 8 grados, el rechazo de apoyos ausentes, ambas direcciones de abordaje, la salida en otra estación y el bloqueo de arranque con la puerta abierta. El mayor paso de posición durante el abordaje fue de 3,67 cm a 30 Hz. En la sesión renderizada, el carro quedó inclinado 6,19 grados en un bordillo real del mapa y el pasajero llegó al interior por la puerta abierta.

La regresión de diez minutos con 864 peatones y 100 vehículos pasó sus 21 controles: 113 cruces, ningún contacto registrado, ningún peatón en paredes o en el aire y ningún bloqueo prolongado. Todos los vehículos avanzaron; el menor recorrido fue de 1.737,49 metros. Los apoyos detallados se consultan para los vehículos cercanos y para los conducidos o estacionados por el jugador.

Resultados: validacion_vehiculos_puertas.json y validacion_mapa_clima.json. Capturas: [carro inclinado](../Capturas/Carro_Inclinado.png), [apertura del carro](../Capturas/NPC_Abre_Carro.png), [abordaje del bus](../Capturas/NPC_Sube_Transmilenio.png) y [puerta de la estación](../Capturas/Transmilenio_Puerta_Abierta.png).

La población estacionada ahora incluye cuatro carros parcialmente sobre el andén y ocho al borde de la calzada. La selección y los pequeños ángulos de estacionamiento cambian entre sesiones. Véase CLIMA_DINAMICO_Y_ESTACIONAMIENTO.md.
