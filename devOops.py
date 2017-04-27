#!/usr/bin/python
# DevOps like a hacker. Monitor stuff that's falling over restart
# @glennzw
#
#ToDo:
#   Exponential backoff for SMS dispatch and restart attempts
#   SMS limiting (MAX_SMS_HOUR paramter ignored at the moment)
#   Add SMS delivery status checking (e.g. failed to send, insufficient credit, etc)
import zensend
import psutil
import time
import ConfigParser
from subprocess import call, STDOUT
import signal
import sys
import json
import os
import requests

DEBUG_MODE = False #Won't dispatch SMSs

requests.packages.urllib3.disable_warnings() # http://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package

#Parse configuration options
if DEBUG_MODE:
    print "[+] Starting DevOops monitor in debug mode (no SMS will be dispatched)"
else:
    print "[+] Starting DevOops monitor"

print "[-] Loading config file"
Config = ConfigParser.ConfigParser()
Config.read("config.ini")
ZENKEY = Config.get('Zensend','Key')
ORIGINATOR = Config.get('Zensend','Originator')
NUMBERS = Config.get('Numbers', 'SMSMe').split(",")
INTERVAL = int(Config.get('Other', 'Interval'))  #Check every n seconds
MAX_SMS_HOUR = int(Config.get('Other', 'MaxSMS')) #Max SMS per hour
FNULL = open(os.devnull, 'w')

#Read service monitoring file
print "[-] Loading Services file"
with open('services.json') as json_data:
    SERVICES = json.load(json_data)

def isRunning(name):
  "Check if a process name is running"
  for proc in psutil.process_iter():
    if proc.name() == name:
      return True
  return False

def notify(msg):
  if DEBUG_MODE:
    return
  "Dispatch SMS to numbers"
  client = zensend.Client(ZENKEY)
  result = client.send_sms(
    body = msg,
    originator = ORIGINATOR,
    numbers = NUMBERS
  )
  return result

def main():
    print "[+] Monitoring services...."
    #Inital pass through file to make sure services are running
    for s in SERVICES:
        if not isRunning(s.get("proc")):
          print "[!] At least one service in your services.json is not already running. Please ensure services are already running before starting."
          exit(1)

    while True:
      mem = int(psutil.virtual_memory().percent) #Percent mem used
      cpu = int(psutil.cpu_percent())
      for s in SERVICES:
        name, proc, restart = s.get("name"), s.get("proc"), s.get("restart")
        if not isRunning(proc):
          print "[*] %s has stopped. Dispatching SMS." % name
          if restart:
            notify("Dear Human,\n\n%s has stopped. Attempting restart.\n\nCPU load: %d%% \nRAM load: %d%% \n\nLove,\nYour Server" %(name,cpu,mem))
            r = call(restart.split(), stdout=FNULL, stderr=STDOUT)
            time.sleep(10)
            if isRunning(proc):
                notify("Successfully restarted %s, you owe me." % name)
                print "[-] Successfully restarted %s" % name
            else:
                notify("Failed to restart %s. I'm so sorry, Sir." % name)
                print "[-] Failed to restart %s" % name
          else:
            notify("Dear Human,\n\n%s has stopped. I will not attempt a restart.\n\nCPU load: %d%% \nRAM load: %d%% \n\nLove,\nYour Server" %(name,cpu,mem))

      time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
