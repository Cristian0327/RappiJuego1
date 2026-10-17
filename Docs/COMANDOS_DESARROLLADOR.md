# Códigos de desarrollador

Durante Play, con el celular cerrado y el juego enfocado, escribe las letras seguidas, sin abrir ningún cuadro ni pulsar Enter. Primero activa **ESOYAM**. No dejes más de tres segundos entre letras.

| Código escrito | Resultado |
|---|---|
| **ESOYAM** | Activa o desactiva el modo desarrollador. |
| **LLOVIZNA** | Lluvia leve. |
| **LLUVIA** | Lluvia normal. |
| **GRANIZO** | Lluvia fuerte con granizo, relámpagos y truenos. |
| **SOLEADO** | Quita la lluvia inmediatamente. |
| **CICLO** | Restaura el clima automático. |
| **MORADO** | Hace aparecer el TransMilenio morado en una vía libre cercana. |
| **CARRO** | Sube al carro cercano o baja si ya estás dentro. |

Para tomar un carro también puedes acercarte y pulsar F. LLUVIA, SOLEADO y CARRO requieren el modo desarrollador activo. CICLO permite restaurar el clima automático en cualquier momento.

## Consola alternativa

También se conservan los comandos anteriores. Durante Play, pulsa **F10**, escribe el comando y pulsa Enter. F10 vuelve a cerrar la consola. Se conservan también las teclas de consola anteriores.

| Comando | Resultado |
|---|---|
| `BogDev 1` | Activa el modo de pruebas existente: dinero y catálogo desbloqueados, acceso a lluvia y carros. |
| `BogDev 0` | Sale del modo de pruebas y restaura saldo y mejoras. El clima vuelve a automático. |
| `BogRain 2` | Lluvia leve. Requiere modo desarrollador. |
| `BogRain 1` | Lluvia normal. Requiere modo desarrollador. |
| `BogRain 3` | Tormenta con granizo y truenos. Requiere modo desarrollador. |
| `BogRain 0` | Desactiva lluvia inmediatamente. Requiere modo desarrollador. |
| `BogRain -1` | Devuelve el clima a su clima automático. |
| `BogCar` | Sube al carro cercano; si ya estás dentro, intenta bajar de forma segura. |
| `BogCar 12` | Ejemplo: toma el vehículo de circulación con índice 12. |

Los índices iniciales de circulación van de 0 a 99; incluyen particulares, taxis y buses. En modo desarrollador también puedes acercarte a un carro y pulsar **F**, incluidos los estacionados. Al tomar un estacionado se conserva su modelo y pintura.

## Conducción

- **W / S:** acelerar o retroceder.
- **Mouse:** apunta hacia la dirección en la que quieres conducir.
- **A / D:** dirección adicional.
- **Espacio:** frenar.
- **F:** bajar, si hay un espacio seguro.

Al bajar, el carro queda estacionado en su posición actual. El tráfico detecta su volumen incluso si queda atravesado. No vuelve automáticamente a su antigua ruta. Si las salidas están bloqueadas, el personaje permanece dentro y aparece un mensaje; mueve el carro a un lugar despejado.

Los carros conducidos comprueban paredes, otros vehículos y peatones antes de avanzar. Los pasajeros de un bus tomado en modo desarrollador vuelven a una plataforma válida; el resto de buses sigue prestando servicio.

El código de teclado anterior **ESOYAM** sigue alternando el mismo modo. Al salir mediante ese código también se restaura el clima automático.

Este modo de pruebas reinicia los pedidos activos al alternarlo, como ya hacía ESOYAM. El dinero y las mejoras de prueba no sustituyen el saldo y equipo normales restaurados al salir. Úsalo fuera de un reparto que quieras continuar.

**MORADO** requiere ESOYAM activo y estar fuera de un vehículo. Genera el modelo G66 morado, estacionado para que puedas acercarte y subir con F. Si repites la clave, recoloca el mismo bus; si no encuentra espacio seguro, muestra un aviso. No altera el horario de aparición natural del G66.

La clave anterior PURPURA se conserva como alias. El reconocimiento de letras se ejecuta en BPC_DeliveryGameplay > DeveloperKey; la entrada de dirección se calcula en BP_DeliveryRider > DeveloperDriveInput. Los sistemas de vehículo y aparición que reciben esas órdenes todavía tienen soporte nativo pendiente de migración. F2 abre el celular como atajo alternativo a TAB; F3 adelanta la hora. Las letras M y N ya no disparan esos atajos mientras se escribe una clave.
