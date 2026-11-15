from pathlib import Path
p=Path('work/build_pure_world_runtime_test.py');s=p.read_text(encoding='utf-8-sig')
s=s.replace("g.exec(start,tag);done(tag);checks.append(name)",'''g.exec(start,tag)
 if name in ['NOON_AMBIENT','NIGHT_AMBIENT','ROOF_TRACE_CACHED','RAIN_FOLLOWS_CAMERA','RAIN_STOPS']:
  g.call(tag+'Shot','ExecuteConsoleCommand',K,Command='Shot showui filename="'+str(r/('work/PureWorldVisualQA/'+name+'.png')).replace(chr(92),'/')+'"');g.exec(tag,tag+'Shot');done(tag+'Shot')
 else:done(tag)
 checks.append(name)''')
s=s.replace("r=Path(unreal.Paths.project_dir()).parent;sys.path", "r=Path(unreal.Paths.project_dir()).parent;(r/'work/PureWorldVisualQA').mkdir(exist_ok=True);sys.path")
p.write_text(s,encoding='utf-8')
