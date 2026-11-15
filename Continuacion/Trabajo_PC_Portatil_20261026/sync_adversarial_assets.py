from pathlib import Path
import shutil,json,hashlib,sys
R=Path(__file__).resolve().parent;source=R/'BlueprintAuthoring/Content';original=R.parent/'BogotaVoxel/Content';mode=sys.argv[1] if len(sys.argv)>1 else 'runtime';is_original=mode.startswith('original');target=original if is_original else R/'ModulelessRuntime/Content';backup=R/'AdversarialQA_20261026/before'
assets=['Delivery/BlueprintGameplay/BPC_DeliveryDataCore.uasset','Delivery/BlueprintGameplay/People/BP_DeliveryRecipient.uasset','Delivery/BlueprintGameplay/UI/WBP_BlueprintPhone.uasset']
if mode=='original-core':assets=assets[:2]
elif mode=='original-ui':assets=assets[2:]
if not is_original:assets+=['QA/BP_CPUIsolation.uasset','QA/CPUIsolation.umap','QA/BP_TestPurePhoneRuntime.uasset','QA/PurePhoneRuntime.umap']
manifest=[]
for rel in assets:
 src=source/rel;dst=target/rel
 if is_original:
  before=backup/src.name;assert before.exists() and dst.read_bytes()==before.read_bytes(),str(dst)+' changed since baseline'
 dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert src.read_bytes()==dst.read_bytes();manifest.append(dict(path=str(dst),sha256=hashlib.sha256(dst.read_bytes()).hexdigest()))
(R/'AdversarialQA_20261026'/('promotion_'+mode+'.json')).write_text(json.dumps(manifest,indent=2));print('VERIFIED '+mode+' '+str(len(manifest)))
