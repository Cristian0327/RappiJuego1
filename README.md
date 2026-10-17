# Bogotá Voxel — proyecto editable de Unreal

Proyecto completo de un juego de repartos en Bogotá, con ciudad voxel, peatones, tráfico, ciclo día/noche, cicla y motos, tiendas, pedidos y celular con progresión de mejoras.

## Descargar y abrir

1. En GitHub pulsa **Code → Download ZIP**, o **Open with GitHub Desktop** para clonar y colaborar.
2. Extrae toda la carpeta a una ubicación local, por ejemplo `Documentos/RappiJuego1`. No abras el proyecto dentro del ZIP.
3. Instala **Unreal Engine 5.8.3** desde Epic Games Launcher. Esa es la versión con la que se preparó esta entrega.
4. Abre `BogotaVoxel.uproject`. El mapa inicial es `/Game/Maps/Bogota` y se carga automáticamente.
5. Espera a que Unreal prepare los shaders y pulsa **Play** para probar el juego.

No es un instalador ni una versión empaquetada. Incluye los archivos editables de Unreal y los módulos de editor compilados para Windows y UE 5.8.3. Unreal Engine se instala por separado.

Si Unreal pide recompilar módulos, o si cambias código C++, instala Visual Studio 2022/Build Tools con **Desarrollo de juegos con C++**, MSVC v143 y Windows SDK. Después genera los archivos de proyecto desde el `.uproject` y compila `BogotaVoxelEditor / Development Editor / Win64`. El código fuente completo está incluido; también puedes utilizar otra versión compatible recompilándolo, pero la entrega se comprobó con 5.8.3.

## Qué contiene

- `Content`: mapa, personajes, animaciones, edificios, locales, vehículos, materiales, texturas, Blueprints y widgets.
- `Source`: lógica de juego, interfaz, tráfico, personajes y herramientas de editor.
- `Config`: mapa inicial, controles y configuración visual.
- `DeliveryData`: catálogos editables de mejoras, vehículos y locales.
- `Binaries/Win64`: módulos de editor para abrir esta versión en Windows.
- `Docs` y `Capturas`: guía de colaboración y referencias del aspecto actual.

Los recursos están guardados como archivos reales de Unreal: no se necesita Git LFS y el ZIP de GitHub incluye los modelos y mapas completos. Las cachés, partidas personales, registros e instaladores no forman parte del repositorio.

## Blueprints y colores

Las reglas de juego se editan en [Blueprints](Docs/BLUEPRINTS.md). Los autos particulares y estacionados tienen pintura por instancia, conservando vidrios, llantas, luces y placas.

## Controles

| Acción | Tecla |
|---|---|
| Moverse | WASD |
| Mirar | Ratón |
| Abrir/cerrar celular | TAB |
| Acción / recoger / aceptar manteniendo | E |
| Subir o bajar del vehículo | F |
| Cambiar vehículo | V |
| Impulso | SHIFT |
| Saltar / frenar | Espacio |
| Pausa | ESC |

En el celular, usa ratón o flechas. Enter también confirma; la aceptación de un pedido requiere mantener la tecla. El taller conserva el tamaño del celular y muestra las mejoras conectadas; el garaje tiene un escenario voxel.

## Probar y modificar con amigos

Lee [COLABORAR.md](Docs/COLABORAR.md). Para cada cambio, crea una rama y abre un pull request. El proyecto es público para que cualquiera pueda descargarlo y probarlo. Los colaboradores invitados pueden enviar cambios directamente en sus ramas.

Al abrir por primera vez se regeneran las cachés. Esto puede tardar; no falta contenido por esa preparación inicial. Las partidas empiezan desde cero en cada equipo.

## Clima y recorridos

La ciudad incluye lluvia ocasional con transición gradual, cielo e iluminación adaptados y detección de techos. Las probabilidades se editan en `BP_BogotaCity`. Consulta [la auditoría del mapa y clima](Docs/QA_MAPA_CLIMA.md) para ver las correcciones de peatones, vehículos y los resultados de las pruebas.

## Pruebas de desarrollador

Durante Play, escribe **ESOYAM** directamente para activar el modo desarrollador. Escribe **LLOVIZNA**, **LLUVIA**, **GRANIZO**, **SOLEADO** o **CICLO** para controlar el clima y **CARRO** para subir o bajar del carro cercano. No necesitas abrir la consola ni pulsar Enter; mantén el celular cerrado. **F** cerca de un carro también permite subir. Consulta [los comandos y controles](Docs/COMANDOS_DESARROLLADOR.md), incluyendo los efectos del modo de pruebas sobre pedidos activos, y [la revisión de fluidez y evasión](Docs/QA_NPC_FLUIDEZ.md).

La lluvia alterna entre leve, normal y tormenta con granizo, relámpagos y truenos. Consulta [los niveles de clima y la corrección de las puertas del Escarabajo](Docs/CLIMA_Y_PUERTAS.md).

Los vehículos cercanos adaptan la carrocería y las ruedas al terreno; la inclinación se mantiene al estacionar. Los NPC abren las puertas de los carros y los pasajeros caminan por la puerta del TransMilenio cuando está abierto en la estación. Consulta [apoyo de ruedas y puertas](Docs/VEHICULOS_PUERTAS_Y_APOYO.md).

El clima automático es probabilístico: puede intensificarse desde llovizna hasta tormenta, o bajar progresivamente hasta quedar seco. Un tercio de los carros estacionados se coloca parcialmente sobre el andén, con inclinación real del terreno. Consulta [clima dinámico y estacionamiento](Docs/CLIMA_DINAMICO_Y_ESTACIONAMIENTO.md).
