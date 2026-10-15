# Ruta / sistema voxel

## Scene

Una persona juega en escritorio mientras recorre una ciudad cambiante entre día y noche; necesita paneles opacos legibles sobre edificios, asfalto y vegetación.

## Visual system

Conservar turquesa y naranja. Superficies azul petróleo oscuro, texto marfil claro, selección naranja con tinta oscura. El turquesa identifica navegación y seguimiento; el naranja identifica confirmación y selección.

Botones con silueta escalonada, cara superior iluminada y cara inferior sombreada, sin degradados ni esquinas redondas. Texturas procedurales pequeñas con filtrado nearest y nueve segmentos que conservan las esquinas. Estados normal, hover, pressed, disabled y selected compartidos en las aplicaciones.

Fuente RutaPixel existente. Encabezados breves; cuerpo en caja mixta. Etiquetas y razones explícitas para estados bloqueados. Navegación inferior resalta la aplicación actual. Paneles HUD con borde completo y relieve de bloques.

## Responsive behavior

Conservar el teléfono y sus áreas interactivas con escala uniforme. Evitar giro y deformación durante apertura. Ajustar HUD a la resolución; ayudas legibles y mapa con instrucciones separadas. Validar 1024×576, 1280×720 y 1920×1080.

## Garaje y progresión final

Conservar siempre el celular original de 420 × 680 y su escala. Cuatro nodos de cicla y seis de moto se conectan dentro de la pantalla; las flechas siguen su posición. El detalle del nodo explica el requisito y el coste. El modelo se presenta en un escenario 3D voxel con suelo, paredes, banco y herramientas, con cámara alejada y proporción de captura ajustada al visor. No ampliar el celular a una tableta.
