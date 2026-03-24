import urllib.request
import json

req = urllib.request.Request("https://openrouter.ai/api/v1/models", headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        ids = [m['id'] for m in data.get('data', [])]
        for mid in ids:
            if 'minimax' in mid.lower() or 'free' in mid.lower() or 'stepfun' in mid.lower() or 'nemotron' in mid.lower() or 'glm' in mid.lower() or 'qwen' in mid.lower():
                print(mid)
except Exception as e:
    print(e)
