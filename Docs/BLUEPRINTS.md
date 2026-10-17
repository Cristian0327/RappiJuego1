# Editar las reglas del juego en Blueprints

Proyecto: Unreal Engine 5.8.3. Abre `Content/Maps/Bogota` y pulsa Play.

| Blueprint | Lógica editable con nodos |
|---|---|
| `/Game/Delivery/Core/BPC_DeliveryGameplay` | Ofertas, aceptación, recogida, entrega, mejoras, compras, capacidad de carga, energía, vehículos y guardado |
| `/Game/Delivery/Vehicles/BP_DeliveryRider` | Movimiento, cámara, velocidad, dirección, interacción con E, pausa, calidad y salto de hora |
| `/Game/Delivery/UI/WBP_VoxelPhone` | Acciones y selección de aplicaciones, pedidos, taller, garaje, pintura y equipamiento; diseño UMG del teléfono |
| `/Game/Delivery/Orders/BP_DeliveryBuilding` | Clientes, posiciones interiores y reglas de recogida |
| `/Game/Delivery/Orders/BP_VoxelCustomer` | Comprobación y recepción de entregas |
| `/Game/Delivery/Animation/ABP_*` | Estados y ritmos de las animaciones |
| `/Game/World/BP_BogotaCity` | Reloj, distritos, fases de semáforos, elección de pintura de los autos, clima probabilístico y plan de estacionamiento |

Las 93 implementaciones duplicadas de estas reglas se retiraron de C++. Además, interacción de teclado, acción, pausa, calidad y salto de hora pasaron a Blueprints: 98 funciones de reglas en total. Las declaraciones `BlueprintImplementableEvent` solo conectan el motor con los grafos; ya no contienen una implementación alternativa de esas reglas en C++.

Se retiraron los 12 grafos antiguos que solo llamaban al código nativo, las llamadas al padre sin uso, el HUD del prototipo y su prueba antigua. Usa las clases BP anteriores al crear instancias, porque las clases base nativas no implementan sus reglas.

## Pintura de autos

Abre `BP_BogotaCity` y entra en Class Defaults > World > TrafficPaint. `TrafficPaintPalette` tiene 12 colores editables. La función `TrafficPaintFor` decide qué color recibe cada instancia; puedes modificar sus nodos.

Los 20 modelos particulares tienen una máscara explícita de carrocería en UV1. El material `M_TrafficVoxelVertex` utiliza `BodyPaint` y `PaintEnabled`; cada auto obtiene su propia instancia dinámica. La textura de píxeles y las piezas que no son pintura se conservan. Los 12 autos estacionados también varían. Taxis y buses conservan sus colores de servicio. La comprobación detectó 12 colores en los autos particulares en circulación y al menos 4 colores para cada modelo.

## Soporte nativo conservado

El proyecto sigue siendo híbrido. Se conserva C++ para la generación e instanciación de la ciudad, la simulación masiva del tráfico y la evasión de peatones, integración física, carga de recursos, renderizado Slate/Canvas y enlace de widgets, además de las herramientas de editor y verificación. Los tipos de datos y las clases base también se mantienen para conservar la compatibilidad de los recursos existentes. Esto no es un proyecto sin módulos C++.

Las reglas descritas en la tabla se ejecutan en los Blueprints. La presentación y la simulación todavía utilizan ese soporte nativo; no se han sustituido por grafos que solo oculten llamadas al mismo código.

## Verificación

Consulta `validacion_blueprints_y_pintura.json`. Se comprobaron límites del reloj y semáforos, distritos, variación por modelo, máscaras importadas, pausa y reanudación, calidad, pedidos, compras, guardado e interfaz. Las pruebas usan perfiles aislados y no alteran la partida personal.

## Lluvia ocasional

En `BP_BogotaCity` estas funciones tienen implementación con nodos:

- `NextWeatherState`: probabilidades de mantener, subir o bajar la intensidad.
- `AdvanceDynamicWeather`: inicialización, cuenta atrás, cambios automáticos, pausa por comando y retorno al ciclo desde la intensidad visible.
- `ChooseWeatherHold`: intervalo aleatorio entre decisiones, con rangos distintos para seco y lluvia.
- `WeatherStateForIntensity` y `WeatherIntensityForState`: conversión entre los cuatro estados y sus intensidades.
- `InitializeParkingPlan`: semilla y selección de cuatro espacios diferentes entre doce.
- `ParkingPoseFor`: separación al bordillo, orientación y elección entre calzada y andén.

Se retiraron de C++ el temporizador del clima, la selección aleatoria de espacios sobre el andén y las reglas de separación y giro. Las llamadas entre estas funciones despachan a los grafos del Blueprint. El código nativo conserva la búsqueda de espacios libres del mapa, generación de los modelos, rayos contra el terreno, apoyo de ruedas y actualización visual.

 `RainStartChance`, `DryWeatherHold` y `WetWeatherHold` se ajustan en Class Defaults > World > Weather. Consulta CLIMA_DINAMICO_Y_ESTACIONAMIENTO.md para ver las probabilidades.

Las gotas voxel, las consultas de techos y la actualización de iluminación usan el soporte de renderizado nativo. La lluvia entra y sale de forma gradual, reduce la luz directa y aumenta ligeramente la bruma. Las gotas no tienen colisión y no se muestran por debajo de la superficie superior detectada.

La auditoría de recorridos y clima está documentada en `QA_MAPA_CLIMA.md` y `validacion_mapa_clima.json`.

La migración del temporizador de clima y del plan de estacionamiento se verifica en `validacion_clima_estacionamiento_blueprints.json`: seis grafos con bytecode en BP_BogotaCity, 63 controles por ejecución con dos semillas y 1.200 posiciones evaluadas a través de Blueprint.

## Entrada de desarrollador y dirección

DeveloperKey en BPC_DeliveryGameplay interpreta las letras y decide la clave reconocida. DeveloperDriveInput en BP_DeliveryRider calcula aceleración y dirección con mouse y teclado. Sus implementaciones anteriores se retiraron de C++; las funciones nativas de aparición, acceso a vehículos y física siguen pendientes de migración. Validación: validacion_entrada_y_clima_blueprints.json.

## Animaciones de NPC y servicios

ABP_Cashier, ABP_Chef, ABP_TechClerk, ABP_Pharmacist, ABP_Florist, ABP_CustomerStudent, ABP_CustomerOffice y ABP_CustomerNeighbor heredan directamente de AnimInstance. BlueprintUpdateAnimation calcula el desplazamiento real del componente, descarta teletransportes y actualiza caminar y cadencia. Pasaron 16 comprobaciones en ejecución. BP_PoliceOfficer deriva de Character y BP_PolicePatrol de SkeletalMeshActor; no usan clases ni llamadas de juego C++ propias. Los modelos se editaron y exportaron en Blender. Más detalles en SERVICIOS_VOXEL_Y_ANIMACIONES.md.
