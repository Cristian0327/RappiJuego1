import sys,json,unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parent
sys.path.insert(0,str(root/'Herramientas'))
import blueprint_graph as d
d.bp=unreal.load_asset('/Game/World/BP_BogotaCity')
g=d.Graph();M=d.M;A='/Script/Engine.KismetArrayLibrary'
g.get('TrafficPaintPalette');g.call('Count','Array_Length',A);g.link('TrafficPaintPalette','TrafficPaintPalette','Count','TargetArray')
for id,fn,b in [('Model','Percent_IntInt','20'),('Variant','Divide_IntInt','20')]:
 g.call(id,fn,M,B=b);g.link('entry','VehicleIndex',id,'A')
for id,src,b in [('ModelHue','Model','7'),('VariantHue','Variant','5')]:
 g.call(id,'Multiply_IntInt',M,B=b);g.link(src,'ReturnValue',id,'A')
g.call('Hue','Add_IntInt',M);g.link('ModelHue','ReturnValue','Hue','A');g.link('VariantHue','ReturnValue','Hue','B')
g.call('Index','Percent_IntInt',M);g.link('Hue','ReturnValue','Index','A');g.link('Count','ReturnValue','Index','B')
g.call('Paint','Array_Get',A);g.link('TrafficPaintPalette','TrafficPaintPalette','Paint','TargetArray');g.link('Index','ReturnValue','Paint','Index');g.link('Paint','Item','result','ReturnValue');g.exec('entry','result');g.build('TrafficPaintFor')
unreal.EditorAssetLibrary.save_loaded_asset(d.bp,only_if_is_dirty=False)
exec((root/'work/validate_traffic_paint.py').read_text())
