from pathlib import Path
p=Path('work/extend_pure_rider_two_wheel_motion.py');s=p.read_text(encoding='utf-8-sig');s=s.replace("g.exec('Mounted','NewSpeed')", "g.exec('Mounted','Speed');g.exec('Speed','NewSpeed')");p.write_text(s,encoding='utf-8')
p=Path('work/build_rider_motion_coordinator.py');s=p.read_text(encoding='utf-8-sig');s=s.replace("g.exec('RidingNow','SpeedNow')", "g.exec('RidingNow','Advance');g.exec('Advance','SpeedNow')");p.write_text(s,encoding='utf-8')
s=s[:s.index("w=unreal.EditorLoadingAndSavingUtils.load_map")]+"\nunreal.log('MAIN_RIDER_ACCELERATION_EXECUTION_FIX_PASS')\n";Path('work/fix_main_rider_acceleration_execution.py').write_text(s,encoding='utf-8')
