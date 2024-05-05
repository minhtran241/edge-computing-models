import subprocess
import time

process1 = subprocess.Popen(["python", "CloudServer.py"])
time.sleep(1)
process2 = subprocess.Popen(["python", "EdgeNode.py"])
time.sleep(1)
process3 = subprocess.Popen(["python", "IoTClient.py"])

process1.wait()
process2.wait()
process3.wait()
