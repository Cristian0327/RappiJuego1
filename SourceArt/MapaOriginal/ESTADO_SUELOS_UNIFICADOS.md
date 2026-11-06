# Suelos y parques — revisión del 27 de octubre de 2026

Complementa ESTADO_ANDENES_ESTACIONES.md. El mapa principal y las calles permanecen en /Game/Maps/MapaOriginal_Reconstruido.

Se corrigen las bases restantes en 37 parques y plazas, incluidas las dos instancias del parque del lago que conservaban casi un metro de plataforma. Las superficies de suelo de estos modelos se extraen, se nivelan a 20 cm y se reúnen en SM_Ciudad_SueloContinuo. Los elementos del parque conservan su forma por encima de la base corregida.

Cada región de suelo tiene un propietario: primero calzada y acera, después los pavimentos originales de los parques y finalmente la cobertura general. Las piezas de cobertura se recortan geométricamente, no con una máscara de textura ni desplazándolas un poco hacia arriba. Se eliminan solapamientos de borde en 7.933 rectángulos. Los suelos conservan la paleta original de césped, canchas y plazas.

El terreno subyacente se rebaja solo bajo las superficies planas y su transición inmediata. 30.432 muestras geométricas no encontraron terreno atravesando el suelo. Se repite la comprobación física de 5.522 puntos en Unreal.

Siete mallas modificadas; no se modifican Blueprints de tráfico, rutas, semáforos, tiendas, posiciones XY ni escalas del escenario. El Blender original de Downloads sigue intacto.

Herramientas de esta revisión: repair_park_bases.py, unify_ground_ownership.py, export_owned_ground.py, import_owned_ground.py y check_owned_ground.py, dentro de la carpeta de trabajo map_reconstruction_20261027. No ejecutar el antiguo build_surfaces.py sin incorporar el recorte exacto: volvería a crear bordes superpuestos. Las nuevas fuentes y manifiestos de esta carpeta sustituyen los de la revisión anterior.
