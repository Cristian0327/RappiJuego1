from pathlib import Path
p=Path('work/compare_manual_rig.py');s=p.read_text().replace(".078,.17,21", ".080,.18,19").replace(".072,.18,20", ".075,.18,18").replace(".060,.16,22", ".078,.18,20").replace(".054,.13,22", ".065,.15,20");p.write_text(s)
