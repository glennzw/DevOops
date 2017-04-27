# DevOops

DevOops will monitor Linux services for you and dispatch an SMS if they stop (and optionally attempt a restart). You'll need a ZenSend API key to use the SMS feature.

### Config File
Put your ZenSend SMS API key in here, and any phone numbers you want SMSs to be sent to. The Originator parameter will be the SMS sender name. Phone numbers need a country code, and multiple ones can be used with comma separation, eg:
```
[Numbers]
smsMe: 4455551111,445555222
```
### Services File
The services.json file determines what processes/services will be monitored. The "proc" parameter will be checked for in the running process list. The restart paramter is optional; if present, the command will be executed to attempt restart of the services.

### Example SMS:

![alt text](https://raw.githubusercontent.com/glennzw/DevOops/b199c317506e393843d85b0c14da49a433a6ab74/example.jpg)
