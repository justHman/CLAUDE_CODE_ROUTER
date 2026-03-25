import urllib.request
import json

data = json.dumps({"command": "ls"}).encode('utf-8')
req = urllib.request.Request("http://127.0.0.1:8082/fly/ssh/ai-router", data=data, headers={'Content-Type': 'application/json'}, method='POST')
try:
    resp = urllib.request.urlopen(req)
    print("Success:", resp.read().decode())
except urllib.error.HTTPError as e:
    print("Error:", e.read().decode())
