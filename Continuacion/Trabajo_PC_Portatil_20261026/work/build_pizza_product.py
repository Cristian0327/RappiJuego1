from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
exec(compile((ROOT/'work/build_commercial_district_blender.py').read_text().split('\nnew_products()')[0],str(ROOT/'work/build_commercial_district_blender.py'),'exec'))
reset()
# Open shallow delivery tray, visible pizza instead of a generic parcel.
box((0,0,.012),(.46,.46,.024),'cream')
for x in [-.226,.226]:box((x,0,.035),(.014,.46,.046),'honey')
for y in [-.226,.226]:box((0,y,.035),(.46,.014,.046),'honey')
for ix in range(-13,14):
 for iy in range(-13,14):
  x=ix*.015;y=iy*.015;r=(x*x+y*y)**.5
  if r<.205:
   crust=r>.178
   box((x,y,.052 if crust else .045),(.015,.015,.045 if crust else .031),'honey' if crust else 'cream')
   if not crust and (ix*7+iy*11)%17==0:box((x,y,.064),(.012,.012,.008),'gold')
for x,y in [(-.10,-.08),(.07,-.12),(.12,.055),(-.065,.11),(0,0)]:
 for dx,dy in [(0,0),(-.015,0),(.015,0),(0,-.015),(0,.015)]:box((x+dx,y+dy,.067),(.017,.017,.009),'red')
for x,y in [(-.13,.025),(.02,.13),(.04,-.05)]:box((x,y,.073),(.026,.013,.009),'leaf')
finish('SM_Pizza',ROOT/'outputs/DeliveryArt/HighFidelity')
