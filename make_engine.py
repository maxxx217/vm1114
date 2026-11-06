import json

with open('scratch/final_zhuyin_dict.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

phrases = {
    "不得不": ["ㄅㄨˋ", "ㄉㄜˊ", "ㄅㄨˋ"],
    "狂犬病": ["ㄎㄨㄤˊ", "ㄑㄩㄢˇ", "ㄅㄧㄥˋ"],
    "雙層毛": ["ㄕㄨㄤ", "ㄘㄥˊ", "ㄇㄠˊ"],
    "大小便": ["ㄉㄚˋ", "ㄒㄧㄠˇ", "ㄅㄧㄢˋ"],
    "定點大小便": ["ㄉㄧㄥˋ", "ㄉㄧㄢˇ", "ㄉㄚˋ", "ㄒㄧㄠˇ", "ㄅㄧㄢˋ"],
    "打晶片": ["ㄉㄚˇ", "ㄐㄧㄥ", "ㄆㄧㄢˋ"],
    "垃圾桶": ["ㄌㄜˋ", "ㄙㄜˋ", "ㄊㄨㄥˇ"],
    "垃圾": ["ㄌㄜˋ", "ㄙㄜˋ"],
    "便宜": ["ㄆㄧㄢˊ", "ㄧˊ"],
    "因為": ["ㄧㄣ", "ㄨㄟˋ"],
    "為了": ["ㄨㄟˋ", "ㄌㄜ˙"],
    "行為": ["ㄒㄧㄥˊ", "ㄨㄟˊ"],
    "成為": ["ㄔㄥˊ", "ㄨㄟˊ"],
    "成長": ["ㄔㄥˊ", "ㄓㄤˇ"],
    "生長": ["ㄕㄥ", "ㄓㄤˇ"],
    "長大": ["ㄓㄤˇ", "ㄉㄚˋ"],
    "長期": ["ㄔㄤˊ", "ㄑㄧ"],
    "長毛": ["ㄔㄤˊ", "ㄇㄠˊ"],
    "晶片": ["ㄐㄧㄥ", "ㄆㄧㄢˋ"],
    "結紮": ["ㄐㄧㄝˊ", "ㄓㄚ"],
    "便便": ["ㄅㄧㄢˋ", "ㄅㄧㄢˋ"],
    "乾糧": ["ㄍㄢ", "ㄌㄧㄤˊ"],
    "餅乾": ["ㄅㄧㄥˇ", "ㄍㄢ"],
    "吹乾": ["ㄔㄨㄟ", "ㄍㄢ"],
    "烘乾": ["ㄏㄨㄥ", "ㄍㄢ"],
    "乾淨": ["ㄍㄢ", "ㄐㄧㄥˋ"],
    "養得起": ["ㄧㄤˇ", "ㄉㄜ˙", "ㄑㄧˇ"],
    "跑得快": ["ㄆㄠˇ", "ㄉㄜ˙", "ㄎㄨㄞˋ"],
    "認得": ["ㄖㄣˋ", "ㄉㄜ˙"],
    "記得": ["ㄐㄧˋ", "ㄉㄜ˙"],
    "覺得": ["ㄐㄩㄝˊ", "ㄉㄜ˙"],
    "懂得": ["ㄉㄨㄥˇ", "ㄉㄜ˙"],
    "看醫生": ["ㄎㄢˋ", "ㄧ", "ㄕㄥ"],
    "看獸醫": ["ㄎㄢˋ", "ㄕㄡˋ", "ㄧ"]
}

header = "const ZHUYIN_DICT = " + json.dumps(d, ensure_ascii=False) + ";\n"
header += "const ZHUYIN_PHRASES = " + json.dumps(phrases, ensure_ascii=False) + ";\n"

body = """
const SORTED_PHRASE_KEYS = Object.keys(ZHUYIN_PHRASES).sort((a, b) => b.length - a.length);

function formatZhuyinChar(char, bpm) {
  if (!bpm) return char;
  
  let tone = 1;
  let symbols = bpm;
  
  if (bpm.startsWith('˙')) {
    tone = 5;
    symbols = bpm.slice(1);
  } else if (bpm.endsWith('˙')) {
    tone = 5;
    symbols = bpm.slice(0, -1);
  } else if (bpm.endsWith('ˊ')) {
    tone = 2;
    symbols = bpm.slice(0, -1);
  } else if (bpm.endsWith('ˇ')) {
    tone = 3;
    symbols = bpm.slice(0, -1);
  } else if (bpm.endsWith('ˋ')) {
    tone = 4;
    symbols = bpm.slice(0, -1);
  }
  
  let symSpans = '';
  if (tone === 5) {
    symSpans += '<span class="zy-light">˙</span>';
  }
  for (let i = 0; i < symbols.length; i++) {
    symSpans += '<span>' + symbols[i] + '</span>';
  }
  
  let toneSpan = '';
  if (tone === 2) {
    toneSpan = '<span class="tone tone-2">ˊ</span>';
  } else if (tone === 3) {
    toneSpan = '<span class="tone tone-3">ˇ</span>';
  } else if (tone === 4) {
    toneSpan = '<span class="tone tone-4">ˋ</span>';
  }
  
  return '<span class="zy-w"><span class="zy-c">' + char + '</span><span class="zy-r" aria-hidden="true"><span class="zy-b">' + symSpans + '</span><span class="zy-t">' + toneSpan + '</span></span></span>';
}

function zhuyinifyText(text) {
  if (!text) return text;
  
  let result = '';
  let i = 0;
  const len = text.length;
  
  while (i < len) {
    let matchedPhrase = false;
    for (let p = 0; p < SORTED_PHRASE_KEYS.length; p++) {
      const phrase = SORTED_PHRASE_KEYS[p];
      if (text.startsWith(phrase, i)) {
        const bpms = ZHUYIN_PHRASES[phrase];
        for (let k = 0; k < phrase.length; k++) {
          result += formatZhuyinChar(phrase[k], bpms[k]);
        }
        i += phrase.length;
        matchedPhrase = true;
        break;
      }
    }
    if (matchedPhrase) continue;
    
    const ch = text[i];
    if (/[\\u4e00-\\u9fa5]/.test(ch)) {
      const bpm = ZHUYIN_DICT[ch];
      result += formatZhuyinChar(ch, bpm);
    } else {
      result += ch;
    }
    i++;
  }
  return result;
}

function zhuyinify(input) {
  if (!input || typeof input !== 'string') return input;
  const parts = input.split(/(<[^>]+>)/g);
  return parts.map(part => {
    if (part.startsWith('<') && part.endsWith('>')) {
      return part;
    }
    return zhuyinifyText(part);
  }).join('');
}

// Test
const testStr = '💡 <strong>小知識</strong>：雙層毛狗狗不怕冷，短毛犬或老狗才需要穿保暖衣服。';
print('Result test length: ' + zhuyinify(testStr).length);
print('Starts with: ' + zhuyinify(testStr).substring(0, 150));
"""

with open('scratch/test_zhuyin_engine.js', 'w', encoding='utf-8') as f:
    f.write(header + body)

print("Generated scratch/test_zhuyin_engine.js")
