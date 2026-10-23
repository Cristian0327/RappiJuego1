from pathlib import Path
for name in ['integrate_monserrate.py','finish_monserrate.py']:
 p=Path('compact_city')/name;s=p.read_text();marker='# Trace the complete pavement' if '# Trace the complete pavement' in s else None
 if marker:s=s[:s.index(marker)]+"exec(compile((C/'verify_monserrate.py').read_text(),'VerifiedMonserrateAccess','exec'),{})\n";p.write_text(s)
