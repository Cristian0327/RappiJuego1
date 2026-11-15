import json
from pathlib import Path
from fleet20_catalog import FLEET20
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs/DeliveryArt/TrafficDetailed'
(OUT/'fleet20_catalog.json').write_text(json.dumps(FLEET20,indent=2,ensure_ascii=False),encoding='utf-8')
rows=[]
for s in FLEET20:
 half=s['length']*50+(40 if 'spare' in s['extras'] else 14)
 rows.append(f' {{TEXT("{s["name"]}"),{half:.2f}f,{s["width"]*50+26:.2f}f,{s["radius"]*100:.2f}f}},')
rows += [' {TEXT("TaxiCompact"),199.f,111.f,32.f},',' {TEXT("TaxiSedan"),228.f,112.5f,32.f},']
code='// Generated from the 20 distinct, closed-body private vehicle catalog.\nstruct FTrafficModelSpec {const TCHAR* Name;float HalfLength,HalfWidth,WheelRadius;};\nstatic const FTrafficModelSpec TrafficCarModels[]={\n'+'\n'.join(rows)+'\n};\nstatic_assert(UE_ARRAY_COUNT(TrafficCarModels)==22);\n'
(ROOT/'outputs/BogotaVoxel/Source/BogotaVoxel/TrafficModelCatalog.inl').write_text(code,encoding='utf-8')
print('FLEET20_RUNTIME_CATALOG_READY')
