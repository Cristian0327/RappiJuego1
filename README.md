> Estado de desarrollo pausado (test / Michaelxd). Las calles y los pedidos tienen pruebas aprobadas; el trafico sigue pendiente. Leer [el informe de continuacion](Continuacion/CONTINUAR_EN_OTRO_PC.md).

# Bogotá Voxel — proyecto editable de Unreal

Abre **BogotaVoxel.uproject** con Unreal Engine **5.8.3** y pulsa **Play**. El mapa inicial es `/Game/Maps/Bogota_Blueprint_Integration`.

La lógica del proyecto funciona con Blueprints y componentes de Unreal. No requiere compilar módulos C++ ni instalar Visual Studio. Unreal prepara sus cachés y shaders al abrirlo por primera vez.

## Carpetas

- `Content/World/BlueprintWorld`: ciudad, clima, tráfico, peatones, servicios y modo de juego.
- `Content/Delivery/BlueprintGameplay`: jugador, vehículos, pedidos, progresión, celular y garaje.
- `Content/Delivery/BlueprintSchema`: estructuras, enumeraciones y partida guardada.
- `Content/Crowd` y `Content/Traffic`: modelos, materiales y animaciones.
- `Config`: controles, navegación y presentación.

Los recursos antiguos que dependían del código retirado se conservan fuera del proyecto, en la carpeta de recuperación de la entrega. No son necesarios para jugar.

## Controles

| Acción | Tecla |
|---|---|
| Moverse / conducir | WASD |
| Mirar y dirigir | Ratón |
| Abrir o cerrar celular | TAB |
| Interactuar / recoger | E |
| Subir o bajar del vehículo cercano | F |
| Impulso | SHIFT |
| Saltar / frenar | Espacio |
| Pausar / continuar | ESC |

Selecciona un pedido en el celular antes de recogerlo. El taller muestra la progresión y el garaje dentro del formato vertical del teléfono.

## Claves de pruebas

Escribe las claves directamente durante Play, con el celular cerrado:

- **ESOYAM**: modo desarrollador.
- **CARRO**: habilitar la interacción de prueba con carros; usa **F** para entrar o salir con su transición.
- **MORADO**: crear el TransMilenio morado.
- **LLUVIZNA**, **LLUVIA**, **GRANIZO**, **TORMENTA**, **SOLEADO**: forzar un estado del clima.
- **CICLO**: regresar al clima automático.

## Editar

Consulta [BLUEPRINTS.md](Docs/BLUEPRINTS.md). Los cambios de esta entrega son locales; no se han subido a GitHub.
