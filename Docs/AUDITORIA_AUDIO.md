# Auditoría de audio de Bogotá Voxel

10 de noviembre de 2026 · Mapa de inicio `/Game/Maps/Bogota_Juego_Final`

La revisión cruza los recursos del proyecto, las conexiones en Unreal y FMOD y los registros de ejecución. Un recurso presente en disco puede ser una versión anterior o una toma de respaldo. La revisión de conexiones indica qué tiene una ruta de reproducción. La prueba automatizada confirma eventos, mientras que el equilibrio y la identificación de un ruido concreto requieren escucha en la build.

## Revisión técnica de mezcla, cobertura y respuesta

### Qué se midió

- Se leyeron los 13 eventos del proyecto editable de FMOD y las rutas que los invocan desde `BogotaAudio.cpp`. Cinco eventos son espaciales. El máximo del espacializador es de 36 m para carro y pito, 44 m para las motos y 55 m para el bus. Los siete fondos continuos y el trueno son 2D.
- La salida registrada de Unreal es estéreo a 48 kHz, con 32 canales de reproducción. FMOD registra 48 kHz y se configura por separado. Que un clip aparezca en el registro confirma una activación, pero la captura final y un perfil de voces son necesarios para detectar enmascaramiento, saturación o canales descartados.
- Se midieron RMS y pico de muestras en las fuentes, antes de volumen en juego, distancia, oclusión y mezcla. RMS expresa nivel medio de señal. Los picos son picos de muestra. Estas cifras sirven para comparar la preparación de los archivos.
- Se revisó el registro de una sesión anterior de `Windows_Bogota_Derrape`. Contiene 78 arranques de motores FMOD, dos bocinas registradas por FMOD y seis inicios de conversación. Un mismo vehículo puede reaparecer en el registro al entrar otra vez en alcance. El registro de esa sesión carece de activaciones de trueno y no captura la señal audible final.

| Fuente medida | Duración | RMS dBFS | Pico dBFS | Lectura |
| --- | ---: | ---: | ---: | --- |
| Bike Loop original | 3,38 s | −41,2 | −17,4 | Promedio bajo y picos aislados. Explica por qué subir solo el volumen del componente tenía margen limitado. |
| Bike_Player | 3,26 s | −15,4 | −1,3 | La copia adaptada tiene más presencia. Con carga debe dejar hueco a pasos y señales al desmontar. |
| Car_Recorded / Bus_Recorded | 4,40 / 5,90 s | −17,7 / −17,7 | −4,3 / −4,5 | Nivel de origen parecido. La distancia y los multiplicadores hacen que el carro quede más atrás. |
| Horn_Recorded | 0,60 s | −15,8 | −1,3 | Transitorio alto. Conviene priorizar la bocina cercana y limitar coincidencias antes de seguir subiéndola. |
| Park ambience Day | 95,06 s | −30,6 | −6,1 | El promedio es bajo respecto a sus picos. Subir el fondo completo también sube los detalles más fuertes. |
| City_Plaza | 24,00 s | −27,8 | −2,2 | Gran diferencia entre promedio y pico. Revisar las crestas en la escucha, incluida la posibilidad de pitos residuales. |
| City_Neighborhood / City_DistantTraffic | 24,00 s | −20,9 / −20,9 | −5,7 / −4,3 | Las dos capas tienen el mismo RMS. La mezcla debe decidir cuándo domina cada una. |
| Step_Wet_0 / Ride_Land | 0,24 / 0,23 s | −19,4 / −18,1 | −0,9 / −0,9 | Ataques con poco margen. El aterrizaje se desconectó en la revisión anterior. Probar también pisadas fuertes junto a una bocina. |
| Voces NPC, seis tomas | 2,13 s cada una | −18,0 a −15,9 | −11,7 a −6,6 | El nivel de origen es consistente. La distancia, posición de la boca y oclusión son las siguientes variables que probar. |
| Boost ready | 2,00 s | −23,4 | −9,9 | Tiene margen para funcionar como aviso reconocible sobre la cicla. Separar su prioridad de la de otros efectos. |
| Thunder_Distant | 7,00 s | −34,6 | −17,4 | Fuente grave y con margen. Su diseño 2D impide ubicar la tormenta por dirección. |

