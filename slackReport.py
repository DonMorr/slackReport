#!/usr/bin/python

import configparser, os
import subprocess
import argparse
import json
import requests
import resource
import time
import os

env = {}
env.update(os.environ)

# Get the name of the file to monitor
parser = argparse.ArgumentParser()
parser.add_argument('--c', dest='command', help='The full command in single quotes. e.g. \'cp file to\'')
args = parser.parse_args()

# Read the expected config file
config = configparser.ConfigParser()
configFile=os.path.expanduser('~/.slackreportrc');
config.read(configFile)

channel = config.get('CONFIG', 'channel')
url     = config.get('CONFIG', 'url')
username=config.get('CONFIG', 'username')

# Run the command, making sure the command output is sent to the console
# http://www.cyberciti.biz/faq/python-run-external-command-and-get-output/

print('Executing command: ' + args.command)

# Time the process
timeStart = time.time()

p = subprocess.Popen(args.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, env=env, executable='/bin/bash')
#p = subprocess.Popen(args.command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, env=env, executable='/bin/bash')
#(output, err) = p.communicate()
while p.poll() is None:
	print(p.stdout.readline().strip())

p_status = p.wait()

timeEnd = time.time()

print("Command exit status/return code : ", p_status)

response = 'Command \'' +args.command+ '\' ' 

# Now send the result to slack
payload = {
	"text": "",
        "username": username,
        "channel": channel
}

# Assemble a response
if (p_status == 0):
	response += 'successful'
else:
	response += 'failed: ' + str(p_status)

#response += ' - time taken: ' + str(resource.getrusage(resource.RUSAGE_CHILDREN))

durationS = (timeEnd - timeStart)
m,s = divmod(durationS, 60)
h,m = divmod(m, 60)
elapsedTime = "%d:%02d:%02d" % (h,m,s)

response += ' - time taken: ' + elapsedTime

payload['text']=response

payload_json = json.dumps(payload)

req = requests.post(url, payload_json, headers={'content-type': 'application/json'})

print(req.text)
