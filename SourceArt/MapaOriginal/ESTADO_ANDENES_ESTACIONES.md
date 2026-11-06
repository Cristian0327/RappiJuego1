# Andenes, bases y estaciones — 27 de octubre de 2026

Proyecto principal: C:/Users/CRISTIAN/OneDrive/Desktop/BogotaVoxel_JuegoCompleto/RappiJuego1/BogotaVoxel.uproject
Mapa: /Game/Maps/MapaOriginal_Reconstruido. Unreal 5.8.4.

## Cambios
- Se conservan las calles principales y las 14 calles secundarias conectadas. No se cambian posiciones XY ni escalas de los edificios en esta revisión.
- Se amplía y une el pavimento residencial; se conserva toda el área de andén anterior y se evita invadir el asfalto. Se protegen 41 zonas verdes especiales, con excepciones de las huellas reales de viviendas.
- Material opaco M_BogotaLadrillo: ladrillos de 24 x 12 cm en coordenadas mundiales, juntas y variación de color; caras laterales de bordillo en concreto. Sin recortes por máscara ni desplazamiento de vértices.
- Se nivelan las plataformas propias de 75 mallas, correspondientes a 892 instancias, al datum común de andén de 20 cm. Se trabaja desde la copia anterior, evitando aplicar dos veces la corrección.
- Nueve estaciones: se mantienen los siete IDs existentes y se añaden 7 y 8. Alineación según la tangente real de la ruta de bus; nuevas puertas orientadas hacia el bus. Se sincronizan pasajeros, bancos, farolas y las nueve paradas del vehículo.
- Dieciocho accesos peatonales; uniones al pavimento corregidas. Las rampas elevadas comienzan después de los carriles.

## Verificación
- Simulación funcional de aproximadamente 126 segundos a paso fijo de 30 Hz: los 90 vehículos se desplazaron; 63 muestras sin solapamientos de envolventes de carrocería; cero errores de ejecución de Blueprint. No es una medición de rendimiento ni garantiza todos los recorridos posibles.
- 253 personajes muestreados; 176 se desplazaron. Pasajeros en espera y personajes sentados pueden permanecer quietos.
- Suelo: 5.522 puntos sin fallos durante simulación y una segunda comprobación sin fallos después de unir los accesos.
- Ninguna plataforma corta los enlaces existentes del grafo de navegación.
- Blender original preservado: SHA256 AE21D899B4A27EE874E60ACDBF9D0888E674CD45B55A68C93F223B10686D2B0B.

## Continuidad
Revisar visualmente los andenes y las transiciones en juego. La prueba no recorre todas las tiendas ni todas las combinaciones de pedidos; existe la prueba anterior de un pedido completo y las pantallas del celular. Conservar las correcciones de tráfico, arcos de cruces, separación entre buses y caché de navegación. No ejecutar de nuevo el escalado global ni reasignar M_MapaVoxel a la geometría reconstruida.

La copia de autoría contiene módulos auxiliares solo para edición. No trasladar su descriptor, Binaries ni DLL al principal. Copiar únicamente los contenidos del manifiesto de promoción, con respaldo previo.
