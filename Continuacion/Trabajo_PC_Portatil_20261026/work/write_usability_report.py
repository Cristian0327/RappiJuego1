from pathlib import Path
import json, re, csv, shutil, hashlib

root = Path(__file__).resolve().parents[1]
out = root / 'outputs/Revision_Usabilidad'
issues = [
 ('U01','Alta','La aceptación continuaba al cambiar de ventana','Seleccionar una oferta, mantener aceptar y desactivar la ventana antes de completar la espera.','La tecla consumida por la interfaz podía perder su evento de liberación; no se cancelaba la acción al desactivar la aplicación.','La desactivación cancela la espera y detiene los controles de movimiento.','alt_tab_cancels_pending_acceptance'),
 ('U02','Media','Flechas y Enter no permitían completar la navegación','Abrir Pedidos y pulsar abajo, arriba y Enter.','La interfaz solo reconocía la cruceta y las teclas de confirmación anteriores.','Se admiten flechas y Enter; mantener confirma y soltar cancela, sin seleccionar automáticamente una oferta.','keyboard_down_selects_first_offer; keyboard_up_selects_previous_offer; enter_supports_hold_to_accept'),
 ('U03','Media','No se veía la ruta completa antes de aceptar','Seleccionar una oferta con nombres largos de origen y destino.','El detalle de la selección no mostraba ambos nombres completos.','El detalle muestra Recoge, Entrega, recompensa y capacidad disponible.','selected_offer_shows_full_origin_and_destination'),
 ('U04','Media','La barra de aceptación aparecía lejos del botón','Mantener el botón para tomar una ruta.','La barra usaba coordenadas fijas del HUD, incluso con el teléfono abierto.','La barra se coloca sobre el borde inferior del botón real.','hold_progress_is_at_accept_button'),
 ('U05','Baja','El mapa tapaba parte de sus instrucciones','Abrir Mapa y leer las instrucciones superiores.','El mapa empezaba antes de terminar el bloque de texto.','Se ajustaron posición y altura del mapa, incluso al reutilizar la página.','map_does_not_cover_its_instructions'),
 ('U06','Baja','Equipar parecía disponible para vehículos sin comprar','Abrir Garaje y elegir un modelo bloqueado o no adquirido.','El control visual no reflejaba las restricciones que ya comprobaba la lógica.','Equipar se desactiva si el modelo no pertenece al jugador o no admite la carga actual.','unowned_vehicle_cannot_offer_equip_action'),
 ('U07','Baja','Las ayudas del teclado eran demasiado pequeñas','Abrir el teléfono en una ventana pequeña.','El tamaño de fuente disminuía con la escala de la interfaz.','Las ayudas conservan un mínimo de 12 píxeles físicos y espacio para dos líneas.','keyboard_hints_have_readable_physical_size'),
 ('U08','Media','La vista de maletas podía cargar una textura inexistente','Cambiar repetidamente entre páginas y entrar a la vista de carga con una selección de otra categoría.','Un índice heredado podía quedar fuera de 10–12 y producir Art[Selection-10] con índice negativo; el registro mostraba /Game/Delivery/Art/(null).(null).','Se normalizan las selecciones de cada categoría y se verifica el rango antes de cargar la ilustración.','cargo_page_selection_is_sanitized; cargo_preview_loaded_after_page_changes'),
]
baseline = json.loads((out/'Antes/validacion.json').read_text(encoding='utf-8-sig'))
runs=[]
for label in ['Final/1024x576','Final/1280x720','Final/1920x1080','Empaquetado/1280x720','Reinicio']:
 p=out/label/'validacion.json'
 d=json.loads(p.read_text(encoding='utf-8-sig'))
 assert d['status']=='PASS' and not d['failures'], (label,d)
 runs.append({'prueba':label,'comprobaciones':d['total'],'estado':d['status']})
