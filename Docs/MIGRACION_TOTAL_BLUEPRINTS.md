# Migración completa a Blueprints

Estado: EN CURSO. El proyecto todavía depende de C++ propio y no se considera convertido.

## Completado

BP_DeliveryGameMode hereda directamente de /Script/Engine.GameModeBase. Su grafo ReceiveBeginPlay comprueba si existe BP_BogotaCity y lo crea si falta. El mapa y la configuración apuntan a este GameMode. El arranque tiene bytecode Blueprint y no llama a funciones propias de BogotaVoxel.

## Pendiente

- Personaje, cámara, bicicletas, motos y entrada de desarrollador.
- Tráfico, peatones, servicio de taxis, puertas y apoyo de ruedas.
- Ciclo de vida de la ciudad y presentación de los efectos de clima.
- Datos de pedidos, carga de recursos y guardado.
- Teléfono, mapa, HUD y vista previa del garaje.
- Entrada de animaciones, estructuras y enumeraciones.
- Herramientas de editor y retirada final de módulos y archivos C++.

Hay 7 Blueprints con una clase base propia de C++ pendiente de sustituir. El inventario está en estado_migracion_total_blueprints.json.

## Criterio de cierre

La migración se termina cuando el proyecto abre y funciona sin los módulos BogotaVoxel y BogotaVoxelEditor, sin referencias de recursos o configuración a esos módulos y con las pruebas funcionales aprobadas. Borrar Source o quitar Modules del .uproject antes de sustituir las clases no cumple este criterio.

La recuperación conserva la configuración, el mapa y el GameMode anteriores fuera de la carpeta del juego. No se han hecho cambios en GitHub.

## Prueba del primer cambio

El perfil aislado PureGameModeFinalQA pasó 63 comprobaciones después de sustituir el GameMode. El mapa arrancó con una sola ciudad y sin advertencias ni errores de compilación de Blueprint. Esto verifica la regresión de ese cambio; no certifica todavía la independencia de C++ del proyecto completo.

## Entrada y clima: 16 de octubre

DeveloperKey y DeveloperDriveInput pasaron a grafos Blueprint. MORADO aparece entre las claves y las letras dejan de interferir con los atajos de mapa/hora. Se verificó la dirección del mouse y se rebalanceó el clima. Pasaron 65 comprobaciones. La simulación, aparición de vehículos, presentación de pasajeros, interfaz y demás bases nativas siguen pendientes; no se han retirado los módulos C++. El servicio de taxi, los conductores de motos, el control de puertas y los indicadores siguen pendientes. El policía de la plaza y la patrulla estacionada ya cuentan con Blueprints propios de clases de Unreal.

## Modelos y animaciones de NPC

Se migraron ocho animaciones de comerciantes y clientes a AnimInstance de Unreal. Las 16 pruebas de caminar y detenerse pasaron en ejecución. El policía de la plaza patrulla y rodea al jugador mediante un Blueprint derivado de Character. La patrulla estacionada deriva de SkeletalMeshActor. Los seis modelos de servicios conservan sus archivos editables de Blender. La auditoría fresca compiló los 18 Blueprints de ejecución; todavía quedan siete con base nativa propia. Consulta SERVICIOS_VOXEL_Y_ANIMACIONES.md.
