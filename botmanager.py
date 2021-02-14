import subprocess
import os
import time
import sys

output = subprocess.check_output("git pull", shell=True)
subprocess.Popen([sys.executable, 'bot.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
while True:
    print("Refreshing")
    output = subprocess.check_output("git pull", shell=True)
    output = output.decode()
    if not('Already up to date.') in output:
        os.system("pkill -f bot.py")
        subprocess.Popen([sys.executable, 'bot.py'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    else:
        print('Up to date')
    time.sleep(10)



