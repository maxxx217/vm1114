import re

with open('scratch/integrated_test.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace mobile btn-ox-text font-size
c = re.sub(r'(\.btn-ox-text\s*\{\s*font-size:\s*)1\.25rem;', r'\1clamp(0.95rem, 3.4vw, 1.2rem);', c)

with open('scratch/integrated_test.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Updated btn-ox-text with clamp")
