# Interacciones animadas de vehículos

F y el botón izquierdo frontal del mando activan la entrada y salida animadas. No hace falta escribir un comando de puertas: el carro abre y cierra durante la interacción. La entrada de cicla y moto usa animaciones específicas adaptadas en Blender a los apoyos del modelo voxel. Pulsar F varias veces durante una transición no inicia otra.

Las fuentes son Mixamo Idle y Entering Car, retargeteadas al esqueleto existente. El gesto de montar cicla/moto y sus contactos se adaptaron en Blender; no se presenta como una captura original específica de ciclismo.

BP_TwoWheelerCitizen implementa en Blueprint conducir, buscar un espacio de aparcamiento, bajarse, caminar, volver y montar. El mismo NPC permanece visible, y su vehículo queda aparcado con colisión mientras camina. Hay tres bicicletas voxel editables en Blender y variaciones de motocicleta civiles y policiales.

Validado: doce comprobaciones del jugador y cuatro NPC con dos o más ciclos completos en escenario aislado. La prueba urbana de 120 segundos verificó a los doce NPC en circulación, sin errores de ejecución de Blueprint. Diez completaron un ciclo de aparcamiento y regreso; dos siguieron su recorrido sin completar aparcamiento durante la prueba. Se añadieron desvíos laterales seguros para ciclistas y cancelación de una maniobra de aparcamiento bloqueada tras doce segundos.

La migración global sigue pendiente: estos nuevos estados y tiempos están en Blueprint, pero la interacción del jugador todavía confirma el acceso al vehículo mediante el backend existente. Persisten bases nativas del proyecto; no es todavía un proyecto independiente de C++.
