exec((__import__('pathlib').Path(__file__).parent/'import_corrected_rigs.py').read_text().split('for file in (art/')[0])
exec((root/'work/import_cohesive_shops.py').read_text(encoding='utf-8-sig'))
exec('rows=[]'+(root/'work/import_bogota_variants.py').read_text(encoding='utf-8-sig').split('rows=[]',1)[1])
exec((root/'work/place_large_commercial_spaces.py').read_text(encoding='utf-8-sig'))
