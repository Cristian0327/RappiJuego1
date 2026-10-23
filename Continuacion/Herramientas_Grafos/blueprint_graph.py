import unreal,json
from pathlib import Path
bp=None  # Assign the Blueprint asset before building a graph.
M='/Script/Engine.KismetMathLibrary';G='/Script/Engine.KismetGuidLibrary';T='/Script/Engine.KismetTextLibrary'
class Graph:
 def __init__(self):self.nodes=[];self.links=[];self.variables=[]
 def node(self,id,kind,**kw):self.nodes.append(dict(id=id,kind=kind,**kw));return id
 def get(self,var):return self.node(var,'get',var=var)
 def call(self,id,fn,owner='',**defaults):return self.node(id,'call',fn=fn,owner=owner,defaults=defaults)
 def link(self,a,ap,b,bp):self.links.append([a,ap,b,bp])
 def exec(self,a,b,ap='then'):self.link(a,ap,b,'execute')
 def branch(self,id,source,pin='ReturnValue'):self.node(id,'branch');self.link(source,pin,id,'Condition');return id
 def setter(self,id,var,source=None,pin='ReturnValue',value=None):
  self.node(id,'set',var=var,defaults={} if value is None else {var:str(value)})
  if source:self.link(source,pin,id,var)
  return id
 def returner(self,id,value):return self.node(id,'return',defaults={'ReturnValue':str(value).lower()})
 def build(self,name):
  assert unreal.DeliveryEditorLibrary.build_logic_graph(bp,name,json.dumps({'nodes':self.nodes,'links':self.links,'variables':self.variables})),name
  return {'function':name,'nodes':len(self.nodes)+2,'links':len(self.links)}
