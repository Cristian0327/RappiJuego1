import unreal,json,math,traceback
from pathlib import Path
R=Path(__file__).resolve().parent.parent;out=R/'AdversarialQA_20261026';results=[];scope=dict(__file__=str(R/'work/test_pure_order_lifecycle.py'),__name__='__main__',unreal=unreal,json=json,math=math)
try:
 exec(compile((R/'work/test_pure_order_lifecycle.py').read_text(encoding='utf-8-sig'),scope['__file__'],'exec'),scope)
 results.append(dict(test='full_pickup_checkout_delivery_lifecycle',status='PASS',checks=scope['checks']))
 core=scope['core'];owner=scope['owner'];uid=scope['uid'];cfg=scope['cfg'];at=scope['at'];call=scope['call']
 for state,paid,position,label in [(2,False,unreal.Vector(5000,6000,5),'deliver_before_pickup'),(3,False,unreal.Vector(5000,6000,5),'deliver_without_payment'),(3,True,unreal.Vector(30000,30000,5),'deliver_wrong_location')]:
  cfg(state=state,paid=paid);at(position)
  if label=='deliver_without_payment':
   call('SpawnOrderRecipient');client=core.get_editor_property('Recipient');allowed=client.call_method('CanDeliver',args=(owner,uid)) if client else False;results.append(dict(test='recipient_rejects_unpaid_delivery',status='PASS' if not allowed else 'FAIL',returned=allowed))
  balance=core.get_editor_property('Balance');accepted=call('CompleteOrder',uid);unchanged=core.get_editor_property('Balance')==balance
  results.append(dict(test=label,status='PASS' if not accepted and unchanged else 'FAIL',returned=accepted,balance_before=balance,balance_after=core.get_editor_property('Balance')))
 cfg();balance=core.get_editor_property('Balance');rejected=0
 for _ in range(100):
  bad=unreal.GuidLibrary.new_guid()
  if not call('CollectOrder',bad) and not call('CompleteOrder',bad) and not call('AcceptOffer',bad):rejected+=1
 results.append(dict(test='100_invalid_id_sequences',status='PASS' if rejected==100 and core.get_editor_property('Balance')==balance else 'FAIL',rejected=rejected))
except Exception:results.append(dict(test='lifecycle_setup_or_execution',status='FAIL',error=traceback.format_exc(),checks_before_failure=scope.get('checks',[])))
(out/'delivery_invariants.json').write_text(json.dumps(results,indent=2,default=str));unreal.log('DELIVERY_INVARIANTS_COMPLETE')
