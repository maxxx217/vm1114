with open('scratch/integrated_test.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Update showCertificate
old_cert = """      document.getElementById('ui-cert-grade').innerText = grade;
      document.getElementById('ui-cert-title').innerText = title;
      document.getElementById('ui-cert-advice').innerText = advice;

      showScreen('screen-certificate');"""

new_cert = """      document.getElementById('ui-cert-grade').innerText = grade;
      document.getElementById('ui-cert-title').innerHTML = zhuyinify(title);
      document.getElementById('ui-cert-advice').innerHTML = zhuyinify(advice);

      showScreen('screen-certificate');
      zhuyinifyElement(document.getElementById('screen-certificate'));"""

c = c.replace(old_cert, new_cert)

# Update triggerFatalityScreen
old_fatal = """      document.getElementById('ui-fatal-player').innerText = Game.playerName;
      document.getElementById('ui-fatal-pet').innerText = petNames[Game.petId] || "寵物夥伴";
      showScreen('screen-fatal');"""

new_fatal = """      document.getElementById('ui-fatal-player').innerText = Game.playerName;
      document.getElementById('ui-fatal-pet').innerHTML = zhuyinify(petNames[Game.petId] || "寵物夥伴");
      showScreen('screen-fatal');
      zhuyinifyElement(document.getElementById('screen-fatal'));"""

c = c.replace(old_fatal, new_fatal)

with open('scratch/integrated_test.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("Updated showCertificate & triggerFatalityScreen")
