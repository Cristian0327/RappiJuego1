import bpy
from mathutils import Vector
x=-146;y=-360;o=next(o for o in bpy.data.objects if o.name.startswith('Relieve'));M=o.matrix_world;hit,co,n,j=o.ray_cast(M.inverted()@Vector((x,y,200)),M.inverted().to_3x3()@Vector((0,0,-1)));print('TERRAIN',o.name,[(m.name,m.type) for m in o.modifiers],hit,list(M@co),j,len(o.data.polygons));print('FACE',[(list(M@o.data.vertices[i].co)) for i in o.data.polygons[j].vertices]);print('MATRIX',M)
