import re
import json
from pypinyin import pinyin, Style

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Find all Chinese characters
all_hanzi = set(re.findall(r'[\u4e00-\u9fa5]', html))
sorted_hanzi = sorted(list(all_hanzi))
print(f"Total unique Chinese characters: {len(sorted_hanzi)}")

# Known Taiwan MOE corrections vs Mainland pypinyin default
TAIWAN_CHAR_FIXES = {
    '乾': 'ㄍㄢ',
    '紮': 'ㄓㄚ',
    '垃圾': 'ㄌㄜˋ ㄙㄜˋ',
    '勒': 'ㄌㄜˋ',
    '企': 'ㄑㄧˋ',
    '期': 'ㄑㄧ',
    '微': 'ㄨㄟˊ',
    '穴': 'ㄒㄩㄝˋ',
    '崖': 'ㄧㄞˊ',
    '酵': 'ㄐㄧㄠˋ',
    '質': 'ㄓˊ',
    '偽': 'ㄨㄟˋ',
    '識': 'ㄕˋ',
    '液': 'ㄧㄝˋ',
    '法': 'ㄈㄚˇ',
    '和': 'ㄏㄢˋ', # or ㄏㄜˊ, will check context
    '為': 'ㄨㄟˊ',
    '重': 'ㄓㄨㄥˋ',
    '長': 'ㄔㄤˊ',
    '得': 'ㄉㄜˊ',
    '應': 'ㄧㄥ',
    '間': 'ㄐㄧㄢ',
    '處': 'ㄔㄨˇ',
    '當': 'ㄉㄤ',
    '量': 'ㄌㄧㄤˋ',
    '角': 'ㄐㄧㄠˇ',
    '給': 'ㄍㄟˇ',
    '背': 'ㄅㄟˋ',
    '卡': 'ㄎㄚˇ',
    '落': 'ㄌㄨㄛˋ',
    '便': 'ㄅㄧㄢˋ',
    '牠': 'ㄊㄚ',
    '牠們': 'ㄊㄚ ㄇㄣ˙',
}

# Build base dictionary
base_dict = {}
for ch in sorted_hanzi:
    if ch in TAIWAN_CHAR_FIXES:
        base_dict[ch] = TAIWAN_CHAR_FIXES[ch]
    else:
        py = pinyin(ch, style=Style.BOPOMOFO)[0][0]
        base_dict[ch] = py

print("Sample base dict entries:")
for k in list(base_dict.keys())[:20]:
    print(f"  '{k}': '{base_dict[k]}'")

