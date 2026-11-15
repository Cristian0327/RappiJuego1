from pathlib import Path
root=Path(__file__).resolve().parents[1]
for name in ['import_city_visuals.py','import_staff_courier_eyes.py','migrate_lifecycle_blueprints.py','migrate_residential_market_blueprint.py']:
 p=root/'work'/name
 exec(compile(p.read_text(encoding='utf-8-sig'),str(p),'exec'),{'__file__':str(p)})
