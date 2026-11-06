import re

sample_text = '💡 <strong>小知識</strong>：雙層毛狗狗不怕冷，短毛犬或老狗才需要穿保暖衣服。'
tokens = re.split(r'(<[^>]+>)', sample_text)
print('Tokens:', tokens)
