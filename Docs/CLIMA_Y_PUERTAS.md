# Puertas y niveles de clima

El Escarabajo tenía un cuerpo inferior de aproximadamente 1,15 m de ancho frente a una cabina y guardabarros más anchos. Las puertas se ensancharon de forma simétrica hasta aproximadamente 1,36–1,40 m, manteniendo una curvatura pequeña, los arcos de las ruedas, los cristales y el estilo voxel. Se reposicionaron las manijas y molduras sobre la superficie nueva. Se conserva el esqueleto y la variación de pintura existente.

La regla `BP_BogotaCity.NextWeatherState` usa probabilidades para mantener, aumentar o reducir la intensidad. Las transiciones automáticas siguen siendo graduales y pueden recorrer seco, llovizna, lluvia y tormenta en ambos sentidos.

La tormenta añade hasta 200 partículas cúbicas de granizo, junto con hasta 1.800 gotas en lluvia fuerte; la normal mantiene unas 420 y la leve unas 150. Cada columna consulta el techo o el suelo para ocultar la precipitación bajo una cubierta. El granizo cae más rápido y recibe más viento que la lluvia. No se acumula en el suelo.

Las tormentas producen un destello breve, seguido del sonido de trueno con un retraso de 0,8 a 2,5 segundos. Los siguientes relámpagos se separan de 14 a 28 segundos. El sonido se sintetizó para este proyecto y se importa como `S_Thunder`. Al quitar la tormenta se cancelan los destellos y truenos pendientes; un sonido ya iniciado termina normalmente.

Para probar: escribe ESOYAM y luego LLOVIZNA, LLUVIA o GRANIZO, con el celular cerrado. SOLEADO quita la precipitación y CICLO restaura el clima automático. Consulta COMANDOS_DESARROLLADOR.md.

## Verificación

Estado PASS: 40 comprobaciones de comandos, peatones y conducción, incluidos los niveles de clima, la generación de granizo, el destello y trueno retardado y la ocultación de las 200 columnas de granizo bajo una cubierta de prueba. La sesión renderizada produjo un relámpago y un trueno y se revisaron las capturas de los tres niveles. La política automática se sustituyó posteriormente por transiciones probabilísticas entre esas intensidades; la validación actual está en validacion_clima_dinamico_estacionamiento.json.

Resultados: validacion_clima_puertas.json. Capturas: [puertas](../Capturas/Escarabajo_Puertas.png), [lluvia leve](../Capturas/Lluvia_Leve.png), [normal](../Capturas/Lluvia_Normal.png), [granizo](../Capturas/Granizo.png) y [relámpago](../Capturas/Relampago.png).
