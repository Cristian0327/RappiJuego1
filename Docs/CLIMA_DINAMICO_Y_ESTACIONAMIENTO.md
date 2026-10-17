# Clima dinámico y estacionamiento

El clima usa estados probabilísticos. Cada evaluación puede mantener la intensidad o pasar al estado inmediatamente anterior o siguiente. La intensidad visible converge gradualmente al nuevo objetivo; no se salta de seco a granizo ni de tormenta a seco.

| Estado actual | Baja | Sigue igual | Sube |
|---|---:|---:|---:|
| Seco | — | 70 % | 30 % a llovizna |
| Llovizna | 55 % a seco | 25 % | 20 % a lluvia |
| Lluvia | 55 % a llovizna | 25 % | 20 % a tormenta |
| Tormenta | 80 % a lluvia | 20 % | — |

En seco, las evaluaciones se separan aleatoriamente entre 120 y 240 segundos de juego. En los demás estados, entre 45 y 75 segundos. Estos tiempos no garantizan un cambio: puede repetirse el mismo estado durante varias evaluaciones. El 30 % representa la probabilidad de iniciar llovizna en una evaluación en seco, no un porcentaje fijo del tiempo jugado bajo lluvia.

Cada sesión usa una semilla nueva independiente de las partículas. Las pruebas pueden fijar la semilla para reproducir un resultado. Las decisiones se editan con nodos en BP_BogotaCity > NextWeatherState. AdvanceDynamicWeather controla el temporizador y los comandos; ChooseWeatherHold calcula las esperas. WeatherStateForIntensity y WeatherIntensityForState convierten entre estado e intensidad. RainStartChance controla la probabilidad inicial; DryWeatherHold y WetWeatherHold controlan los rangos de espera.

ESOYAM y los códigos de clima siguen disponibles. Mientras se fuerza un tipo de clima, se pausa la toma de decisiones automática. CICLO retoma el clima automático desde la intensidad que se está viendo, por lo que una tormenta forzada puede luego bajar a lluvia y llovizna de forma natural.

## Estacionamiento

De los doce carros inicialmente estacionados, cuatro se eligen al azar para quedar parcialmente sobre el andén, con las ruedas de un lado más altas. Los demás permanecen al borde de la calzada. Se varían ligeramente la separación al bordillo y el ángulo de estacionamiento. La postura se calcula contra el terreno real y se conserva al subir y bajar del carro.

Los espacios usados están fuera de los carriles de circulación y dejan libre el recorrido habitual de los peatones. Los puntos de acceso de los NPC se calculan según la orientación y la altura reales del carro. La selección varía entre sesiones; las pruebas usan ParkingSeed para reproducirla. InitializeParkingPlan y ParkingPoseFor implementan la selección, separación y orientación en Blueprint. El apoyo de las ruedas contra el terreno conserva su implementación nativa.

## Verificación vigente

El perfil BlueprintInputSunnyQA pasó 65 comprobaciones. Incluye la dirección por mouse hacia ambos lados, MORADO, puertas y acceso a vehículos, restauración del modo desarrollador y los cuatro estados meteorológicos. Esto no certifica que los nuevos sistemas pedidos de pasajeros visibles, taxis, policía, motos o direccionales estén implementados.

En 80.000 muestras de decisiones, la probabilidad observada de iniciar llovizna fue 29,945 %. El calendario Blueprint se ejecutó durante 10.080 minutos simulados: 8.027 secos, 1.417 de llovizna, 510 de lluvia y 126 de tormenta. Tiempo seco observado: 79,63 %. Es una muestra reproducible, no una garantía de ese porcentaje en cada partida.

La regresión anterior de recorridos está conservada en validacion_mapa_clima.json. La validación actual de entrada y clima está en validacion_entrada_y_clima_blueprints.json.
