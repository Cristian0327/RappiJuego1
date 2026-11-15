# Mecánica Robo

Estado al 11 de noviembre de 2026: rigs y clips exportados, vista previa programada y pendiente de compilar, importar y probar en Unreal. Este directorio pertenece a Bogotá Voxel y usa su proyecto activo, `../BogotaVoxel.uproject`.

## Propuesta de juego

- **Personaje de rayas, con frente amplia y barba.** Intenta quitarle al jugador parte del saldo. Si el jugador falla el QTE, pierde el 15 % del saldo actual, con un tope de 12.000 COP. El evento se omite si el saldo es inferior a 3.000 COP. El celular muestra el valor exacto que perdió.
- **Personaje Hornets, con gorra turquesa.** Retiene la cicla o moto que el jugador tiene equipada. Si el jugador falla, queda a pie y aparece un aviso en la app **Recuperar vehículo**. La app muestra cuál vehículo está retenido y el importe exacto. Precio inicial para calibrar: 50.000 COP para cicla y 80.000 COP para moto. El vehículo conserva su identidad y mejoras.
- **QTE para zafarse.** Mostrar tres indicaciones, de una en una, usando acciones reasignables con iconos para teclado y mando. Empezar con 1,25 s por paso y dar un margen de entrada al iniciar. Una pulsación sostenida no cuenta varias veces. Una tecla equivocada consume la tolerancia de un error y permite repetir el paso dentro de su ventana. Una segunda equivocación o agotar el tiempo falla el evento. Superarlo conserva saldo y vehículo. Pausar congela el temporizador. Incluir opción de tiempo ampliado.
- **Salida si el jugador queda sin plata.** Puede seguir a pie y usar el transporte público. El rescate siempre exige pagar. Al confirmar el pago se revela un punto de retiro en el mapa. El rescate pendiente aún es de sesión; falta persistirlo al recargar la partida.

## Frecuencia por visita

Una tirada por visita elegible al recoger o entregar. En la misma visita, bajarse, entrar, salir y volver a subir no generan sorteos adicionales. Cambiar de sector tampoco genera un sorteo. Los valores son iniciales para probar y representan la probabilidad de un intento, que todavía puede evitarse con el QTE.

| Sector | Mañana 06–12 h | Tarde 12–19 h | Noche 19–00 h | Madrugada 00–06 h |
| --- | ---: | ---: | ---: | ---: |
| Centro | 6 % | 9 % | 16 % | 22 % |
| Sur | 5 % | 8 % | 14 % | 19 % |
| Norte | 3 % | 5 % | 9 % | 12 % |

- Rayas puede aparecer durante el trayecto a pie entre el vehículo y la puerta, a la ida o al regreso. Hornets puede aparecer al estacionar o justo después de bajarse. Excluir el interior de la tienda, conducción en marcha, tutorial e interacciones activas.
- Si ambos son elegibles, repartir 60 % para Rayas y 40 % para Hornets dentro del intento. Si solo uno es elegible, usar ese. Si se pierde la oportunidad del personaje elegido, cancelar sin volver a sortear.
- Después de un intento, las próximas dos visitas elegibles quedan protegidas, incluso si cambia el sector. Guardar la protección restante. Una retención pendiente impide otro robo de vehículo.
- Sortear tres acciones reasignables por intento. Mostrar una a la vez con el icono del dispositivo activo y evitar repeticiones consecutivas. Mantener la tolerancia de un error y el tiempo ampliado.

## Rig y animaciones

Fuente: `SourceArt/PersonajesVoxel/Personajes_Bogota_Voxel.blend`. Blender 5.2.1 abrió el archivo y confirmó que las piezas de ambos personajes son mallas separadas y todavía no hay armaduras.

1. Preparar una copia de trabajo con ambos personajes centrados individualmente y en pose de referencia. Usar el esqueleto del jugador como referencia de proporciones y ejes. Probar una jerarquía humanoide común para ambos, asignar pesos rígidos a gorra, barba y adornos, y ajustar las articulaciones para conservar la silueta voxel. Preparar el puñal separado para un socket de mano de Hornets.
2. Comprobar primero la locomoción con `AN_Idle`, `AN_Walk_InPlace` y `AN_Run_Mixamo` de `Content/VoxelExplorer`. Evaluar compatibilidad con `SK_VoxelExplorer_Skeleton` e `IK_VoxelExplorer`. Si el rig requiere otro esqueleto, transferir los clips mediante retarget y revisar pies, hombros y manos.
3. Crear animaciones cortas propias para los momentos que dependen del jugador: aviso, reacción al QTE y salida. Rayas tiene un gesto breve y una retirada. Hornets tiene una pose con el accesorio y una salida diferenciada para cicla y moto. Probar si sus proporciones permiten reutilizar los clips de montaje de `VoxelExplorer`.
4. En Unreal, usar montajes coordinados para el NPC y el jugador. Mantener un loop corto mientras se espera la respuesta al QTE y pasar a la salida correspondiente al resolverlo. Alinear al NPC cerca del jugador o del vehículo según el caso. Verificar que se recuperen cámara y controles al terminar o cancelar.
5. Probar primero a Rayas en una visita de recogida, con éxito y fallo usando teclado y mando. Después probar a Hornets con ambos vehículos. Revisar deslizamiento de pies, separación entre cuerpos, manos en el manillar y transiciones.

