import subprocess
import time

process1 = subprocess.Popen(["python", "models/CloudServer.py"])
time.sleep(1)
process2 = subprocess.Popen(["python", "models/EdgeNode.py"])
time.sleep(1)
process3 = subprocess.Popen(["python", "models/IoTClient.py"])

process1.wait()
process2.wait()
process3.wait()