### Hallazgos y correcciones que propondría

1. **Primero ordenar las prioridades de la mezcla.** Las carpetas de grupos, VCA y snapshots de FMOD están vacías. Las voces, pasos, interfaz y varias capas del jugador están en Unreal, y la mayoría de los niveles se resuelven mediante multiplicadores en código. Separaría tráfico cercano, tráfico de fondo, ambientes, clima, jugador, voces, interfaz y música. Durante una frase de cajero o cliente bajaría de forma breve el ambiente y los motores, con recuperación gradual. El ducking actual de tienda usa un temporizador aproximado para algunas capas urbanas.
2. **Proteger los eventos que informan.** Con 32 voces en Unreal, una avenida concurrida es el caso que merece perfilarse antes de agregar más emisores. Daría prioridad a pasos y señales propias, diálogo de entrega y pitos cercanos. Pondría límites distintos a murmullo, peatones y efectos repetitivos. No hay evidencia de que el límite de voces haya cortado el paso en una sesión concreta. Es un riesgo comprobable con un perfil de concurrencia.
3. **Calibrar por distancia y por perspectiva.** Un carro con RMS de −17,7 dBFS y ganancia base de 0,32 queda cerca de −27,6 dBFS de RMS antes de atenuación. La cicla al avanzar puede quedar bastante por encima porque se mezcla cerca del jugador. Ajustaría con pares de pruebas a 5, 15 y 30 m, con el vehículo pasando a izquierda y derecha. El objetivo es reconocer el motor cercano y su dirección mientras sigue clara la pisada, no lograr que toda la avenida suene al mismo nivel.
4. **Separar ambiente y emisor.** El parque actual entra a unos 42 m desde el punto etiquetado más próximo. El fondo de 95 s es estéreo común. Usaría una cama suave en el borde, un fondo propio al entrar y emisores de detalles separados por posición. Daría a cada parque un perfil de día, noche y lluvia. La distancia a una etiqueta no basta para distinguir estar al otro lado de un muro de estar dentro del parque.
5. **Unificar acústica y puertas.** Unreal aplica oclusión a sus voces y efectos espaciales. Los motores de FMOD tienen distancia propia, pero la ruta revisada no pasa los mismos valores de oclusión a FMOD. La build anterior sustituyó el submix de reverberación de Resonance al faltar el preset empaquetado. Comprobaría primero ese recurso y después probaría la misma voz y el mismo carro con puerta abierta, puerta cerrada, esquina y exterior. También mediría el paso entre calle e interior de bus.
6. **Vigilar repetición y continuidad.** Los motores de FMOD arrancan un evento nuevo al entrar en rango. Los bucles urbanos y de clima duran 24 s. La primera lluvia tiene un fondo de Unreal como respaldo que queda a nivel reducido cuando FMOD está activo. Alternaría puntos de inicio o variantes compatibles y comprobaría los bordes de alcance caminando, en cicla y al cambiar de cámara. Antes de agregar más fondos, quitaría los que se solapen en función.
7. **Acotar el golpe.** Los clips breves de aterrizaje y frenada tienen picos cercanos a escala completa en la fuente. La bocina y el fondo de plaza también tienen crestas importantes. La sesión revisada no registró trueno. Para identificar el ruido haría una reproducción repetible con trazas de cada evento y captura de salida. Después silenciaría por turno jugador, tráfico y ambientes. El aterrizaje ya está desconectado; los demás quedan como hipótesis.

### Sonidos nuevos que añadiría después del inventario anterior

