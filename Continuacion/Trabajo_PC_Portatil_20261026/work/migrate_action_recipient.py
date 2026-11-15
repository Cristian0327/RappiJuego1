import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
source=(root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig')
exec(source.split('reports=[]')[0])
A='/Script/Engine.KismetArrayLibrary';reports=[]
start=source.index("g=Graph()\nfor v in ['bHolding','State','PhoneOpen','Vehicle','ActiveOrders','Order']")
end=source.index("reports.append(g.build('BeginAction'))",start)+len("reports.append(g.build('BeginAction'))")
exec(source[start:end])
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
unreal.log('ACTION_USES_RECIPIENT_INTERFACE')
