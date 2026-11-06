import re
import json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract all Chinese characters
hanzi = sorted(list(set(re.findall(r'[\u4e00-\u9fa5]', html))))
print(f"Total unique characters in index.html: {len(hanzi)}")

# Save to file
with open('scratch/all_hanzi.json', 'w', encoding='utf-8') as f:
    json.dump(hanzi, f, ensure_ascii=False, indent=2)

print("Saved scratch/all_hanzi.json")