reg=json.loads((root/'work/packaged_current_validation.json').read_text(encoding='utf-8-sig'))
assert reg['status']=='PASS' and not reg['failures']
log=(root/'work/packaged_current_validation.log').read_text(encoding='utf-8-sig',errors='replace')
reg_count=len(re.findall(r'DELIVERY_TEST [^\r\n]* PASS',log))
assert reg_count>1900, reg_count
shutil.copy2(root/'work/packaged_current_validation.json',out/'regresion_completa.json')
with (out/'hallazgos.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f); w.writerow(['ID','Prioridad','Problema','Reproducción','Causa','Corrección','Pruebas','Estado'])
 for row in issues:w.writerow([*row,'Corregido y verificado'])
summary={'fecha_local':'2026-10-14','problemas_corregidos':len(issues),'baseline':{'total':baseline['total'],'fallos':len(baseline['failures'])},'ejecuciones':runs,'regresion_completa':{'estado':reg['status'],'comprobaciones_pass':reg_count},'hallazgos':[dict(zip(['id','prioridad','problema','reproduccion','causa','correccion','pruebas'],x)) for x in issues]}
(out/'resumen.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
exe=root/'outputs/BogotaVoxel_Playable_Current/Windows/BogotaVoxel/Binaries/Win64/BogotaVoxel.exe'
built=root/'outputs/BogotaVoxel/Binaries/Win64/BogotaVoxel.exe'
digest=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
assert digest(exe)==digest(built),'Packaged executable differs'
(out/'ejecutable_sha256.txt').write_text(digest(exe)+'  BogotaVoxel.exe\n',encoding='utf-8')
lines=['# Revisión de usabilidad de Bogotá Voxel','', 'Fecha: 14 de octubre de 2026. Estado: **completada; ocho problemas corregidos y verificados**.','',
 'Se realizó una exploración inicial del juego y una revisión de sus tareas principales. Después se reprodujeron los fallos con la interfaz real de Unreal, se corrigieron sus causas y se repitieron las comprobaciones con renderizado del juego. Los perfiles de prueba están aislados de la partida personal.','',
 '## Resultado de las pruebas','',
 f'La referencia inicial registró {baseline["total"]} comprobaciones y {len(baseline["failures"])} fallos de aserción correspondientes a siete problemas. La revisión del registro identificó un octavo problema de carga de texturas; se añadieron dos comprobaciones para impedir su reaparición.','',
 '| Ejecución final | Comprobaciones | Resultado |','|---|---:|---|']
for r in runs:lines.append(f'| {r["prueba"]} | {r["comprobaciones"]} | PASS |')
lines += [f'| Regresión completa del paquete jugable | {reg_count} | PASS |','',
 'Las repeticiones a distintas resoluciones validan los mismos criterios; no equivalen a cientos de tareas humanas diferentes. No se detectaron errores del motor en las ejecuciones finales de usabilidad. La prueba de reinicio también se repitió en el ejecutable empaquetado.','',
 '## Problemas corregidos','', '| ID | Prioridad | Problema | Solución |','|---|---|---|---|']
for i,p,title,steps,cause,fix,test in issues:lines.append(f'| {i} | {p} | {title} | {fix} |')
lines += ['', '## Reproducción y evidencia','']
for i,p,title,steps,cause,fix,test in issues:
 lines += [f'### {i}: {title}','',f'**Cómo reproducir:** {steps}', '', f'**Causa:** {cause}', '', f'**Corrección:** {fix}', '', f'**Regresión:** `{test}`. Resultado final: PASS.','']
lines += ['## Capturas de antes y después','',
 'Las capturas provienen del juego renderizado y muestran estados controlados de prueba. El perfil con cinco pedidos utiliza mejoras y saldo de prueba.','',
 '### Pedido seleccionado y barra de aceptación','', 'Antes:', '', '![Antes: información incompleta y barra separada](Antes/QA_Accept_Hold.png)','', 'Después:', '', '![Después: ruta completa y barra en el botón](Empaquetado/1280x720/QA_Accept_Hold.png)','',
 '### Mapa e instrucciones','', 'Antes:', '', '![Antes: superposición de instrucciones](Antes/QA_Map.png)','', 'Después:', '', '![Después: instrucciones despejadas](Empaquetado/1280x720/QA_Map.png)','',
 '### Resolución pequeña y carga de cinco pedidos','', '![Teléfono a 1024 por 576](Final/1024x576/QA_Accept_Hold.png)','', '![Cinco pedidos en el paquete final](Empaquetado/1280x720/QA_Five_Orders.png)','',
 '## Cobertura y límites','',
 '- Inicio sin dinero y con un espacio de carga; apertura, cierre y cambio repetido de aplicaciones del teléfono.',
 '- Selección explícita de oferta; flechas; confirmar manteniendo; liberación, repetición de tecla, cambio de página, cambio de selección, pérdida de foco y ofertas vencidas.',
 '- Mapa: instrucciones, colocación y retirada de marca; pausa y reanudación; bloqueo del movimiento mientras se usa el teléfono.',
 '- Compras sin fondos y bloqueadas; compra única; modelos equipables; ampliaciones de capacidad y cinco pedidos simultáneos; rechazo de un vehículo con capacidad insuficiente.',
 '- Persistencia del dinero, las mejoras y el vehículo al volver a abrir el juego con un perfil de prueba.',
 '- Regresión existente de tiendas, recogida de productos, presupuesto, pago, entrega, colisiones de acceso y variantes de vehículo. Se usa posicionamiento controlado para recorrer casos reproducibles.',
 '- Se inspeccionaron capturas reales a distintas resoluciones. Los eventos de interfaz y de desactivación se ejercitaron de forma instrumentada; no se realizó una prueba con mando físico ni un estudio con participantes externos.',
 '- Los pedidos activos no se conservan al reiniciar en el diseño actual; la prueba verifica que el inicio no inventa pedidos ni conserva una pulsación activa.',
 '- Esta revisión no acredita la ausencia de todos los errores posibles ni sustituye una sesión prolongada con jugadores en distintos equipos. Las comprobaciones previas de cielo, peatones y tráfico están documentadas en la revisión anterior; no se presentan como nuevas pruebas de esta sesión.','',
 '## Archivos entregados','',
 '- `hallazgos.csv`: ocho hallazgos con causa, reproducción, corrección y prueba asociada.',
 '- `resumen.json`: resultados consolidados; cada carpeta contiene su `validacion.json` y capturas.',
 '- `regresion_completa.json`: resultado de la batería del paquete final.',
 '- `ejecutable_sha256.txt`: huella del ejecutable verificado, idéntico al compilado.',
 '- Juego actualizado: `../BogotaVoxel_Playable_Current/Windows/BogotaVoxel.exe`.','']
(out/'INFORME.md').write_text('\n'.join(lines),encoding='utf-8')
memory=root/'memory';memory.mkdir(exist_ok=True)
(memory/'2026-10-14-usabilidad-juego.md').write_text('# Depuración de usabilidad — DONE\n\nSíntoma: controles ambiguos, aceptación sin cancelación al perder foco y defectos de presentación del teléfono.\n\nCausas y correcciones: ocho hallazgos reproducidos, detallados en outputs/Revision_Usabilidad/INFORME.md y hallazgos.csv. Cambios en DeliverySystem.cpp, DeliveryUI.cpp y DeliverySystem.h; DeliveryUsability.cpp añade las pruebas instrumentadas.\n\nEvidencia: baseline de 60 comprobaciones con 9 fallos; 62 PASS por resolución final, paquete final PASS y 6 comprobaciones de reinicio PASS. Regresión completa: '+str(reg_count)+' PASS.\n\nRelacionado: revisión previa de cielo y tránsito en outputs/Revision_Cielo_Transito. Límite: revisión por agente con renderizado y entradas instrumentadas, sin participantes externos ni mando físico.\n',encoding='utf-8')
print(json.dumps({'issues':len(issues),'runs':runs,'regression_pass':reg_count,'exe_sha256':digest(exe)},ensure_ascii=False,indent=2))
