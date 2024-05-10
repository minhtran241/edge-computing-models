import subprocess
import time

process1 = subprocess.Popen(["python", "CloudServer.py"])
time.sleep(1)  # Wait for the cloud server to start
process2 = subprocess.Popen(["python", "EdgeNode.py"])
time.sleep(1)  # Wait for the edge node to start
process3 = subprocess.Popen(["python", "IoTClient.py", "ocr"])

process1.wait()
process2.wait()
process3.wait()
