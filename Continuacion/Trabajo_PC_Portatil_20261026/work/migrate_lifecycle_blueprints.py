import unreal,json
from pathlib import Path
root=Path(unreal.Paths.project_dir()).parents[1]
exec((root/'work/migrate_delivery_blueprints.py').read_text(encoding='utf-8-sig').split('reports=[]')[0])
A='/Script/Engine.KismetArrayLibrary'
reports=[]
g=Graph()
g.call('LoadProgress','LoadProfile');g.call('ApplyUpgrades','RebuildStats');g.get('Capacity')
g.setter('FillEnergy','Energy','Capacity','Capacity');g.call('Ready','EnterIdle')
chain=['entry','LoadProgress','ApplyUpgrades','FillEnergy','Ready','result']
for a,b in zip(chain,chain[1:]):g.exec(a,b)
reports.append(g.build('InitializeGameplay'))

g=Graph();g.setter('Idle','State',value='Idle');g.node('EmptyOrder','make',type='/Script/BogotaVoxel.DeliveryOrder')
g.setter('ClearOrder','Order','EmptyOrder','DeliveryOrder');g.get('SelectedOffer');g.call('ClearSelection','Invalidate_Guid',G);g.link('SelectedOffer','SelectedOffer','ClearSelection','InGuid');g.call('CancelHold','EndAction')
g.setter('RefreshSoon','MarketRefreshRemaining',value='0');g.call('Notify','Changed')
chain=['entry','Idle','ClearOrder','ClearSelection','CancelHold','RefreshSoon','Notify','result']
for a,b in zip(chain,chain[1:]):g.exec(a,b)
reports.append(g.build('EnterIdle'))

g=Graph()
for v in ['State','Offers','MarketRefreshRemaining','OfferInterval']:g.get(v)
g.call('Expire','CullExpiredOffers');g.exec('entry','Expire')
g.call('Count','Array_Length',A);g.link('Offers','Offers','Count','TargetArray')
g.call('SafeDelta','FMax',M,B='0');g.link('entry','Dt','SafeDelta','A')
g.call('Countdown','Subtract_DoubleDouble',M);g.link('MarketRefreshRemaining','MarketRefreshRemaining','Countdown','A');g.link('SafeDelta','ReturnValue','Countdown','B')
g.setter('AdvanceClock','MarketRefreshRemaining','Countdown');g.exec('Expire','AdvanceClock')
g.call('Empty','EqualEqual_IntInt',M,B='0');g.link('Count','ReturnValue','Empty','A')
g.call('Due','LessEqual_DoubleDouble',M,B='0');g.link('MarketRefreshRemaining','MarketRefreshRemaining','Due','A')
g.call('NeedsRefill','BooleanOR',M);g.link('Empty','ReturnValue','NeedsRefill','A');g.link('Due','ReturnValue','NeedsRefill','B')
g.branch('Refill','NeedsRefill');g.exec('AdvanceClock','Refill');g.exec('Refill','result','else')
g.call('NewOffers','GenerateOffer');g.exec('Refill','NewOffers')
g.call('Interval','FMax',M,B='2');g.link('OfferInterval','OfferInterval','Interval','A')
g.setter('ResetClock','MarketRefreshRemaining','Interval');g.exec('NewOffers','ResetClock');g.exec('ResetClock','result')
reports.append(g.build('UpdateMarketplace'))
assert unreal.EditorAssetLibrary.save_loaded_asset(bp,only_if_is_dirty=False)
p=Path(unreal.Paths.project_saved_dir(),'blueprint_migration.json');data=json.loads(p.read_text());names={r['function'] for r in reports};data['graphs']=[r for r in data['graphs'] if r['function'] not in names]+reports;p.write_text(json.dumps(data,indent=2))
unreal.log('LIFECYCLE_BLUEPRINTS_SAVED '+json.dumps(reports))