| Prioridad | Sonido y función | Cuándo y dónde | Condición de aceptación |
| --- | --- | --- | --- |
| Alta | **Contacto de rueda con juntas, tapas y adoquín**. Da lectura de velocidad y superficie sin depender del motor. | Impulsos cortos solo cuando la rueda atraviesa la junta. Variantes para cicla, moto y bus. | Al atravesar la misma junta en vehículos distintos, cambia el peso. Una pasada lenta produce menos nivel. |
| Alta | **Cruce peatonal y semáforo accesible**, en lugares que tengan esa señal. | Desde el poste correcto y sincronizado con la fase del cruce. | Se puede ubicar el cruce con audífonos y la señal se detiene con la fase correspondiente. |
| Alta | **Cambio de perspectiva dentro de TransMilenio o taxi**. Añade vibración del habitáculo, rodadura amortiguada y un tono breve de apertura. | Al subir, cerrar puertas, cruzar una junta o girar. Desde fuera se conserva el sonido exterior del vehículo. | Una misma parada se distingue desde la plataforma y desde el asiento por timbre, dirección y nivel. |
| Alta | **Interacción de manos y equipaje**. Cremallera, cierre de maleta, roce de chaqueta y apoyo de paquete. | En el fotograma de contacto al guardar, sacar o entregar. Variantes por peso o material. | El sonido cae sobre el gesto y permite distinguir abrir, guardar y soltar sin mirar el aviso. |
| Media | **Vendedores y locales a distancia**. Añade actividad reconocible sin crear diálogo ajeno al elenco. | Desde una fachada abierta o un punto de reunión. Cerca se alternan voces originales. Detrás de un muro queda un fondo amortiguado. | Se distingue un emisor local de la multitud general y se entiende al cliente durante una entrega. |
| Media | **Fauna y detalles de parque por hora**. Aves aisladas, alas, hojas cercanas y un ambiente nocturno propio. | Aves de día en árboles y sonidos nocturnos discretos donde corresponda. Gotas desde ramas en lluvia. | La aproximación al parque cambia en tres distancias. Los detalles aparecen de forma irregular y se pueden localizar. |
| Media | **Aleros, canaletas y desagües**. Da referencias espaciales durante lluvia. | Gotas periódicas desde puntos visibles, agua más fuerte al pasar cerca de un desagüe y una transición cuando el jugador se refugia. | Entrar bajo techo reduce y oscurece el fondo de lluvia. Las gotas cercanas siguen teniendo posición. |
| Media | **Microambientes de infraestructura**. Zumbido de ventilación, cierre metálico de local, escalera resonante y vibración bajo un puente. | Emisores discretos en geometría que los justifique, con perfiles de distancia propios. | El lugar cambia de carácter al pasar cerca y el efecto se pierde al alejarse o rodear el obstáculo. |
| Media | **Identidad de oficios por tienda**. Papel de panadería, cartón de farmacia, hojas y cubetas de floristería, cajas de tecnología. | Al tomar el producto, pasarlo por caja o guardar el pedido. | Dos tiendas son distinguibles por detalles de interacción sin subir la música ni tapar la voz. |
| Baja | **Respuesta al esfuerzo continuo**. Respiración, ropa y tensión de cadena según pendiente, cadencia y estamina. | En subida y tras un tramo sostenido, con una recuperación progresiva. | Se percibe la diferencia entre costear, pedalear en plano y subir con esfuerzo. El aviso de Shift queda reconocible. |

### Recorrido de aceptación

1. **Avenida → parque → avenida.** Repetir ida y vuelta de día y noche. Registrar cuándo entra el fondo, cuándo se distinguen las fuentes puntuales y si el tráfico sigue bien posicionado. En estéreo, probar con auriculares y con parlantes.
2. **Calle → tienda → entrega.** Caminar y correr, abrir la puerta, hablar con cajero, recoger producto y entregar. Revisar que la voz y la primera pisada se distingan aunque haya un motor y una bocina cerca.
3. **Cicla y moto.** Rodar, soltar pedal, activar Shift y sostener Ctrl mientras ya se está avanzando. Comparar sonido de rodadura, derrape y lluvia. Al soltar Ctrl debe volver la tracción normal.
4. **TransMilenio y aguacero.** Escuchar la misma parada desde fuera y dentro, y cruzar a un alero. Medir picos de salida y voces activas en el tramo más cargado.

## Inventario

| Carpeta de Unreal | Recursos | Cobertura |
| --- | ---: | --- |
| Ambience | 4 | Parque, noche, lluvia suave original y fondo diurno de respaldo |
| Delivery | 4 | Aceptación, rechazo y finalización de pedido, más cierre de misión |
| Gameplay | 7 | Música, confirmación, error, recogida, señal de impulso y bucles originales de los dos vehículos |
| NPC | 12 | Seis tomas originales y sus seis copias mono para reproducción espacial |
| Rider | 26 | Bucle de cicla adaptado, capas de conducción y 15 pisadas por superficie |
| Traffic | 15 | Moto, moto policial, carro, bus, bocinas, puertas, descarga de aire y variantes previas |

