# Animaciones, controles y cámara — 19 de octubre de 2026

Implementado en el proyecto del escritorio mediante Blueprints.

- Subida y bajada de cicla/moto en 0,68 segundos. Clips adaptados en Blender desde Mixamo, con desplazamiento lateral contado una sola vez y giro explícito de la malla.
- Carrera del protagonista: Mixamo «Unarmed Run Forward», retargeteada al esqueleto voxel. Recurso AN_Run_Mixamo, seleccionado por ABP_DeliveryRiderRun al correr. Caminata normal compartida con NPC y viejitos conservados.
- Al desmontar se restaura la orientación del cuerpo. La causa final era el formato de los valores de rotación: ahora Make Rotator conecta el giro directamente a los nodos, en lugar de depender de un literal que Unreal interpretaba como cero. Alineación medida del cuerpo: 0,996837 sobre 1.
- ESOYAM permite entrar con F a los autos de tráfico; no necesita escribir CARRO primero.
- MORADO utiliza el modelo SK_TransMilenioG66, incluyendo sus laterales morados. Los buses normales siguen rojos. Conserva la comprobación de espacio libre al aparecer.
- WASD dirige y mueve. El ratón permite mirar sin desviar el vehículo. A pie, el rumbo se mantiene mientras se sostiene la entrada de movimiento.
- Cámara con comprobación de obstáculos, esfera de 24 cm, inclinación de −55 a 15 grados y sin giro lateral. Los NPC visibles bloquean la cámara. Se oculta la malla del protagonista si la cámara queda demasiado cerca; los buses usan una distancia acorde a su longitud.

## Verificación

13/13 comprobaciones en el juego real: bicicleta inicial, caminata, montaje, pedaleo de jugador/NPC, sentido del pedal, bajada, alineación del cuerpo, carrera de Mixamo, límites de cámara, ESOYAM+F y conducción independiente del ratón. Sin errores «Accessed None» en la ejecución final.

Registro: work/RequestedFixesRuntime7.log. Prueba visual del G66 y aparición sin superposición: work/PurpleVisualRuntime3.log y work/PureIntegratedVisualQA/PURPLE_BUS00043.png.

Es una regresión centrada en estos cambios, no una prueba exhaustiva de cada obstáculo o vehículo. No se volvió a medir el rendimiento general. El arranque mostró advertencias de memoria durante la preparación de modelos.

Proyecto: RappiJuego1/BogotaVoxel.uproject. Mapa: /Game/Maps/Bogota_Blueprint_Integration. Sin cambios en GitHub ni C++ de ejecución añadido.
