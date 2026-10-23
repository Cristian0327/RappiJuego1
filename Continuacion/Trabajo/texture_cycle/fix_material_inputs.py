from pathlib import Path
p=Path('texture_cycle/implement.py');s=p.read_text().replace('for name in names:\n  i=','for name in names.values():\n  i=');s=s.replace("obj.set_editor_property('texture',mask);random=", "obj.set_editor_property('texture',mask);obj.set_editor_property('sampler_type',unreal.MaterialSamplerType.SAMPLERTYPE_MASKS);random=");p.write_text(s)