El banco de FMOD contiene 13 eventos. Hay cuatro motores y una bocina de carro, tres fondos urbanos, viento, tres intensidades de lluvia y trueno distante. Los demás sonidos del juego se mezclan en Unreal.

La prueba en el mapa principal encontró 93 puntos etiquetados para parques. Varios puntos pueden pertenecer al mismo parque. La nueva mezcla empieza a introducir el fondo a unos 42 metros del punto más próximo y alcanza su nivel máximo cerca de 11,5 metros. Al alejarse vuelve a predominar el fondo urbano. El parque se reproduce como un fondo estéreo común. Queda por colocar fuentes individuales de aves y gente.

## Cobertura y sonidos que faltan

| Lugar o acción | Ya conectado | Qué añadir y cuándo debe sonar |
| --- | --- | --- |
| Parque | Fondo original con entrada y salida gradual por distancia a puntos del mapa. Por la noche se reduce el nivel. | Poner fuentes separadas para hojas, aves diurnas y charla distante. El fondo empieza en el borde y cada detalle se ubica donde tiene sentido. Si hay un juego infantil o una fuente visible, añadirle su propio audio. Evitar trinos fijos en bucle. |
| Sendero y ladera de Monserrate | Viento según exposición y altura. Pisadas de sendero donde se identifica la malla. | Viento por orientación y ráfagas, hojas y tierra suelta. Variar la presencia de la ciudad al ganar altura. En escaleras y pendientes, usar pisadas y respiración según esfuerzo. |
| Avenida y cruces | Motores espaciales de carros, taxis, motos y bus, bocinas por frenada de tráfico y capas de fondo urbano. | Separar ralentí, aceleración y paso de neumáticos. Añadir rodadura mojada, frenos suaves, direccionales y puertas de taxi. Una bocina corta cuando un carro reacciona y otra más larga para un bloqueo persistente. |
| Barrio, plaza y noche | Fondos urbanos ajustados por densidad, viento y base nocturna. | Dar una identidad propia a cada zona. Barrio tranquilo con voces lejanas y actividad espaciada, plaza con murmullo más amplio, noche con menos tráfico y fuentes intermitentes. Añadir campanas únicamente donde haya una fuente que las justifique. |
| Parada y TransMilenio | Motor, bocina, freno de aire y apertura y cierre de puertas. | Ambiente separado de plataforma e interior, aviso previo al cierre, señal de parada, pasos de subida y bajada, murmullo interior y timbre diferente cuando se oye el motor desde dentro. |
| Tiendas | Voz de atención, charla cercana, pasos de interior, recogida y reducción del ambiente de calle. | Puerta o campanilla al entrar, nevera o ventilación donde corresponda, bolsas, escáner y caja al pagar. Variar entre tienda de comida, mercado y local de tecnología. Mantener clara la voz al atender. |
| NPC | Conversaciones de dos personajes con las seis tomas originales, saludos y reacciones de entrega. | Grupos estables en esquinas, parques y estaciones. Darles pausas y turnos más largos y variar la distancia. Usar más tomas del mismo estilo si se amplía el elenco. Añadir ropa y pisadas específicas para personajes visibles cercanos. |
| Cicla y moto | Rodadura, cadena, rueda libre, viento, frenada, derrape, montaje y desmontaje. Motor espacial para moto y señal de sprint de cicla. | Separar pedaleo con carga y rueda libre con cadencia. Añadir traqueteo en adoquín, neumático húmedo, salpicadura y respiración en rampas. Recuperar el aterrizaje con un sonido amortiguado que dependa de la fuerza del impacto. |
| Caminar y correr | Variantes de pavimento, asfalto, sendero, interior y mojado. | Escaleras, metal, madera, césped y charcos dedicados. Usar contacto de animación en acciones precisas y distinguir caminata, carrera, salto y aterrizaje. Revisar que el primer paso se oiga al empezar a moverse. |
| Lluvia y techo | Llovizna, lluvia sostenida, aguacero, trueno, reducción de nivel bajo techo y pasos mojados. | Goteras en aleros y entradas, lluvia de techo, gotas en hojas y charcos, salpicaduras de ruedas y transición bajo techo con filtro además de volumen. Hacer que el trueno siga a una tormenta y no tape avisos. |
| Entregas, teléfono e interfaz | Notificaciones de pedidos, recogida, confirmación/error y música de menú. | Tacto del teléfono y vibración discreta, navegación del menú, selección de producto por material, timbre o golpe en puerta, cierre de bolsa y señales diferenciadas para pago, devolución y cancelación. |

