import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

with open('scratch/all_hanzi.json', 'r', encoding='utf-8') as f:
    chars = json.load(f)

print(f"Querying Moedict for {len(chars)} characters...")

def fetch_char(ch):
    url = f"https://www.moedict.tw/raw/{urllib.parse.quote(ch)}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as res:
            data = json.loads(res.read().decode('utf-8'))
            heteronyms = data.get('heteronyms', [])
            readings = [h.get('bopomofo', '') for h in heteronyms if h.get('bopomofo')]
            return ch, readings
    except Exception as e:
        return ch, None

results = {}
failed = []

with ThreadPoolExecutor(max_workers=25) as executor:
    futures = {executor.submit(fetch_char, c): c for c in chars}
    for future in as_completed(futures):
        c, readings = future.result()
        if readings:
            results[c] = readings
        else:
            failed.append(c)

print(f"Successfully fetched: {len(results)}, Failed/Not found: {len(failed)}")
if failed:
    print(f"Failed sample: {failed[:10]}")

with open('scratch/moedict_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
