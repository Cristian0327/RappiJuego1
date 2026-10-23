from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
root=Path(__file__).resolve().parents[1]/'outputs/DeliveryArt/UI/Fonts'
for weight,name in [(400,'Regular'),(600,'Bold')]:
 font=instantiateVariableFont(TTFont(root/'PixelifySans-Variable.ttf'),{'wght':weight},inplace=True)
 required='áéíóúüñÁÉÍÓÚÜÑ¿¡$0123456789'
 assert all(ord(c) in font.getBestCmap() for c in required)
 font.save(root/('RutaPixel-'+name+'.ttf'))
print('PIXEL_FONT_SPANISH_GLYPHS_VERIFIED')
