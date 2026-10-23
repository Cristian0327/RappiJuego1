from pathlib import Path
root=Path(__file__).resolve().parent
IMPORT_ONLY_NAMES=['SK_TransMilenio','SK_TransMilenioG66']
exec(compile((root/'import_colombia_traffic_detailed.py').read_text(),str(root/'import_colombia_traffic_detailed.py'),'exec'))
assert report['status']=='PASS',report
exec(compile((root/'validate_colombia_traffic_detailed.py').read_text(),str(root/'validate_colombia_traffic_detailed.py'),'exec'))
