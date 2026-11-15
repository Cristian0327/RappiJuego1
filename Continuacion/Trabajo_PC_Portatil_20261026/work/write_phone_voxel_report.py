from pathlib import Path
import json, shutil, re, hashlib

root=Path(__file__).resolve().parents[1]
out=root/'outputs/Revision_UI_Voxel';out.mkdir(exist_ok=True)
before=out/'Antes';before.mkdir(exist_ok=True)
for name in ['QA_Home.png','QA_Garage_Locked.png','QA_Accept_Hold.png','QA_Map.png']:
 shutil.copy2(root/'outputs/Revision_Usabilidad/Final/1280x720'/name,before/name)
runs=[]
for label,target in [('CelularFinal/1024x576','1024x576'),('CelularFinal/1280x720','1280x720'),('CelularFinal/1920x1080','1920x1080'),('CelularEmpaquetado/1280x720','Paquete_1280x720')]:
 src=root/'outputs/Revision_Usabilidad'/label
 data=json.loads((src/'validacion.json').read_text(encoding='utf-8-sig'))
 assert data['status']=='PASS' and not data['failures'],label
 dst=out/target;dst.mkdir(exist_ok=True)
 for p in src.iterdir():
  if p.suffix in ['.png','.json']:shutil.copy2(p,dst/p.name)
 runs.append({'ejecucion':target,'comprobaciones':data['total'],'estado':data['status']})
reg=json.loads((root/'work/packaged_current_validation.json').read_text(encoding='utf-8-sig'))
assert reg['status']=='PASS' and not reg['failures']
log=(root/'work/packaged_current_validation.log').read_text(encoding='utf-8-sig',errors='replace')
assert ': Error:' not in log and 'Fatal error' not in log
count=len(re.findall(r'DELIVERY_TEST [^\r\n]* PASS',log));assert count>1900
shutil.copy2(root/'work/packaged_current_validation.json',out/'regresion_paquete.json')
shots=root/'work/UsabilityProfile/FullRegression/Saved/Screenshots'
for name in ['UrbanWorkshop.png','UrbanCatalog.png','CargoShop.png','DeliveryHUD.png','UrbanHome.png','UrbanOrders.png']:
 assert (shots/name).exists(),name
 shutil.copy2(shots/name,out/name)
