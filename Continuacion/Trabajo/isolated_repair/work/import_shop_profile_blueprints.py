import unreal
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/migrate_shop_rule_blueprints.py').read_text(encoding='utf-8-sig'))
exec((root/'work/migrate_profile_blueprints.py').read_text(encoding='utf-8-sig'))
