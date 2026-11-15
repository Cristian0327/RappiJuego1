# Créditos de audio de Bogotá Voxel

Las grabaciones externas se recortaron, filtraron y convirtieron a mono. Los motores se prepararon como bucles y la bocina como efecto breve. Las licencias se aplican a los audios correspondientes.

| Recurso en el juego | Grabación y autoría | Licencia |
| --- | --- | --- |
| `Police_Moto_Recorded` | [Police motorbike engine](https://commons.wikimedia.org/wiki/File:WWS_Policemotorbike8211engine.ogg), grabado por Dušan Oblak para Work With Sounds y Technical Museum of Slovenia | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| `Bus_Recorded` | [MAN SG 220 city bus engine](https://commons.wikimedia.org/wiki/File:WWS_CityBusMANSG220engine.ogg), grabado por Dušan Oblak para Work With Sounds y Technical Museum of Slovenia | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| `Car_Recorded` | [Car Engine Idling.wav](https://freesound.org/people/jpkweli/sounds/154758/), de jpkweli, fragmento distribuido en [ESC-50](https://github.com/karolpiczak/ESC-50/blob/master/audio/3-154758-A-44.wav) | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| `Horn_Recorded` | [Car Horn.wav](https://commons.wikimedia.org/wiki/File:Car_Horn.wav), de 15HPanska_Ruttner_Jan | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |

`Moto_Recorded` se preparó a partir de `Motorcycle motor loop.wav`, entregado por el usuario. Las voces, la música de menú y las capas de parque, noche y lluvia también proceden de sus archivos.

| Evento FMOD | Fuente |
| --- | --- |
| `City_Plaza` | `In case/Caotic Plase traffic and crowd.mp3`, del segundo 35 al 60 |
| `City_Neighborhood` | `In case/City and Crowd ambience Day.mp3`, del segundo 416 al 441 |
| `City_DistantTraffic` | `In case/Traffic Sound maybe.mp3`, del segundo 275 al 300 |
| `Wind_Bogota`, `Rain_Drizzle`, `Rain_Steady`, `Rain_Downpour`, `Thunder_Distant` | Síntesis original del proyecto |

Las tres tomas de `In case` fueron proporcionadas por el usuario. Se prepararon como fondos estéreo con filtro y fundido de bucle. Las conversaciones ambientales reutilizan las seis tomas de `NPC sounds`.

`Bike_Player` procede de `Bike Loop.wav`, entregado por el usuario. Se convirtió a mono, se ajustó su nivel y se empalmó el bucle. Las capas de rodadura, cadena, derrape, frenada, viento al avanzar, montaje, desmontaje, aterrizaje y las nuevas pisadas se sintetizaron para el proyecto.

Incluye este archivo de créditos al distribuir el juego o el proyecto de FMOD con estas grabaciones.

`WorldFoley` contiene 44 efectos y capas de síntesis propia. Sus fuentes editables se regeneran con `work/prepare_world_foley.py`. La nueva edición de `City_Plaza` usa el mismo fragmento de la toma del usuario con reducción suave de picos.

La megafonía de las once estaciones usa voz sintética de Microsoft Sabina Desktop, filtrada para imitar altavoz. Los archivos se generaron para esta build local. Se conserva la paleta original de NPC por separado.

## Grabaciones incorporadas el 10 de noviembre de 2026

Las tomas de Freesound se editaron a partir de sus previsualizaciones públicas de alta calidad. El trueno se editó desde el archivo Ogg de Wikimedia. Los cortes, fundidos y filtros están en `work/prepare_recorded_bogota_audio.py`.

| Recurso | Fuente | Licencia |
| --- | --- | --- |
| `Foot_Walk_1–5` | [Concrete walking, de ralph.whitehead](https://freesound.org/people/ralph.whitehead/sounds/565711/) | CC0 1.0 |
| `Foot_Run_1–5` | [Concrete running, de ralph.whitehead](https://freesound.org/people/ralph.whitehead/sounds/565708/) | CC0 1.0 |
| `Foot_Gravel_1–5` | [Gravel running, de ralph.whitehead](https://freesound.org/people/ralph.whitehead/sounds/565706/) | CC0 1.0 |
| `Foot_Stairs_1–5` | [Escaleras, de TylerAM](https://freesound.org/people/TylerAM/sounds/389659/) | CC0 1.0 |
| `Sprint_Wind` | [Viento grabado en bicicleta, de cognito perceptu](https://freesound.org/people/cognito%20perceptu/sounds/20108/) | CC0 1.0 |
| `Storm_Rain` | [Lluvia y ráfagas grabadas bajo un toldo, de sonicwars](https://freesound.org/people/sonicwars/sounds/213872/) | CC0 1.0 |
| `Traffic_Field` | [Traffic on a busy street, de tiggyduu](https://freesound.org/people/tiggyduu/sounds/804986/) | CC0 1.0 |
| `Park_Field` | [Morning Birdsong and Distant Dog Bark in the Park, de WhisperingEarth](https://freesound.org/people/WhisperingEarth/sounds/799143/) | CC0 1.0 |
| `S_Thunder` | [Rain and thunder, de Caesar](https://commons.wikimedia.org/wiki/File:Rain_and_thunder.ogg) | Dominio público |

Las tres capas urbanas de `In case` y el trueno sintético se conservan como material de FMOD archivado. La mezcla activa usa `Traffic_Field` para el fondo urbano, el trueno grabado de la presentación del clima y las voces de NPC del usuario para las conversaciones.

En la revisión de miniturbo se recuperaron los fondos `City_DistantTraffic` y `City_Plaza` de `In case`, con niveles según tráfico, cercanía al parque, hora y refugio. `Street_Bird_1–3` son cortes de la grabación de WhisperingEarth indicada en la tabla. `Drift_Charge` y `Drift_Turbo` son señales originales generadas con `work/prepare_bogota_miniturbo_audio.py`.

En la mezcla posterior se reactivó también `City_Neighborhood`. Los pájaros grabados se reservan para parques. El viento ambiental y las señales de carga y miniturbo quedaron fuera de la mezcla activa. La lluvia usa como base `Ambientes/Rain soft.mp3`, proporcionado por el usuario.

En la revisión de manubrios se retiraron de la mezcla `City_Plaza` y `City_Neighborhood` por las voces y tonos que podían percibirse como canciones. El fondo activo es `City_DistantTraffic`, editado a partir de `In case/Traffic Sound maybe.mp3` con reducción de tonos sostenidos. El proyecto de FMOD conserva las otras tomas para edición.

En la revisión posterior, `City_DistantTraffic` se recreó con los intervalos 7–32 s y 51–76 s de [Traffic on a busy street, de tiggyduu](https://freesound.org/people/tiggyduu/sounds/804986/), CC0 1.0. El script `work/rebuild_bogota_street_without_horns.py` mezcla ambos tramos, filtra tonos estrechos y empalma un bucle de 24 segundos. El recorte previo de `In case` se conservó en `work/City_DistantTraffic.pre_nohorn.wav`.

El aire de avance de la cicla se sintetizó para este proyecto con `work/prepare_bogota_bicycle_air.py` y quedó en el evento `Wind_Bogota` de FMOD. La grabación `Sprint_Wind` queda archivada. El evento nuevo utiliza ruido de banda ancha y entra al acelerar con Shift.

La versión vigente de `City_DistantTraffic` vuelve a la toma del usuario `In case/Traffic Sound maybe.mp3`, segundos 275–300. `work/restore_bogota_original_traffic.py` atenúa los tonos de bocina dentro de la propia grabación y empalma un bucle de 24 segundos.

El fondo activo pasó a `City_Neighborhood` a petición del usuario. La edición usa el tramo 416–441 s de `In case/City and Crowd ambience Day.mp3`, con recorte de graves y atenuación de tonos estrechos. Se regenera con `work/restore_bogota_original_traffic.py --crowd`. El evento de viento se conserva en el banco para edición.

`City_Neighborhood` se usa como fondo nocturno. De día se usa `City_DistantTraffic`, con fundido entre ambos según la hora del juego.
