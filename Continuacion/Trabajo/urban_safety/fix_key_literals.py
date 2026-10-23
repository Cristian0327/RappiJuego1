from pathlib import Path
p=Path('urban_safety/build_traversal_blueprint.py');s=p.read_text();s=s.replace('Key=\'(KeyName="\'+name+\'")\'', 'Key=name');p.write_text(s)
