import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig'))
exec((root/'work/migrate_residential_market_blueprint.py').read_text(encoding='utf-8-sig'))
exec((root/'work/migrate_offer_expiration_blueprint.py').read_text(encoding='utf-8-sig'))
