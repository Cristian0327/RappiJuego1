exec(compile(__import__('pathlib').Path('C:/Users/CRISTIAN/Documents/Codex/2026-09-12/ho/traffic_gameplay_repair/implement.py').read_text().split('# Recovery never')[0],'helpers','exec'))
assert 'isolated_repair' in root.parts
PHONE='/Game/Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone.WBP_BlueprintPhone_C';b=use(PHONE);g=d.Graph();g.call('P','BreakVector',M);g.link('entry','Position','P','InVec');g.call('C','BreakVector',M);g.link('entry','Center','C','InVec')
for tag,axis,full,small,invert in [('X','Y',88000,11000,False),('Y','X',64000,16000,True)]:
 op(g,tag+'Delta','Subtract_DoubleDouble',('P',axis),('C',axis));g.call(tag+'Span','SelectFloat',M,A=str(full),B=str(small));g.link('entry','FullMap',tag+'Span','bPickA');op(g,tag+'Ratio','Divide_DoubleDouble',(tag+'Delta','ReturnValue'),(tag+'Span','ReturnValue'));g.call(tag+'Norm','Subtract_DoubleDouble' if invert else 'Add_DoubleDouble',M,A='.5');g.link(tag+'Ratio','ReturnValue',tag+'Norm','B')
g.call('Point','MakeVector2D',M);g.link('XNorm','ReturnValue','Point','X');g.link('YNorm','ReturnValue','Point','Y');g.link('Point','ReturnValue','result','ReturnValue');g.exec('entry','result');build(b,g,'MapNormalizedPoint',[dict(name='Position',category='struct',object='/Script/CoreUObject.Vector'),dict(name='Center',category='struct',object='/Script/CoreUObject.Vector'),dict(name='FullMap',category='bool'),dict(name='ReturnValue',category='struct',object='/Script/CoreUObject.Vector2D',out=True)],True)
plan=json.loads((P.parent/'new_map_audit/integration_plan.json').read_text());c=unreal.get_default_object(b.generated_class());preserved={n:list(c.get_editor_property(n)) for n in ['CityRoadStarts','CityRoadEnds']};c.set_editor_property('MapBuildings',[unreal.Vector((v[0]+v[2])/2,(v[1]+v[3])/2,0) for v in plan['building_footprints']]);c.set_editor_property('MapExtents',[unreal.Vector2D((v[2]-v[0])/2,(v[3]-v[1])/2) for v in plan['building_footprints']]);save(b)
# Rebuild only the input event, with exactly the same inverse mapping.
s=(root/'work/extend_pure_phone_map_input.py').read_text();s=s[s.index('g=MapGraph();'):s.index('assert E.compile_blueprint(bp)')];s=s.replace("B='90000'","B='64000'").replace("B='60000'","B='88000'")
class MapGraph(d.Graph):
 def build(self,name):
  for n in self.nodes:
   if n.get('kind')=='call' and not n.get('owner'):n['owner']=PHONE
  build(b,self,name)
ns=dict(MapGraph=MapGraph,bp=b,M=M,K=K,CORE=C,PHONE=PHONE,UI='/Script/UMG.WidgetBlueprintLibrary',INPUT='/Script/Engine.KismetInputLibrary',W='/Script/UMG.Widget',SLATE='/Script/UMG.SlateBlueprintLibrary');exec(compile(s,'CurrentMapClickInverse','exec'),ns);save(b)
unreal.log('MAP_DATA_AND_CLICK_INVERSE_READY buildings='+str(len(plan['building_footprints'])))
