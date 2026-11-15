from pathlib import Path
import json,re,shutil
root=Path.cwd();out=root/'outputs/Revision_Cielo_Transito';r=json.loads((out/'validacion.json').read_text());pack=json.loads((root/'work/packaged_current_validation.json').read_text(encoding='utf-8-sig'))
assert r['status']=='PASS' and pack['status']=='PASS'
log=(root/'work/packaged_current_validation.log').read_text(encoding='utf-8',errors='replace');checks=len(re.findall(r'DELIVERY_TEST [^\r\n]* PASS',log));pack['passed_checks']=checks
(out/'prueba_juego_empaquetado.json').write_text(json.dumps(pack,indent=2),encoding='utf-8')
text=f'''# Cielo, peatones y tráfico

Actualizado el proyecto de Unreal y el juego BogotaVoxel_Playable_Current.

- Cielo con degradado de horizonte a cenit, nubes voxel en movimiento, sol, luna y estrellas. Transiciones continuas entre amanecer, día, atardecer y noche. Ciclo de 24 minutos: 16 de día y 8 de noche.
- Los peatones esquivan al jugador quieto y adelantan a personas lentas conservando su velocidad propia. También rodean al jugador si ocupa una esquina o la llegada de un cruce.
- 44 rutas de cruce conectan cuadras largas y dos intersecciones diferentes. Se eliminó el regreso inmediato por la misma calle.
- 100 vehículos en circulación, frente a 38: 96 carros y 4 buses. Se distribuyen por seis recorridos de tráfico privado y el corredor de buses, con separación al aparecer y seguimiento entre rutas compartidas.

## Comprobaciones

- Evasión: 6/6 pasan al jugador quieto, 6/6 adelantan al anciano y 6/6 rodean la esquina ocupada. Distancia mínima al jugador: {r['local_avoidance']['minimum_player_clearance_cm']:.1f} cm.
- Simulación de diez minutos con 864 peatones: 0 bloqueos prolongados, 127 cruces completados, 0 cruces ilegales y 0 solapamientos con vehículos en los cruces.
- Diez minutos de tráfico: 100 vehículos, 0 solapamientos y todos recorren al menos {r['traffic']['minimum_travel_cm']/100:.0f} metros. Movimiento conservado entre cuadros y tras una pausa de 200 ms.
- Juego empaquetado: PASS, {checks} comprobaciones aprobadas y ninguna fallida.
- Cuatro capturas verificadas: Amanecer.png, Mediodia.png, Atardecer.png y Noche.png. Sin errores de compilación del material del cielo.

Juego: ../BogotaVoxel_Playable_Current/Windows/BogotaVoxel.exe

Proyecto: ../BogotaVoxel/BogotaVoxel.uproject

Los resultados detallados están en validacion.json y prueba_juego_empaquetado.json.
'''
(out/'LEEME.md').write_text(text,encoding='utf-8')
mem=root/'memory';mem.mkdir(exist_ok=True)
(mem/'2026-10-14-cielo-peatones-trafico.md').write_text(f'''# DEBUG REPORT — Cielo y movilidad urbana

Status: DONE

## Síntoma
Cielo gris; filas detrás de ancianos o del jugador; cruces de ida y vuelta repetidos; poco tráfico visible.

## Causas
M_Sky emitía exclusivamente Horizon; Zenith no participaba en el resultado. El jugador dentro de 125 cm imponía Move=0. El adelantamiento dependía de BlockedTime, que no crecía mientras el seguidor avanzaba despacio. Las rutas de cruce regresaban a 220 cm de la salida. Un waypoint ocupado tampoco podía alcanzarse. Solo había 38 vehículos y dos circuitos privados largos.

## Corrección
BogotaGame.h, BogotaTraffic.cpp, BogotaPedestrianBehaviors.inl y BogotaCity.cpp implementan velocidad local con predicción y separación, continuidad en waypoints ocupados, rutas por dos intersecciones con claves de semáforo por segmento y 100 vehículos con separación entre circuitos compartidos. M_Sky se reconstruye con work/build_complete_sky.py. work/build_world_assets.py y work/fix_sky_material.py reutilizan ese generador para evitar regresiones.

## Evidencia
outputs/Revision_Cielo_Transito/validacion.json: PASS. Evasión 6/6 en tres situaciones, 864 peatones durante 600 s sin bloqueos prolongados, 100 vehículos durante 600 s sin solapamientos. Capturas verificadas de cuatro fases del cielo. BuildCookRun completado. Juego Current: PASS, {checks} comprobaciones aprobadas. Binario compilado y archivado con SHA256 idéntico.

## Regresión
ABogotaCity::ValidateStreetFlow ejecuta el movimiento real de SimulateWalkers con una obstrucción de jugador determinista, seis seguidores detrás de un peatón de 38 cm/s y una esquina ocupada. También verifica que las rutas de cruce tengan claves distintas y más de 50 m de recorrido entre cruces. work/validate_sky_street_flow.py ejecuta estas pruebas y las simulaciones completas. work/validate_packaged_current.ps1 comprueba la versión distribuida.

## Relacionado
La prueba anterior de multitud en mundo de editor no incluía un jugador estacionario ni exigía adelantar al peatón lento. Evitar depender únicamente de la ausencia de bloqueos en un mundo vacío. Preservar la separación física al añadir circuitos que comparten tramos; sus distancias de ruta no son comparables entre sí.

Backups: work/Backups/SkyStreetFlow_20261014.
''',encoding='utf-8')
print('Final verification:',checks,'packaged checks; report saved')
