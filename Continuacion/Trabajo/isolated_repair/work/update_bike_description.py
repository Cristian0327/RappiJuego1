from pathlib import Path
p=Path('outputs/BogotaVoxel/DeliveryData/Vehicles.csv');s=p.read_text();s=s.replace('Carguera,Parrilla y cajon termico para recorrer el barrio.','Reforzada,Marco robusto y guardabarros. Las maletas van en el repartidor.');p.write_text(s)
