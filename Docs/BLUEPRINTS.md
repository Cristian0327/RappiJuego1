# Blueprints del proyecto

El proyecto abre sin módulos propios de C++. Los padres de la lógica activa son clases y componentes de Unreal.

| Sistema | Carpeta / recurso principal |
|---|---|
| Modo de juego | `World/BlueprintWorld/BP_BlueprintGameMode` |
| Ciudad | `World/BlueprintWorld/BP_CityGeometry` |
| Hora, señales y clima | `World/BlueprintWorld/BP_WorldState`, `BP_WorldPresentation` |
| Peatones | `World/BlueprintWorld/Crowd` |
| Cruces entre manzanas | `BP_CrosswalkCitizen` |
| Carros, taxis y buses | `World/BlueprintWorld/Traffic` |
| Pasajeros de taxi | `BP_TaxiPassenger` |
| Jugador | `Delivery/BlueprintGameplay/Player/BP_BlueprintRider` |
| Conducción de carros | `Delivery/BlueprintGameplay/Player/BP_RoadInteraction` |
| Datos, pedidos y progreso | `Delivery/BlueprintGameplay/BPC_DeliveryDataCore` |
| Celular | `Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone` |
| Partida guardada | `Delivery/BlueprintSchema/BP_DeliveryProfile` |

Abre el Blueprint y sus funciones para cambiar su comportamiento. Compila y guarda antes de probar. Conserva las referencias a los materiales y esqueletos al modificar los modelos.

La caminata con bastón se mantiene en `Crowd/AN_CrowdCane`. Los taxis tienen puertas delanteras y traseras independientes. Los viajeros del TransMilenio conservan una representación visible al abordar, sentarse y bajar.

No vuelvas a importar los Blueprints retirados desde la recuperación: pertenecen a la versión anterior y dependen del módulo que ya no utiliza el juego.
