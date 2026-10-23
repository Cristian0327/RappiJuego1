from pathlib import Path
p=Path('work/render_rig_comparison.py');s=p.read_text();a=s.index('for label,file in ');b=s.index(':\n bpy.ops.wm.open_mainfile',a);s=s[:a]+"for label,file in [('Mixamo',out/'Mixamo_AutoRig.blend')]"+s[b:];Path('work/render_mixamo_comparison.py').write_text(s)
