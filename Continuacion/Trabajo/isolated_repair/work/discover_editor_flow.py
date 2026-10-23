import sys,time
sys.path.insert(0,r'C:/Program Files/Epic Games/UE_5.8/Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python')
import remote_execution as r
c=r.RemoteExecution();c.start();time.sleep(2);print(c.remote_nodes);c.stop()
