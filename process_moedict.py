import json

with open('scratch/moedict_results.json', 'r', encoding='utf-8') as f:
    moe = json.load(f)

# Manually specified best readings for pet care & educational context
CONTEXT_OVERRIDES = {
    '乾': 'ㄍㄢ',       # 乾糧、吹乾、乾淨
    '為': 'ㄨㄟˊ',     # 行為、成為
    '重': 'ㄓㄨㄥˋ',   # 重要、體重
    '長': 'ㄔㄤˊ',     # 長期、長毛
    '得': 'ㄉㄜˊ',     # 得到
    '應': 'ㄧㄥ',       # 應該
    '間': 'ㄐㄧㄢ',     # 時間
    '處': 'ㄔㄨˇ',     # 處理
    '當': 'ㄉㄤ',       # 當心
    '量': 'ㄌㄧㄤˋ',   # 食量、飲水量
    '角': 'ㄐㄧㄠˇ',   # 視角
    '給': 'ㄍㄟˇ',     # 給予
    '背': 'ㄅㄟˋ',     # 背部
    '卡': 'ㄎㄚˇ',     # 熱量卡路里
    '落': 'ㄌㄨㄛˋ',   # 掉落
    '便': 'ㄅㄧㄢˋ',   # 大小便、隨便
    '紮': 'ㄓㄚ',       # 結紮
    '牠': 'ㄊㄚ',       # 牠
    '牠們': 'ㄊㄚ ㄇㄣ˙',
    '差': 'ㄔㄚ',       # 差別
    '教': 'ㄐㄧㄠˋ',   # 教育、衛教
    '食': 'ㄕˊ',       # 食物
    '種': 'ㄓㄨㄥˇ',   # 品種
    '好': 'ㄏㄠˇ',     # 好冷、好香
    '樂': 'ㄌㄜˋ',     # 快樂
    '轉': 'ㄓㄨㄢˇ',   # 轉向
    '發': 'ㄈㄚ',       # 發生
    '结': 'ㄐㄧㄝˊ',
    '結': 'ㄐㄧㄝˊ',
    '的': 'ㄉㄜ˙',     # 的
    '了': 'ㄌㄜ˙',     # 了
    '嗎': 'ㄇㄚ˙',     # 嗎
    '吧': 'ㄅㄚ˙',     # 吧
    '呢': 'ㄋㄜ˙',     # 呢
    '啊': 'ㄚ˙',       # 啊
    '著': 'ㄓㄜ˙',     # 著 (看著)
    '麼': 'ㄇㄜ˙',     # 麼
    '們': 'ㄇㄣ˙',     # 們
    '垃圾': 'ㄌㄜˋ ㄙㄜˋ',
    '便宜': 'ㄆㄧㄢˊ ㄧˊ',
    '飼主': 'ㄙˋ ㄓㄨˇ',
    '晶片': 'ㄐㄧㄥ ㄆㄧㄢˋ',
    '狂犬病': 'ㄎㄨㄤˊ ㄑㄩㄢˇ ㄅㄧㄥˋ',
    '雙層毛': 'ㄕㄨㄤ ㄘㄥˊ ㄇㄠˊ',
    '卟': 'ㄅㄨˇ',
    '啉': 'ㄌㄧㄣˊ',
    '曬': 'ㄕㄞˋ',
    '污': 'ㄨ',
    '萜': 'ㄊㄧㄝ',
}

final_dict = {}

# Clean moe reading: e.g. "（語音）ㄉㄨㄥ" or "ㄉㄨㄥ"
def clean_bpm(s):
    if not s: return ''
    # remove parenthesized notes like （語音）、（讀音）
    import re
    s = re.sub(r'（[^）]+）', '', s).strip()
    # sometimes there are multiple separated by spaces, take the first one
    parts = s.split()
    return parts[0] if parts else ''

for ch, readings in moe.items():
    if ch in CONTEXT_OVERRIDES:
        final_dict[ch] = CONTEXT_OVERRIDES[ch]
    else:
        # take first valid reading
        c = clean_bpm(readings[0])
        final_dict[ch] = c

# Add the 5 missing
final_dict['卟'] = 'ㄅㄨˇ'
final_dict['啉'] = 'ㄌㄧㄣˊ'
final_dict['曬'] = 'ㄕㄞˋ'
final_dict['污'] = 'ㄨ'
final_dict['萜'] = 'ㄊㄧㄝ'

print(f"Total processed characters in final_dict: {len(final_dict)}")

# Test sample
for test in ['冬', '天', '好', '冷', '家', '裡', '的', '狗', '貓', '兔', '鼠', '晶', '片', '乾', '紮', '垃圾']:
    print(test, '->', final_dict.get(test))

with open('scratch/final_zhuyin_dict.json', 'w', encoding='utf-8') as f:
    json.dump(final_dict, f, ensure_ascii=False, indent=2)

