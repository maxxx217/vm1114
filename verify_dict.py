import json
import re

with open('scratch/final_zhuyin_dict.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print(f"Total entries: {len(d)}")

invalid = []
bpm_pattern = re.compile(r'^[ㄅ-ㄩ˙ˊˇˋ\s]+$')

for ch, bpm in d.items():
    if not bpm or not isinstance(bpm, str):
        invalid.append((ch, bpm, "empty"))
    elif not bpm_pattern.match(bpm):
        invalid.append((ch, bpm, "invalid chars"))

print(f"Invalid entries: {len(invalid)}")
if invalid:
    for x in invalid:
        print(x)

# Check tone distribution
tones = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
for ch, bpm in d.items():
    if 'ˊ' in bpm:
        tones[2] += 1
    elif 'ˇ' in bpm:
        tones[3] += 1
    elif 'ˋ' in bpm:
        tones[4] += 1
    elif '˙' in bpm:
        tones[5] += 1
    else:
        tones[1] += 1

print("Tone counts in dictionary:", tones)
