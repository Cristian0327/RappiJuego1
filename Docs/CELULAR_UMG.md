# Celular editable en UMG

Abre `/Game/Delivery/UI/WBP_VoxelPhone` en Unreal.

El inicio contiene cinco aplicaciones: Mapa, Pedidos, Taller, Maletas y Garaje. No existe una aplicación independiente de entregas. Los pedidos aceptados se consultan dentro de Pedidos.

- Designer: carcasa, pantalla, tipografía Pixelify Sans, textos y aplicaciones. Conserva los nombres de los widgets al editar su apariencia: el código los utiliza para encontrar cada elemento.
- Graph → LauncherApps: cinco eventos OnClicked conectan las aplicaciones.
- Prefijos de las vistas guardadas: App1 mapa, App2 ofertas, App3 piezas, App4 vehículos, App5 pedidos aceptados y App6 maletas. Bike y Moto identifican variantes de la tienda.
- Atajos con el teléfono abierto: 1 Mapa, 2 Pedidos, 3 Taller, 4 Maletas y 5 Garaje.
- La capacidad y el dinero se leen del componente BPC_DeliveryGameplay del jugador.

La fuente importada tiene su archivo Font guardado además de FontFace. Sus fuentes y licencia están en `../DeliveryArt/UI/Fonts`.

La actualización de datos y parte de la navegación interna todavía utilizan soporte C++; la migración integral solicitada no está terminada. Consulta `Blueprints_Estado.md` para identificar las reglas que ya son nodos editables.

La última prueba de juego se guarda en `Saved/delivery_test.json`. Las capturas actuales están en `Saved/Screenshots`; las capturas de pruebas anteriores no demuestran que los cambios posteriores estén validados.

La navegación OpenHome/OpenMap/OpenOrders/OpenShop/OpenCatalog/OpenActiveOrders/OpenCargo, las acciones AcceptPressed/AcceptReleased/IgnorePressed, ClearPoint/ClosePressed y NextColor están implementadas como funciones Blueprint en WBP_VoxelPhone. BuildPage y RefreshText aún contienen soporte nativo de composición y actualización de datos.

GarageBike, GarageMoto, BuySelected, BuyModel, EquipModel, PaintSelected y SwitchPressed también son funciones Blueprint. Las compras comprueban que exista el componente del jugador y que el índice seleccionado corresponda a un artículo antes de ejecutar la operación. Los precios, requisitos, propiedad y cobros los valida BPC_DeliveryGameplay.

SelectEntry, SelectPrevious y SelectNext implementan en Blueprint la selección de ofertas, pedidos aceptados, piezas, maletas, modelos y colores. La navegación limita el índice al catálogo visible y comprueba que exista el componente antes de consultar los pedidos aceptados. La selección de un modelo recupera su color desde ModelColors.
