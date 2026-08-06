import sys, json, requests
sys.path.insert(0, 'C:\\Full Time Content Assistant 2026')

# Start server in background
import subprocess, time
proc = subprocess.Popen(['python', 'C:\\Full Time Content Assistant 2026\\server.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(3)

try:
    resp = requests.post('http://localhost:5000/api/analyze', json={
        'seed': 'content strategy',
        'entity': 'content management',
        'brand': 'TestCo',
        'locale': 'en-US',
        'device': 'desktop',
        'funnel': 'middle',
        'knowledge': 'intermediate',
        'voice': 'authoritative',
        'secondary': 'SEO,digital marketing',
        'blacklist': '',
        'sme': ''
    })
    data = resp.json()
    mr = data.get('module_results', {})
    print("TOP-LEVEL KEYS:", list(data.keys()))
    print("MODULE_RESULTS KEYS:", list(mr.keys()))
    for mk in ['M14','M15','M16','M17','M18','M19','M20','M21']:
        r = mr.get(mk, {})
        keys = list(r.keys())[:8]
        print(f"{mk}: {keys}")
except Exception as e:
    print(f"ERROR: {e}")
finally:
    proc.terminate()
    proc.wait()
