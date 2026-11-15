import unreal
unreal.log('MATERIAL_USAGE_ENUM ' + repr([n for n in dir(unreal.MaterialUsage) if 'INSTANCE' in n.upper() or 'STATIC' in n.upper()]))
