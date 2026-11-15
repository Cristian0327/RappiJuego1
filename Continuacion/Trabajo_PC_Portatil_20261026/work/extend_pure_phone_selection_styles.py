import unreal,json,re,sys
from pathlib import Path
r=Path(unreal.Paths.project_dir()).parent;ns={};s=(r/'work/extend_pure_phone_data.py').read_text(encoding='utf-8-sig');exec(compile(s[:s.index('# Header')],'PurePhoneSelectionSetup','exec'),ns);globals().update({k:v for k,v in ns.items() if k!='__builtins__'})
g=Graph();last=valid(g)
for n in ['Selection','OrderSelection','CatalogSelection','PaintSelection','UpgradeIDs','ModelIDs']:g.get(n)
g.call('OfferChosen','GetSelectedOffer',CORE);g.link('Delivery','Delivery','OfferChosen','self');count=0
palette=[(.025,.65,.86,1),(1,.22,.025,1),(.94,.72,.025,1),(.72,.025,.055,1),(.79,.76,.64,1),(.035,.045,.06,1)]
for row in info['widgets']:
 if not row['class'].endswith('DeliveryChoiceButton'):continue
 widget=row['name'];m=re.match(r'App(\d)_(Bike|Moto)_(\d+)',widget);page=int(m[1]);mode=m[2];n=int(m[3]);tag='Choice'+str(count);count+=1;paint=False
 if page==2:index=(n-2)//2;selection='OrderSelection'
 elif page==5:index=n-1;selection='OrderSelection'
 elif page==4:index=n-7+(3 if mode=='Moto' else 0);selection='CatalogSelection'
 elif page==6:index=n-2+10;selection='Selection'
 elif page==3:
  paint=n>=(15 if mode=='Moto' else 13);index=n-(15 if mode=='Moto' else 13) if paint else n-7+(4 if mode=='Moto' else 0);selection='PaintSelection' if paint else 'Selection'
 else:raise AssertionError(widget)
 g.get(widget);g.call(tag+'Selected','EqualEqual_IntInt',M,B=str(index));g.link(selection,selection,tag+'Selected','A');condition=tag+'Selected'
 if page==2:
  g.call(tag+'Explicit','BooleanAND',M);g.link(condition,'ReturnValue',tag+'Explicit','A');g.link('OfferChosen','Found',tag+'Explicit','B');condition=tag+'Explicit'
 if paint:
  color=palette[index];g.call(tag+'Tint','MakeColor',M,R=str(color[0]),G=str(color[1]),B=str(color[2]),A='1');g.call(tag+'Opacity','SelectFloat',M,A='1',B='.55');g.link(condition,'ReturnValue',tag+'Opacity','bPickA');g.call(tag+'Alpha','SetRenderOpacity',W);g.link(widget,widget,tag+'Alpha','self');g.link(tag+'Opacity','ReturnValue',tag+'Alpha','InOpacity');g.exec(last,tag+'Alpha');last=tag+'Alpha';colorNode=tag+'Tint'
 else:
  normal='(R=.16,G=.25,B=.29,A=1)';g.call(tag+'Color','SelectColor',M,A='(R=.98,G=.47,B=.10,A=1)',B=normal);g.link(condition,'ReturnValue',tag+'Color','bPickA');colorNode=tag+'Color'
  if page in [3,4,6]:
   array='ModelIDs' if page==4 else 'UpgradeIDs';g.call(tag+'ID','Array_Get',AL,Index=str(index));g.link(array,array,tag+'ID','TargetArray');g.call(tag+'Owned','OwnsVehicle' if page==4 else 'Owns',CORE);g.link('Delivery','Delivery',tag+'Owned','self');g.link(tag+'ID','Item',tag+'Owned','ID');g.call(tag+'OwnedTint','SelectColor',M,A='(R=.08,G=.46,B=.39,A=1)',B=normal);g.link(tag+'Owned','ReturnValue',tag+'OwnedTint','bPickA');g.links=[x for x in g.links if x!=[tag+'OwnedTint','ReturnValue',tag+'Color','B']];g.link(tag+'OwnedTint','ReturnValue',tag+'Color','B')
 g.call(tag+'Apply','SetBackgroundColor',BTN);g.link(widget,widget,tag+'Apply','self');g.link(colorNode,'ReturnValue',tag+'Apply','InBackgroundColor');g.exec(last,tag+'Apply');last=tag+'Apply'
g.exec(last,'result');g.build('RefreshSelectionStyles',[])
g=Graph();last=valid(g)
for fn in ['RefreshHeader','RefreshOfferCards','RefreshActiveCards','RefreshUpgradeCards','RefreshVehicleCards','RefreshPageDetails','RefreshGaragePreview','RefreshSelectionStyles']:
 g.call(fn,fn);g.exec(last,fn);last=fn
g.exec(last,'result');g.build('RefreshText');assert E.compile_blueprint(bp);assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False);(r/'work/pure_phone_selection_styles.json').write_text(json.dumps({'status':'COMPILED_STAGING','choice_buttons':count,'palette_colors':6,'selected':'orange','owned':'teal','pending':['Purchase action availability and requirement text','Visual verification']},indent=2));unreal.log('PURE_PHONE_SELECTION_STYLES_PASS choices='+str(count))
