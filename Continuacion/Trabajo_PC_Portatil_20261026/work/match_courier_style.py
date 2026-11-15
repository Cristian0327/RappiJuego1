from pathlib import Path
root=Path(__file__).resolve().parents[1]
s=(root/'work/sculpt_hf_characters.py').read_text()
s=s.replace('U=.0125','U=.0225').replace('SH=(128,96,184);OR=np.array([-.8,-.6,0.])','SH=(72,54,104);OR=np.array([-.81,-.6075,0.])')
s=s.replace("def ell(c,p,s,power=2):shape(c,p,np.array(s)*.5,power)","def ell(c,p,s,power=2):shape(c,p,np.array(s)*.5,12 if power>=4 else power)")
s=s.replace("leg=[.49,.58,.73,.67,.60][role];shoulder=[1.15,1.28,1.39,1.32,1.26][role];w=[.50,.69,.44,.43,.48][role];head=shoulder+.30", "leg=[.68,.72,.77,.75,.73][role];shoulder=[1.15,1.24,1.26,1.23,1.20][role];w=[.40,.52,.36,.36,.38][role];head=shoulder+.27")
start=s.index('def eye(');end=s.index('def boot(',start)
s=s[:start]+'''def eye(x,y,z,skin):
 # Same restrained graphic eye grammar as the courier: no glossy glint.
 plate('white',x,y,z,.071,.067,.024)
 plate('eye',x+(.013 if x<0 else -.013),y-.022,z,.048,.067,.023)
 plate('hair',x,y-.025,z+.034,.074,.012,.023)
'''+s[end:]
s=s.replace("hw=.44 if role!=1 else .48\n ell(skin,(0,-.01,head),(hw,.37,.41),5);ell(skin,(0,-.035,head-.15),(hw*.80,.30,.12),4)","hw=.36 if role!=1 else .405\n box(skin,(0,-.01,head),(hw,.37,.225));box(skin,(0,-.012,head-.12),(hw-.045,.325,.045));box(skin,(0,-.01,head-.153),(hw-.09,.29,.0225))")
s=s.replace("eye(-.092,-.204,head+.012,skin);eye(.092,-.204,head+.012,skin)","eye(-.095,-.204,head-.012,skin);eye(.095,-.204,head-.012,skin)")
s=s.replace("head+.093,.11,.025","head+.057,.075,.0225").replace("head+.099,.11,.025","head+.061,.075,.0225")
s=s.replace("(.065,.075,.06),5)","(.045,.045,.035),5)")
s=s.replace("head-.113,.083,.014","head-.113,.045,.008")
s=s.replace("elbow=(side*(w*.60),-.012,shoulder-.24);wrist=(side*(w*.64),-.055,shoulder-.40)","elbow=(side*(w*.68),-.012,shoulder-.27);wrist=(side*(w*.71),-.025,shoulder-.48)")
s=s.replace(".17 if role!=1 else .23,.20", ".18 if role!=1 else .21,.20")
s=s.replace(".13 if role!=1 else .18,.16", ".15 if role!=1 else .18,.18")
# Remove the tiny stepped surface noise; retain discrete seams and large layered panels.
s=s.replace("for z in np.arange(leg+.03,shoulder-.10,.075):", "for z in []:")
s=s.replace("for i in range(18):plate('rustLight',rng.uniform(-.21,.21),-.279,rng.uniform(leg+.06,leg+.54),.025,.025,.012)","plate('rustLight',0,-.279,leg+.29,.27,.0225,.023)")
# Aprons follow the shorter torso instead of extending into the face.
s=s.replace("ell('rust',(0,-.245,leg+.31),(.54,.05,.63),5)","ell('rust',(0,-.245,leg+.17),(.43,.05,.48),5)")
s=s.replace("leg+.59", "leg+.37").replace("leg+.51", "leg+.30").replace("leg+.49", "leg+.31")
s=s.replace("ell('sage',(0,-.21,leg+.28),(.40,.045,.52),5)","box('sage',(0,-.21,leg+.12),(.34,.045,.43))")
s=s.replace("leg+.39", "leg+.30")
# Match the protagonist's flat face colors and dark cloth values.
s=s.replace("'skinLight':(.94,.67,.44,1)","'skinLight':(1.0,.757,.596,1)").replace("'skin':(.77,.47,.29,1)","'skin':(.953,.69,.514,1)")
s=s.replace("'hair':(.065,.035,.022,1)","'hair':(.13,.075,.052,1)")
s=s.replace("scene['reference']='Bogota_Encargados_TresVistas.png'","scene['reference']='Courier style: outputs/view_hero.png; distinct identities: Bogota_Encargados_TresVistas.png'")
s=s.replace("scene.view_settings.view_transform='Standard';", "scene.view_settings.view_transform='Standard';scene.view_settings.exposure=-.35;")
s=s.replace("scene['grid_m']=U", "scene['grid_m']=U;scene['style_match']='VoxelExplorer: 2.25 cm grid, planar face, restrained rectangular eyes, layered cloth'")
(root/'work/sculpt_courier_style_staff.py').write_text(s)
