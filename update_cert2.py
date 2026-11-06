with open('scratch/integrated_test.html', 'r', encoding='utf-8') as f:
    c = f.read()

old_block = """      document.getElementById('ui-cert-grade').innerText = grade;
      document.getElementById('ui-cert-title').innerText = title;
      document.getElementById('ui-cert-advice').innerText = advice;

      showScreen('screen-cert');"""

new_block = """      document.getElementById('ui-cert-grade').innerText = grade;
      document.getElementById('ui-cert-title').innerHTML = zhuyinify(title);
      document.getElementById('ui-cert-advice').innerHTML = zhuyinify(advice);
      document.getElementById('ui-cert-pet').innerHTML = zhuyinify(petNames[Game.petId] || "寵物夥伴");

      showScreen('screen-cert');
      zhuyinifyElement(document.getElementById('screen-cert'));"""

if old_block in c:
    c = c.replace(old_block, new_block)
    print("Successfully replaced cert block")
else:
    print("old_block NOT found")

with open('scratch/integrated_test.html', 'w', encoding='utf-8') as f:
    f.write(c)
