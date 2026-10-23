import json,re,shutil,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'outputs/Revision_Ciudad_Personajes_Trafico';out.mkdir(exist_ok=True)
crowd=json.loads((root/'work/city_repairs_validation.json').read_text());traffic=json.loads((root/'outputs/DeliveryArt/TrafficDetailed/traffic_validation.json').read_text());eyes=json.loads((root/'work/courier_eyes_validation.json').read_text());game=json.loads((root/'work/packaged_current_validation.json').read_text(encoding='utf-8-sig'))
assert all(x['status']=='PASS' for x in [crowd,traffic,eyes,game])
perf_path=root/'work/final_packaged_city_visual.log'
if not perf_path.exists():perf_path=root/'work/final_city_visual.log'
performance=re.search(r'CITY_RENDER_PERFORMANCE\s*(\{.*?\})',perf_path.read_text(encoding='utf-8')).group(1)
performance=json.loads(performance)
for source,name in [('HighresScreenshot00071.png','Ojos_Durante_Marcha.png'),('HighresScreenshot00072.png','Rostro_De_Frente.png'),('HighresScreenshot00074.png','Ciudad_Con_Peatones.png'),('HighresScreenshot00075.png','Faros_Nocturnos.png')]:shutil.copy2(root/'outputs/BogotaVoxel/Saved/Screenshots/WindowsEditor'/source,out/name)
for source,name in [('work/city_repairs_validation.json','Peatones.json'),('outputs/DeliveryArt/TrafficDetailed/traffic_validation.json','Trafico.json'),('work/courier_eyes_validation.json','Ojos.json'),('work/packaged_current_validation.json','Juego.json')]:shutil.copy2(root/source,out/name)
(out/'Rendimiento.json').write_text(json.dumps(performance,indent=2),encoding='utf-8')
sim=traffic['simulation'];checks=len(re.findall(r'DELIVERY_TEST [^\r\n]* PASS',(root/'work/packaged_current_validation.log').read_text(encoding='utf-8')))
text=f'''# Ciudad, personajes y tráfico — 14 de octubre de 2026

Cambios aplicados al proyecto de Unreal y a la versión jugable Current.

- Ojos de los 60 peatones y los ocho personajes de tiendas con las proporciones del protagonista. Capas finas de blanco, pupila y párpado; se mantiene despejado el flequillo.
- Cabezas cerradas junto a las orejas, sin franjas de textura estiradas. Cabello y cara siguen juntos el hueso de la cabeza; se conserva el volumen superior.
- 864 peatones repartidos por el mapa, frente a los 144 anteriores. Hasta 120 cercanos en calidad normal y 48 en rendimiento. Rutas en ambos sentidos y adelantamiento para evitar bloqueos.
- Carros compactos ampliados un 18%; el resto de carros, un 12%. Ruedas, luces, puertas y colisiones mantienen la misma escala.
- Faros de carros estacionados y en circulación con luz real sobre el pavimento y encendido nocturno.
- Tráfico con simulación a pasos regulares y posición interpolada en cada cuadro. Se conserva el tiempo durante una caída puntual de rendimiento. Carriles rectos compatibles pueden compartir el cruce; los giros siguen reservándolo hasta que despeje el vehículo.
- Las ofertas disponibles ya no se seleccionan automáticamente. Mantener E sin elegir una ruta no inicia un pedido. Cambiar de oferta, soltar la tecla o vencer la oferta cancela la aceptación en curso.

## Comprobaciones

- Ojos: 68 modelos, cuatro momentos de animación y vistas frontal e inferior; blanco y pupila visibles en ambos ojos.
- Volumen superior: 69 personajes revisados, incluido el protagonista.
- Peatones: diez minutos simulados, {crowd['crossings_completed']} cruces completados, {crowd['stalled_walkers']} bloqueos prolongados, ningún cruce ilegal ni solapamiento con vehículos durante los cruces.
- Tráfico: diez minutos simulados, {sim['vehicles']} vehículos, ningún solapamiento, espera máxima de {sim['longest_stop_seconds']:.2f} s. Movimiento en {sim['moving_render_frames']}/120 cuadros de prueba; los dos primeros corresponden a inicializar la interpolación. Pérdida de recorrido tras una pausa de 200 ms: {sim['hitch_time_loss_cm']:.2f} cm.
- Prueba visual a 1280×720: {performance['average_fps']:.2f} FPS de media; percentil 95 del tiempo de cuadro: {performance['p95_frame_ms']:.2f} ms.
- Versión empaquetada: PASS; {checks} comprobaciones correctas del flujo de pedidos, tiendas, vehículos y progreso.

Capturas: Ojos_Durante_Marcha.png, Rostro_De_Frente.png, Ciudad_Con_Peatones.png y Faros_Nocturnos.png. Los informes JSON guardan los resultados detallados.

Proyecto: outputs/BogotaVoxel/BogotaVoxel.uproject.
Juego: outputs/BogotaVoxel_Playable_Current/Windows/BogotaVoxel.exe.
'''
(out/'LEEME.md').write_text(text,encoding='utf-8')
print(out/'LEEME.md')