## Orden de trabajo propuesto

1. Calibrar en una avenida concurrida con audífonos. La bocina debe ubicarse por dirección, los motores deben ser reconocibles y la pisada debe seguir presente. Verificar un cliente hablando junto a la calle y un grupo de NPC al cruzar la puerta de una tienda.
2. Autorizar y preparar ambientes propios de parque, tienda y estación. Colocar fuentes en el mapa y separar exterior e interior. Probar cada zona al acercarse, entrar y alejarse tanto de día como de noche.
3. Completar superficies e interacciones de alto uso. Priorizar pavimento mojado, escaleras, puertas, bolsas, escáner, respiración y ruedas bajo lluvia. Registrar procedencia y licencia de cada audio externo.
4. Organizar niveles y prioridades por tráfico, voces, clima, ambiente, jugador, interfaz y música. Medir picos con varias fuentes simultáneas y comprobar que las voces importantes bajen el ruido secundario sin cortes bruscos.

El registro de la build anterior muestra que Resonance Audio creó una reverberación provisional al faltar su preset y submix en el paquete. Los recursos correspondientes existen en la instalación del motor. Revisar su inclusión en el próximo empaquetado y comprobar la reverberación en tienda y calle. Este aviso por sí solo no identifica la causa del volumen bajo.

## Golpe parecido a un disparo

La revisión de nombres y referencias de audio no encontró un disparo conectado como evento. Se retiró el impacto corto de aterrizaje del jugador y se suavizó el ataque de montaje, frenada y salida de derrape. Son candidatos, no una identificación auditiva del ruido reportado. Se conserva el trueno de tormenta. Si el golpe continúa, la siguiente comprobación es registrar lugar, acción y clima y aislar esas capas durante la misma secuencia.

## Preflight final antes de ampliar la cobertura

- El derrape se verificó con Ctrl en ambos vehículos, pero el estado público y el bucle de audio se consultaban en momentos distintos. El audio podía seguir durante el fundido genérico después de soltar la tecla. La revisión final debe comprobar la tecla directamente para el estado audible y cancelar el bucle con un fundido breve. Mantener Ctrl con el vehículo detenido conserva la posibilidad de derrapar cuando vuelve a rodar.
- Los fondos urbanos se solapan con los motores. Las bocinas y las crestas de City_Plaza conservan transitorios altos. Separar nivel, alcance y prioridad. Revisar la ganancia de pico de la señal urbana y dar continuidad a una fuente cercana sin multiplicar emisores.
- La clasificación de pasos depende de la malla de contacto. En particular, un suelo de parque cuyo nombre contiene ParkSoil no estaba clasificado como césped. Los sonidos de metal, madera y escaleras requieren un contacto que permita reconocer su superficie.
- Las puertas de taxi y bus tienen estado utilizable. El giro real de vehículos, la lluvia, el estado de tienda, el teléfono y el vehículo de calle ofrecen condiciones para agregar sonidos. No se confirmó una propiedad que identifique un semáforo accesible, un parque infantil, una fuente, una junta de calzada o un desagüe concreto. Esas fuentes necesitan marcas verificadas en el mapa para situarlas.
- Los errores de reverberación del paquete y las advertencias de puerto de FMOD deben verificarse por separado. El perfil de escucha necesita una salida capturada para distinguir saturación, enmascaramiento y el golpe reportado. Los registros de activación por sí solos no dan ese resultado.

## Implementación posterior a la auditoría

