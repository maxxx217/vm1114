import re

with open('scratch/integrated_test.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract script content
m = re.findall(r'<script>([\s\S]*?)<\/script>', html)
for i, s in enumerate(m):
    with open(f'scratch/script_{i}.js', 'w', encoding='utf-8') as out:
        out.write(s)
    print(f"Wrote scratch/script_{i}.js with {len(s)} chars")
