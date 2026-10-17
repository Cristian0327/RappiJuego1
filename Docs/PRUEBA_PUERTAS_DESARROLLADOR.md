# Prueba de puertas en modo desarrollador

1. Inicia la partida, cierra el celular y escribe `ESOYAM`.
2. Acércate a un carro o TransMilenio detenido.
3. Escribe `PUERTAS` para abrir. Escríbelo de nuevo para cerrar.
4. `MORADO` hace aparecer el TransMilenio morado; después puedes acercarte y usar `PUERTAS`.
5. Si el vehículo se mueve, la prueba cierra las puertas y libera el vehículo. Para probar otro, vuelve a escribir `PUERTAS` cerca de él.
6. Escribe `ESOYAM` para salir del modo desarrollador.

El controlador escoge el vehículo con puertas más cercano, dentro de 16 metros. Sin vehículo cercano muestra un aviso. Fuera del modo desarrollador no se activa. No requiere consola.

La prueba anima las bisagras de los carros y las hojas deslizantes de TransMilenio a partir de su transformación de reposo. Conserva la escala y utiliza interpolación por fotograma. Las animaciones automáticas del tráfico recuperan el control al terminar la prueba. Esta función es una herramienta de inspección visual; no sustituye la lógica de embarque, los pasajeros sentados o el servicio de taxis, que continúan pendientes.

Blueprint: `/Game/Delivery/Developer/BP_DeveloperVehicleDoors`.
