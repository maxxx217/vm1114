import re

with open('scratch/integrated_test.html', 'r', encoding='utf-8') as f:
    final_html = f.read()

# Verify that screen-game is also pre-zhuyinified for static badges like 🩺 臺大獸醫系小叮嚀：
if "zhuyinifyElement(document.getElementById('screen-game'));" not in final_html:
    final_html = final_html.replace(
        "zhuyinifyElement(document.getElementById('screen-select'));",
        "zhuyinifyElement(document.getElementById('screen-select'));\n    zhuyinifyElement(document.getElementById('screen-game'));\n    zhuyinifyElement(document.getElementById('screen-cert'));\n    zhuyinifyElement(document.getElementById('screen-fatal'));"
    )

# Write to index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)
print("Updated index.html")

# Write to public/index.html
with open('public/index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)
print("Updated public/index.html")

