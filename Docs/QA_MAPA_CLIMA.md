# Auditoría de recorridos y clima — 15 de octubre de 2026

Proyecto local: BogotaVoxel. Unreal Engine 5.8.3. Mapa `/Game/Maps/Bogota`.

## Alcance

Se revisaron recorridos, colisiones, alturas, cruces, convivencia entre personas y vehículos y legibilidad del clima. No se rediseñaron las mecánicas de pedidos ni la interfaz del celular. Las pruebas usan perfiles separados de la partida personal y no suben cambios a GitHub.

La simulación contiene 864 peatones, 100 vehículos en circulación y 12 estacionados. El catálogo conserva los 20 modelos particulares con cuatro pinturas por modelo.

## Problemas encontrados y correcciones

| Problema | Corrección |
|---|---|
| El suelo se buscaba respecto de la altura anterior del NPC; podía adoptar superficies cada vez más altas. | Búsqueda de suelo anclada a una franja fija de la calle. En locales se usa su piso de referencia. Se excluyen actores dinámicos de esa búsqueda. |
| La evasión peatonal consideraba personas, pero no paredes. | Barridos de cápsula contra la geometría estática antes de elegir dirección y antes de desplazar al peatón. Recuperación de posiciones iniciales inválidas. |
| Dos edificios junto a la Plaza de Bolívar invadían el recorrido peatonal. | Se retiraron 5 m y 6 m hacia el interior de la manzana; se actualizaron 210 piezas del mapa guardado y las posiciones en su generador. |
| Los carriles y los autos estacionados ocupaban parte del mismo espacio. | Circulación a 2,70 m del eje y estacionamiento a 6 m; se mantienen los modelos y sus escalas. |
| Algunas rutas compartidas del borde hacían aparecer dos ciudadanos en el mismo punto. | Separación inicial a lo largo del tramo peatonal previo al cruce. |
| Tras ciertos giros quedaba una pequeña superposición entre peatones. | Separación residual entre posiciones reales, comprobando paredes y distancia al jugador. |
| La parte trasera del TransMilenio invadía el extremo del andén al retornar. | Retorno más allá del extremo de la estación y seguimiento de orientación acorde con la curva. |
| Los peatones perdían tiempo de simulación cuando una imagen tardaba demasiado. | Acumulador de pasos fijos que conserva el tiempo pendiente. |
| Las gotas usaban un material de sustitución oscuro. | Material de lluvia con soporte explícito de mallas instanciadas; gotas cortas y claras sin colisión ni sombras. |

## Clima

`BP_BogotaCity > NextWeatherState` decide si el clima se mantiene, sube o baja de intensidad a partir de una tirada aleatoria. `RainStartChance`, `DryWeatherHold` y `WetWeatherHold` se ajustan en Class Defaults > World > Weather. Consulta CLIMA_DINAMICO_Y_ESTACIONAMIENTO.md para ver las probabilidades.

La intensidad entra y sale gradualmente. Se reduce la luz solar, cambia el horizonte y aumenta suavemente la bruma. Las gotas se dibujan cerca de la cámara y se ocultan bajo la superficie detectada, incluidas las cubiertas. El ciclo de día y noche continúa activo.

Los controles editables están en Class Defaults > World > Weather. `-ForceRain` se reserva para comprobar el aspecto visual; no es necesario para jugar.

## Método de prueba

La auditoría se ejecuta dentro del juego con las colisiones físicas activas. Una prueba de control confirma que una cápsula colocada dentro de una pared detecta esa pared; así se evita aceptar como válida una sesión de editor sin escena de colisión.

La pasada final combina diez minutos simulados con los 864 peatones y 100 vehículos. Se introducen 24 alturas erróneas de 50 m. Se miden paredes, alturas, proximidad entre peatones, contactos con vehículos, estacionados y geometría, cruces y detenciones. Las posiciones y contactos del mapa se muestrean cada segundo; las decisiones de evasión y los bloqueos se actualizan a 15 Hz.

También se ejecutan tres escenarios de 40 segundos con seis seguidores: jugador inmóvil, peatón lento y esquina bloqueada. La prueba aislada de vehículos dura otros 180 segundos y comprueba los pares de autos a 30 Hz. Incluye una comprobación lógica de interpolación a 60 imágenes por segundo y un retraso artificial de 200 ms; esa comprobación no representa un benchmark de la tarjeta gráfica.

La política de clima se comprueba con muestreo de sus probabilidades y trayectorias largas reproducibles. La lluvia y el granizo se comprueban también bajo cubiertas. Los resultados actuales están en validacion_mapa_clima.json y validacion_clima_dinamico_estacionamiento.json.

## Reproducir la auditoría

Con el editor cerrado, inicia UnrealEditor con el proyecto y estos argumentos:

```text
-game /Game/Maps/Bogota -MapRouteTest -MapAuditSeconds=600 -RenderOffscreen -unattended -UserDir="CARPETA_TEMPORAL_DE_PRUEBAS"
```

Al terminar, la sesión sale y deja `Saved/map_routes_validation.json` bajo el perfil de pruebas. No uses la carpeta de la partida personal como perfil de QA. La revisión visual usa `-RainVisualCheck -ForceRain` y guarda dos capturas antes de cerrar esa sesión de prueba.

Las pruebas cubren el mapa y los catálogos actuales con una distribución reproducible. Un mapa modificado, recursos nuevos u otro hardware requieren volver a verificarse.

## Resultado final

Estado: **PASS** en la ejecución conjunta final de 600 segundos, seguida de las pruebas aisladas y de evasión.

| Medida | Resultado |
|---|---:|
| Peatones / vehículos en circulación | 864 / 100 |
| Cruces completados / infracciones | 113 / 0 |
| Muestras de peatones dentro de paredes / en el aire | 0 / 0 |
| Contactos entre peatones / con vehículos | 0 / 0 |
| Solapamientos entre vehículos en circulación / con estacionados | 0 / 0 |
| Contactos de vehículos con geometría estática | 0 |
| Bloqueos peatonales no planificados superiores a 25 segundos | 0 |
| Mayor detención peatonal no planificada | 2,93 s |
| Menor avance entre los 100 vehículos durante 10 minutos | 1.737,49 m |
| Alturas inválidas introducidas y recuperadas | 24 / 24 |
| Seguidores que superan jugador quieto / peatón lento / esquina bloqueada | 6 / 6 / 6 |
| Separación mínima respecto del jugador en los casos de evasión | 135 cm |
| Contactos entre vehículos durante 180 segundos de prueba aislada a 30 Hz | 0 |
| Imágenes con desplazamiento en la prueba lógica de interpolación | 118 de 120 |
| Tiempo de avance perdido tras el retraso artificial de 200 ms | 0 cm |
| Consultas que detectan la cubierta de prueba | 1.800 de 1.800 |
| Gotas visibles debajo de la superficie detectada | 0 |
| Política de clima | Transiciones probabilísticas: PASS |
| Revisión visual de lluvia de día y de noche | PASS |

Las esperas de vehículos por semáforos y cruces peatonales se conservan: la mayor espera registrada fue 60,93 segundos y todos los vehículos progresaron. No se interpreta una espera legítima de tráfico como un fallo de movimiento.

Capturas: [día](../Capturas/Clima_Lluvia_Dia.png) y [noche](../Capturas/Clima_Lluvia_Noche.png).

La regresión posterior de fluidez y modo desarrollador volvió a pasar estos controles. Se verificaron además 392 segmentos rectos de tráfico con circulación por la derecha y cero segmentos en el lado incorrecto.
