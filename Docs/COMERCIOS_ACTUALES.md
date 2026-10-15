# Comercios implementados

20 establecimientos distribuidos en el mapa, con 13 tipos de arquitectura Blender y sus interiores. Plantas de 24 × 24 a 24 × 32 metros, acceso continuo a nivel de calle y fachadas sin textos ni logotipos.

Tipos: mercado, frescos, parrilla, comidas rápidas, electrónica, componentes, droguería, floristería, panadería, café, ferretería mascotas y pizzería. Los cinco productos nuevos son taladro, lata de pintura, alimento, comedero y juguete para mascota.

Fuentes editables: `../DeliveryArt/Shops` y `../DeliveryArt/HighFidelity`. Referencias reales y limitaciones: `../DeliveryArt/Shops/REFERENCIAS_COMERCIOS.md`. Datos editables: `/Game/Delivery/Data/DT_StoreThemes`.

Los pedidos se recogen en comercios y se entregan en puertas de viviendas. El mercado repone ofertas al completar un pedido. La indicación interior cambia a salir por la puerta después de recoger.

La limpieza de esta revisión eliminó 124 archivos (79.4 MB): pruebas de rig descartadas, versiones anteriores de interiores, renders antiguos y respaldos `.blend1`. Se conservaron los personajes, vehículos, animaciones y modelos Blender vigentes. Registro: `../../work/cleanup_commercial_remake.json`.

Validación automatizada: `Saved/delivery_test.json`; incluye acceso y recogida en los 13 temas, presupuesto del cliente, entregas múltiples, vehículos y animaciones. La ausencia de solapes se comprueba contra las huellas físicas de los edificios existentes.

La migración total a Blueprints sigue pendiente: consultar `Blueprints_Estado.md`. El motor instalado y utilizado es Unreal Engine 5.8.2.

## Distribución y materiales actuales

Los mostradores de comida se sitúan ocho metros antes del fondo del local. Los demás mostradores están seis metros dentro. CounterDistanceMeters, en DT_StoreThemes, mantiene coordinados la caja, el empleado y la recogida de comida con la arquitectura Blender.

Los activos vigentes de fachadas e interiores terminan en `_Voxel`; se importaron con asignaciones de materiales limpias para evitar heredar las versiones antiguas. La farmacia pasó de 324 asignaciones a 13 materiales. Se retiraron cuatro árboles del mapa original que invadían parcelas comerciales; registro en `../../work/shop_tree_collision_cleanup.json`.

Se eliminaron además las 26 mallas Unreal anteriores de fachadas e interiores, después de comprobar que no tenían referencias. Los archivos Blender y FBX actuales se conservan. Registro: `../../work/superseded_store_assets_cleanup.json`.

La prueba de Windows empaquetado detectó postes originales dentro de parcelas y entradas. Se retiraron 16 postes con sus luminarias; registro `../../work/shop_lamp_collision_cleanup.json`. La prueba de acceso, estanterías y caja recorre ahora todas las sucursales de cada tema, en vez de elegir solamente la primera.