## Conexión con el juego

1. **Confirmar las fuentes del estado.** El mapa activo es `/Game/Maps/Bogota_Juego_Final`. Se localizaron `BP_BlueprintRider` y `WBP_BlueprintPhone` en `Content/Delivery/BlueprintGameplay`. Identificar en Unreal qué Blueprint o componente posee el saldo, la hora del mundo, el vehículo activo y el guardado antes de crear enlaces. Reutilizar esas fuentes.
2. **Preparar los personajes.** El archivo editable es `SourceArt/PersonajesVoxel/Personajes_Bogota_Voxel.blend`. Preparar e importar ambas variantes siguiendo la sección de rig y animaciones.
3. **Controlar el encuentro.** Añadir un controlador de evento en el runtime existente. Flujo: disponible → aviso → QTE → resuelto → enfriamiento. Usar acciones propias solo mientras el QTE está activo y devolver el control habitual al salir por éxito, fallo, cambio de mapa o cierre. Un evento interrumpido antes de resolverse se cancela sin pérdida.
4. **Aplicar el resultado una vez.** Dar un ID al incidente y registrar de forma conjunta el descuento o la retención, su estado y el enfriamiento. Un guardado anterior se abre con valores iniciales y sin retención. Si falla un pago, conservar el vehículo retenido y el saldo previo. Si el pago se confirma, guardar el derecho a recogerlo antes de ubicar el vehículo. Pulsar dos veces o recargar debe dejar una sola devolución y un solo cobro.
5. **Conectar la app.** Añadir la sección al celular existente. Mostrar costo, saldo y marcador cuando esté disponible. Probar el circuito con cicla y moto por separado.

## Pruebas para darlo por listo

- Forzar cada variante en un perfil de prueba. Pasar y fallar el QTE con teclado y mando. Comprobar pausa, tiempo ampliado y salida del mapa.
- Verificar importe, límites de saldo y ausencia de doble descuento. Probar pago, saldo insuficiente, doble clic y recarga antes y después del pago.
- Confirmar que vuelve el mismo vehículo con sus mejoras, que no se duplica y que el pedido activo se puede continuar.
- Simular tiradas con semilla fija por franja, medir intentos por visita elegible, sector y franja y probar en la build durante recorridos normales de mañana, noche y madrugada.

## Prueba de desarrollador en Unreal

Estado del 11 de noviembre de 2026. Blender generó `SourceArt/PersonajesVoxel/Rigs` con dos fuentes editables y los FBX de mallas, caminata, carrera y gesto. La locomoción se tomó de los clips locales del proyecto. El puñal de la vista previa de Hornets está ligado a la mano derecha dentro de la malla. Opera GX estaba abierto, pero la ventana no respondió al control y no se descargaron clips nuevos.

El módulo `BogotaRuntime` incluye una vista previa para Play In Editor. Antes de usarla, compilar el módulo y ejecutar `importar_personajes.py` en Unreal Editor mediante **File → Execute Python Script**. El importador crea los recursos de ambos personajes en `/Game/Robbery`.

En Play, ubica al jugador a pie frente a un espacio abierto. Abre la consola con **F10**, escribe el comando, pulsa Enter y vuelve al juego.

| Comando | Resultado |
| --- | --- |
| `BogRobPreview Rayas` | Acercamiento, gesto, QTE y retirada del personaje de rayas. |
| `BogRobPreview Hornets` | El mismo circuito de prueba con el personaje Hornets y su accesorio. |
| `BogRobPreview Cancel` | Retira al personaje de prueba. |

El QTE de prueba acepta Q/E/R/F y los cuatro botones frontales del mando. Presenta tres indicaciones al azar sin repetición consecutiva y permite un error dentro de la ventana de 1,25 segundos por paso. Los comandos solo actúan en Play In Editor. Activar `BogDev 1` es opcional.

Verificación pendiente en Unreal. UnrealBuildTool recibió acceso denegado al directorio instalado `Engine/Source`, y el editor ejecutado en segundo plano terminó sin generar el registro ni los recursos importados. La vista previa no aplica descuentos ni retiene vehículos. Faltan conectar visitas, sectores, reloj, celular, guardado y las animaciones sincronizadas del jugador y de montaje de cicla o moto.

## Retomar desde otra cuenta

Abrir la carpeta local `BogotaVoxel_JuegoCompleto` en un proyecto nuevo de Codex desde la otra cuenta, o usar una copia completa de la carpeta si cambia el computador. Pegar en el nuevo chat:

> Lee AGENTS.md, CONTINUAR_BOGOTA_VOXEL.md y RappiJuego1/Mecanica Robo/README.md. Continúa Mecánica Robo sobre RappiJuego1/BogotaVoxel.uproject. Conserva los cambios locales. Confirma en el editor las fuentes de saldo, hora, vehículo y guardado antes de implementar y actualiza la guía al terminar.