| Área | Entregado en esta build | Cobertura pendiente |
| --- | --- | --- |
| Controles | Derrape por Ctrl mantenido, con audio que sale en 55 ms tras detectar que terminó. Ctrl puede seguir presionado si la velocidad cae y vuelve a subir. | Medir sensación con distintas velocidades y dispositivos. |
| Parque y exterior | Fondo estéreo al acercarse, cama nocturna y emisores de hojas, aves o gotas desde el ancla más cercana. Las voces originales siguen disponibles en los NPC. | Colocar árboles, grupos y equipamiento de cada parque como fuentes independientes donde proceda. |
| Tráfico y cabina | Rodadura seca/mojada cerca de vehículos, frenada, clic de giro del vehículo controlado, puertas de taxi y perspectiva de habitáculo. | Dirigir el clic a un estado explícito de direccional, añadir rodadura ligada a juntas reales y distinguir acústica interior entre taxi y bus. |
| Bus y estación | Fondo de plataforma, entrada a cabina, aviso ligado a TransitClosing y señal de parada. Se conserva el motor, el freno de aire y el efecto de puertas. | Avisos de voz por estación y contacto exacto de cada escalón de subida. |
| Tienda y teléfono | Entrada y salida, ventilación o nevera, sonidos por material de producto, escáner, pago, cremallera, toque de entrega, abrir/cerrar y selección/cancelación en teléfono. | Sincronizar con animación de manos, diferenciar otros estados de la interfaz y localizar los equipos individuales. |
| Jugador y clima | Cinco superficies adicionales, tela, esfuerzo, lluvia bajo techo con filtro, ruedas mojadas, salpicaduras y aterrizaje de ataque suave condicionado a caída real. | Asignar superficies por material físico en toda la ciudad, en lugar de inferirlas por nombre de malla. Ubicar charcos y juntas concretas para sincronizar la rueda con el contacto. |
| Mezcla | Buses Traffic, Horns, City y Weather en FMOD. Reducción de fondo y motores mientras se oye una interacción importante. Limitación suave del fondo City_Plaza y ajustes para evitar disparos de puertas cuando una fuente vuelve a entrar en rango. Se solicitó incluir los recursos de Resonance en el paquete. | Perfil de voces y captura estéreo de salida. Medir picos, audibilidad y oclusión por posición; extender el control por categorías a los sonidos que aún usan Unreal. |
| Fuentes de infraestructura | Recursos y conexión por etiquetas para desagüe, campana, persiana y cruce accesible. El cruce exige la fase peatonal y la persiana exige movimiento. | Colocar las etiquetas y vincular el estado del actor donde haya una fuente real. No se confirmó un emplazamiento adecuado en el mapa actual. |

Se generaron 44 SoundWaves originales en WorldFoley. Se verificaron las 44 fuentes mono a 24 kHz. Su pico mayor es de −4,7 dBFS antes de mezclarlas. El pico de City_Plaza bajó de −2,2 a −9,3 dBFS. La validación automatizada comprueba carga, transiciones y disparos instrumentados. La verificación auditiva en el dispositivo y la identificación exacta del ruido parecido a disparo quedan abiertas. El recorte de picos de plaza y el aterrizaje suave reducen dos candidatos.

## Cierre de cobertura y verificación

Se inspeccionaron los actores del mapa principal en Unreal. El inventario de ejecución encontró 11 estaciones de TransMilenio con ID, 297 semáforos peatonales y vehiculares y el santuario de Monserrate. Los puntos de parque ya verificados siguen siendo la base para hojas, aves y gotas. [Inspección de actores](../../work/BogotaAudioMapProbe.log).

