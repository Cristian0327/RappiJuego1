import unreal,json,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;sys.path.insert(0,str(r/'Herramientas'));import blueprint_graph as d
E=unreal.BlueprintEditorLibrary;mel=unreal.MaterialEditingLibrary
s=Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/fix_solid_vehicles_npc_recovery.py').read_text();exec(s[s.index("m=unreal.load_asset('/Game/Traffic/Detailed/M_TrafficVoxelVertex');mel.delete_all"):s.index('# Complete palettes')]);unreal.log('FINAL_MATERIAL_ATLAS_PASS')