resume=json.loads((out/'Reinicio/validacion.json').read_text(encoding='utf-8-sig'))
assert resume['status']=='PASS' and not resume['failures']
native=root/'outputs/BogotaVoxel/Binaries/Win64/BogotaVoxel.exe'
exe=root/'outputs/BogotaVoxel_Playable_Current/Windows/BogotaVoxel/Binaries/Win64/BogotaVoxel.exe'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
assert sha(native)==sha(exe)
summary={'fecha_local':'2026-10-14','celular_original':{'ancho_logico':420,'alto_logico':680,'mismo_escalado_y_proporciones':True},'ejecuciones_ui':runs,'regresion_paquete':{'estado':'PASS','comprobaciones_pass':count},'reinicio':{'estado':'PASS','comprobaciones':resume['total']},'ejecutable_sha256':sha(exe),'actualizacion_impeccable':'No completada: el instalador devolvió invalid zip data en dos intentos. Se conserva v3.9.1.'}
(out/'validacion_consolidada.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
def pic(name,label):return f'![{label}]({(out/name).as_posix()})'
lines=['# Interfaz voxel de Bogotá Voxel','', '**El celular conserva su tamaño y sus proporciones originales.** El taller, la progresión y la escena del garaje funcionan dentro de la misma pantalla de 420 × 680 unidades, con el mismo escalado anterior.','',
 '## Cambios terminados','',
 '- **Progresión de mejoras:** cuatro nodos para la cicla y seis para la moto, conectados en su orden real. Cada nodo muestra su paso, precio o estado de instalada. Los bloqueados llevan `[X]`; el detalle explica el requisito, el efecto y el saldo que falta. La rama de cicla conduce a la de moto.',
 '- **Navegación:** las flechas y la cruceta recorren el árbol según la posición de los nodos. Las pestañas distinguen ciclas y motos. Los modelos comprables se presentan en Mi garaje, separados de Mis mejoras.',
 '- **Garaje voxel real:** suelo de baldosas, paredes de bloques, banco de trabajo, herramientas, cajas, lámpara y plataforma de servicio. Sustituye el fondo negro. La cámara deja espacio alrededor del vehículo; la imagen conserva su proporción.',
 '- **Lenguaje visual compartido:** botones escalonados con relieve y estados coherentes; texto claro sobre superficies oscuras; selección naranja y acciones turquesa; ayudas y HUD con la misma fuente pixel.',
 '- **Inicio y HUD:** etiquetas con fondo, indicación de la aplicación actual, paneles de bloques, mensajes legibles sobre el mundo y controles permanentes resumidos. El teléfono abre sin giro que deforme los píxeles.',
 '- **Pedidos:** iconos correspondientes al tipo de tienda, detalle de ruta con espacio para nombres largos, progreso sobre el botón y mensajes de carga completa y ausencia de pedidos.',
 '- **Compras y capacidad:** se explica el requisito concreto de cada modelo y el dinero que falta. Equipar se bloquea cuando el vehículo no admite la carga actual.','',
 '## Capturas del resultado','',
 '### Taller de cicla dentro del celular','',pic('Paquete_1280x720/QA_Workshop_Bike.png','Progresión de cicla en el celular original'),'',
 '### Rama de moto','',pic('UrbanWorkshop.png','Mejoras de moto conectadas'),'',
 '### Garaje y requisitos de modelos','',pic('Paquete_1280x720/QA_Garage_Locked.png','Garaje voxel con el tamaño original del celular'),'',
 '### Inicio y pedidos','',pic('Paquete_1280x720/QA_Home.png','Inicio del celular'),'',pic('Paquete_1280x720/QA_Accept_Hold.png','Ruta larga, recompensa y aceptación'),'',
 '### HUD','',pic('Paquete_1280x720/QA_HUD.png','HUD con paneles voxel y texto legible'),'',
 '## Verificación','', '| Ejecución | Comprobaciones | Resultado |','|---|---:|---|']
for r in runs:lines.append(f'| {r["ejecucion"]} | {r["comprobaciones"]} | PASS |')
lines += [f'| Regresión completa del paquete | {count} | PASS |',f'| Recuperación del progreso al reiniciar | {resume["total"]} | PASS |','',
 'Se verificaron la dimensión original del celular, lectura de nodos, navegación espacial, requisito exacto de modelos, contraste de ofertas en estado normal y hover, nombres largos sin ocultar la recompensa, ausencia de pedidos, compras y carga. La batería completa conserva las pruebas de entregas, tiendas y vehículos. Los cambios de títulos se verifican por la página que abre cada acceso, para que un renombre no se confunda con un fallo de navegación.','',
 'Las capturas son del juego renderizado, no maquetas. Las comprobaciones usan perfiles aislados y eventos instrumentados de Unreal; no sustituyen un estudio con jugadores externos ni una prueba de mando físico. El árbol corresponde a los requisitos existentes y no cambia los precios ni las reglas de progreso. El escenario del garaje se captura al cambiar modelo, mejora o pintura, no continuamente.','',
 '## Antes del rediseño','',pic('Antes/QA_Garage_Locked.png','Garaje anterior con fondo negro'),'',
 '## Juego y archivos','',
 f'- [Juego actualizado]({(root/"outputs/BogotaVoxel_Playable_Current/Windows/BogotaVoxel.exe").as_posix()})',
 '- `validacion_consolidada.json`: resultados y huella del ejecutable, idéntico al compilado.',
 '- Las carpetas de resolución incluyen resultados individuales y capturas.',
 '- La actualización opcional de Impeccable no pudo completarse: el instalador recibió un archivo inválido en dos intentos. La guía anterior sigue instalada.','']
(out/'LEEME.md').write_text('\n'.join(lines),encoding='utf-8')
design=root/'outputs/BogotaVoxel/DESIGN.md'
text=design.read_text(encoding='utf-8')
text+='\n## Garaje y progresión final\n\nConservar siempre el celular original de 420 × 680 y su escala. Cuatro nodos de cicla y seis de moto se conectan dentro de la pantalla; las flechas siguen su posición. El detalle del nodo explica el requisito y el coste. El modelo se presenta en un escenario 3D voxel con suelo, paredes, banco y herramientas, con cámara alejada y proporción de captura ajustada al visor. No ampliar el celular a una tableta.\n'
design.write_text(text,encoding='utf-8')
(root/'memory/2026-10-14-ui-voxel.md').write_text('# UI voxel — DONE\n\nUsuario pidió rediseñar toda UI/UX y después explicitó conservar estrictamente la idea, tamaño y proporciones de celular. Resultado final: celular original 420×680 con mismo escalado; árbol compacto con requisitos reales, garaje 3D voxel y vehículo menor, colores y estados compartidos, mejor lectura del HUD, ofertas y estados vacíos. La variante ancha fue descartada por petición del usuario.\n\nEvidencia y pruebas finales: outputs/Revision_UI_Voxel/LEEME.md y validacion_consolidada.json. La regresión completa del paquete pasa '+str(count)+' comprobaciones y la usabilidad pasa en las tres resoluciones y el paquete.\n\nImpeccable update falló dos veces con invalid zip data; instalada v3.9.1 sin cambios.\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