- Cada estación tiene su aviso numerado grabado con una voz sintética de megafonía. Se activa desde la estación al abrir la plataforma y se limita a una vez por apertura. Las voces de NPC siguen siendo las seis tomas del usuario.
- Los semáforos cercanos usan la misma ventana peatonal que usa el código de cruce. El sonido sale del poste más cercano al peatón y tiene intervalo entre señales. El santuario sirve como origen de la campana diurna y las estaciones como origen del escurrimiento de lluvia. El cierre metálico de comercio se vincula al umbral de locales de ferretería y tecnología. Las etiquetas permiten añadir emisores individuales con sus propios estados donde la escena los tenga.
- Las pisadas consultan el pie más bajo en el instante de la pisada y trazan el contacto para obtener la malla y el material físico cuando existen. Las ruedas detectan cambios en la superficie de apoyo. El sonido de subida al vehículo añade contacto metálico y la cabina de bus se mezcla con un filtro más grave que la de un automóvil.
- Los motores de FMOD atenúan obstáculos usando una prueba de visibilidad con consultas escalonadas. La ganancia del motor cambia gradualmente. Pisadas del jugador, impulso y voces importantes tienen prioridad sobre efectos secundarios de Unreal. La megafonía reduce temporalmente el fondo y el tráfico.
- Se confirmó que el material físico puede faltar en algunas mallas. En ese caso se usa el nombre de la malla y después el pavimento como respaldo. La cadencia de los pasos sigue usando distancia recorrida y el pie se muestrea al emitir el sonido. Las juntas se aproximan por cambios de contacto; una junta pintada o incluida en una malla continua necesita una marca de superficie para detectarse por separado. El golpe histórico parecido a disparo no tiene una reproducción identificada.

## Revisión de grabaciones y ambientes del 10 de noviembre de 2026

Se importaron 20 variaciones de pisadas grabadas. El concreto usa tomas distintas al caminar y correr. El sendero y el césped identificado usan grava como respaldo y las escaleras tienen una grabación propia. La cadencia depende de la velocidad real. El charco conserva un detalle breve mezclado a nivel bajo.

La mezcla deja de reproducir los fondos con voces de `In case` y el silbido de pájaro sintetizado. Las conversaciones conservan las seis voces de NPC. El tráfico distante se obtiene de pasos de autos grabados y el parque mezcla aves según proximidad, hora y lluvia. El viento del sprint de cicla sube con la velocidad y se funde al soltar el impulso.

La llovizna, lluvia sostenida y tormenta tienen capas con niveles dependientes de intensidad y refugio. El trueno se emite desde la presentación del clima después del relámpago. La bocina automática usa tiempo detenido en cola, orientación y distancia al vehículo que precede, con pausas globales y por emisor.

Los recortes externos se detallan en [Créditos de audio](CREDITOS_AUDIO.md). Los comandos de prueba están en [Códigos de desarrollador](COMANDOS_DESARROLLADOR.md).

### Captura de salida del juego

Se capturó únicamente el proceso de Unreal que ejecutó la ruta de prueba, mediante el ejemplo de captura por proceso de Microsoft. La toma es estéreo a 44,1 kHz y dura 71,97 s, con 48,2 s activos por encima de −60 dBFS. Incluye el recorrido controlado de cicla, moto, pasos, tienda, parque, teléfono y estación. El pico de muestra fue −10,53 dBFS. El pico verdadero estimado por sobremuestreo fue −10,46 dBTP y el RMS mediano de ventanas activas fue −25,2 dBFS. Se contaron cero muestras a escala completa. La parte silenciosa incluye el fin de la ejecución automatizada.

La grabación cubre una ruta y un dispositivo. La prueba confirmó el inicio y la liberación de ambos derrapes y el aviso de la estación 11 al abrir su plataforma. El valor de pico demuestra margen en esta toma, mientras que la percepción con otros auriculares y el caso original del golpe siguen sujetos a reproducción.

[Mediciones](../../work/BogotaAudioCompleteMeasurement.json) · [Captura estéreo](../../work/BogotaAudioCompleteCapture.wav) · [Registro de la ruta](../../work/BogotaAudioCompleteQA.log) · [Ejemplo de captura de Microsoft](https://learn.microsoft.com/en-us/samples/microsoft/windows-classic-samples/applicationloopbackaudio-sample/)

La prueba focalizada registró tres señales desde el poste cercano al entrar en la ventana peatonal del ciclo. [Registro del cruce](../../work/BogotaPedestrianSignalQA.log). La build empaquetada abrió el mapa principal y activó los ambientes de FMOD sin errores de inicialización de Resonance. [Empaquetado](../../work/BogotaAudioCompletePackage.log) · [Arranque](../../work/BogotaAudioCompletePlayable.log).
