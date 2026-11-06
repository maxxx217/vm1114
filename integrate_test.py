import re
import json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('scratch/test_zhuyin_engine.js', 'r', encoding='utf-8') as f:
    engine_code = f.read()

# 1. Prepare Zhuyin CSS
zhuyin_css = """
    /* ==========================================================================
       教育部標準：漢字右側注音排版 (Taiwan Textbook Zhuyin Right-side System)
       ========================================================================== */
    .zy-w {
      display: inline-flex;
      align-items: center;
      vertical-align: baseline;
      margin: 0 1px;
      line-height: 1;
    }
    .zy-c {
      font-size: 1em;
      font-weight: inherit;
      color: inherit;
      line-height: 1;
    }
    .zy-r {
      display: inline-grid;
      grid-template-columns: auto 7px;
      align-items: center;
      margin-left: 1.5px;
      margin-right: 1px;
      user-select: none;
      font-family: -apple-system, "PingFang TC", "Hiragino Sans CNS", "Microsoft JhengHei", sans-serif;
      line-height: 1;
      transform: translateY(-0.05em);
    }
    .zy-b {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      font-size: 0.38em;
      font-weight: 800;
      line-height: 1.05;
      color: #b45309; /* 琥珀焦糖拿鐵色 */
      letter-spacing: -0.04em;
    }
    .zy-t {
      display: flex;
      flex-direction: column;
      justify-content: space-around;
      height: 100%;
      font-size: 0.36em;
      font-weight: 900;
      color: #b45309;
      line-height: 1;
      margin-left: 0.5px;
    }
    .zy-t .tone-2 { align-self: flex-start; margin-top: 1px; }
    .zy-t .tone-3 { align-self: flex-end; margin-bottom: 1px; }
    .zy-t .tone-4 { align-self: flex-start; margin-top: 1px; }
    .zy-light {
      font-size: 0.9em;
      font-weight: 900;
      color: #b45309;
      margin-bottom: -2px;
      line-height: 0.8;
    }

    /* 關閉注音模式：一鍵瞬間切換 */
    body.zhuyin-off .zy-r {
      display: none !important;
    }

    /* 頂部導航列工具區 */
    .header-tools-cluster {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }

    /* 頂部導航列注音模式切換鈕 */
    .btn-zhuyin-toggle {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
      border: 2px solid #f59e0b;
      border-radius: var(--radius-full);
      padding: 0.35rem 0.9rem;
      font-size: 0.82rem;
      font-weight: 900;
      color: #92400e;
      cursor: pointer;
      box-shadow: 0 3px 8px rgba(217, 119, 6, 0.16);
      transition: all 0.2s ease;
      user-select: none;
    }
    .btn-zhuyin-toggle:hover {
      transform: translateY(-1px);
      box-shadow: 0 5px 12px rgba(217, 119, 6, 0.24);
    }
    .btn-zhuyin-toggle:active {
      transform: translateY(1px);
    }
    .btn-zhuyin-toggle .status-dot {
      display: inline-block;
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: #16a34a; /* 綠色：開啟中 */
    }
    body.zhuyin-off .btn-zhuyin-toggle {
      background: #f1f5f9;
      border-color: #cbd5e1;
      color: #64748b;
      box-shadow: none;
    }
    body.zhuyin-off .btn-zhuyin-toggle .status-dot {
      background-color: #94a3b8; /* 灰色：關閉中 */
    }
"""

# Insert CSS before </style>
html = html.replace('  </style>\n</head>', zhuyin_css + '\n  </style>\n</head>')

# 2. Update Header with Toggle Button
old_header_tagline = """      <div class="header-tagline">
        <span>🐾</span>
        <span>十五年的約定 • 飼主責任特展</span>
      </div>"""

new_header_tools = """      <div class="header-tools-cluster">
        <div class="header-tagline">
          <span>🐾</span>
          <span>十五年的約定</span>
        </div>
        <button id="btn-zhuyin-toggle" class="btn-zhuyin-toggle" onclick="toggleZhuyinMode()" aria-label="切換注音模式">
          <span>🔤</span>
          <span id="ui-zhuyin-label">注音：開啟</span>
          <span class="status-dot"></span>
        </button>
      </div>"""

html = html.replace(old_header_tagline, new_header_tools)

# 3. Helper functions for DOM zhuyinification
dom_walker_js = """
function zhuyinifyNode(node) {
  if (!node || node.nodeType !== Node.TEXT_NODE) return;
  const text = node.nodeValue;
  if (!text || !/[\\u4e00-\\u9fa5]/.test(text)) return;
  const parent = node.parentElement;
  if (!parent) return;
  if (parent.closest('.zy-w') || parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE' || parent.tagName === 'INPUT' || parent.tagName === 'TEXTAREA') return;

  const temp = document.createElement('span');
  temp.innerHTML = zhuyinify(text);
  
  const frag = document.createDocumentFragment();
  while (temp.firstChild) {
    frag.appendChild(temp.firstChild);
  }
  node.replaceWith(frag);
}

function zhuyinifyElement(root) {
  if (!root) return;
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
  const nodes = [];
  while (walker.nextNode()) {
    const node = walker.currentNode;
    const parent = node.parentElement;
    if (parent && (parent.closest('.zy-w') || parent.tagName === 'SCRIPT' || parent.tagName === 'STYLE' || parent.tagName === 'INPUT' || parent.tagName === 'TEXTAREA')) {
      continue;
    }
    if (/[\\u4e00-\\u9fa5]/.test(node.nodeValue)) {
      nodes.push(node);
    }
  }
  nodes.forEach(zhuyinifyNode);
}

function initZhuyinMode() {
  const saved = localStorage.getItem('pet_zhuyin_mode');
  // 依使用者指示：預設開啟
  const isOff = (saved === 'off');
  if (isOff) {
    document.body.classList.add('zhuyin-off');
    updateZhuyinButtonUI(false);
  } else {
    document.body.classList.remove('zhuyin-off');
    updateZhuyinButtonUI(true);
  }
}

function toggleZhuyinMode() {
  const isCurrentlyOff = document.body.classList.contains('zhuyin-off');
  if (isCurrentlyOff) {
    document.body.classList.remove('zhuyin-off');
    localStorage.setItem('pet_zhuyin_mode', 'on');
    updateZhuyinButtonUI(true);
  } else {
    document.body.classList.add('zhuyin-off');
    localStorage.setItem('pet_zhuyin_mode', 'off');
    updateZhuyinButtonUI(false);
  }
}

function updateZhuyinButtonUI(isOn) {
  const label = document.getElementById('ui-zhuyin-label');
  if (label) {
    label.innerText = isOn ? '注音：開啟' : '注音：關閉';
  }
}
"""

# Insert Engine JS into <script>
html = html.replace('<script>\n', '<script>\n' + engine_code + '\n' + dom_walker_js + '\n')

# 4. Update renderQuestion to use zhuyinify
old_render_q = """    function renderQuestion() {
      const flipper = document.getElementById('card-flipper');
      flipper.classList.remove('is-flipped');

      const ev = Game.events[Game.currentIndex];
      document.getElementById('ui-pet-year').innerText = `第 ${ev.year} 年`;
      document.getElementById('ui-q-tag').innerText = `第 ${Game.currentIndex + 1} / ${Game.events.length} 關考驗`;
      document.getElementById('ui-q-emoji').innerText = ev.emoji;
      
      const qTextEl = document.getElementById('ui-q-text');
      qTextEl.innerText = ev.text;
      if (ev.text.length >= 26) {
        qTextEl.classList.add('is-long');
      } else {
        qTextEl.classList.remove('is-long');
      }

      // 更新守護愛心顯示
      renderHearts();

      const wrapper = document.getElementById('ui-options-wrapper');
      wrapper.innerHTML = "";

      if (ev.type === "ox") {
        wrapper.className = "ox-container";
        wrapper.innerHTML = `
          <button class="btn-ox btn-ox-correct" onclick="handleAnswer(true)">
            <span class="ox-icon">⭕</span>
            <span class="btn-ox-text">是的 / 做得對</span>
          </button>
          <button class="btn-ox btn-ox-wrong" onclick="handleAnswer(false)">
            <span class="ox-icon">❌</span>
            <span class="btn-ox-text">不對 / 不可以</span>
          </button>
        `;
      } else if (ev.type === "pic") {
        wrapper.className = "pic-choice-container";
        ev.options.forEach(opt => {
          const btn = document.createElement('button');
          btn.className = "btn-pic-card";
          btn.innerHTML = `
            <div class="pic-emoji">${opt.emoji}</div>
            <div class="pic-label">${opt.label}</div>
          `;
          btn.onclick = () => handleAnswer(opt.isCorrect);
          wrapper.appendChild(btn);
        });
      }

      adjustCardHeight();
    }"""

new_render_q = """    function renderQuestion() {
      const flipper = document.getElementById('card-flipper');
      flipper.classList.remove('is-flipped');

      const ev = Game.events[Game.currentIndex];
      document.getElementById('ui-pet-year').innerHTML = zhuyinify(`第 ${ev.year} 年`);
      document.getElementById('ui-q-tag').innerHTML = zhuyinify(`第 ${Game.currentIndex + 1} / ${Game.events.length} 關考驗`);
      document.getElementById('ui-q-emoji').innerText = ev.emoji;
      
      const qTextEl = document.getElementById('ui-q-text');
      qTextEl.innerHTML = zhuyinify(ev.text);
      if (ev.text.length >= 26) {
        qTextEl.classList.add('is-long');
      } else {
        qTextEl.classList.remove('is-long');
      }

      // 更新守護愛心顯示
      renderHearts();

      const wrapper = document.getElementById('ui-options-wrapper');
      wrapper.innerHTML = "";

      if (ev.type === "ox") {
        wrapper.className = "ox-container";
        wrapper.innerHTML = `
          <button class="btn-ox btn-ox-correct" onclick="handleAnswer(true)">
            <span class="ox-icon">⭕</span>
            <span class="btn-ox-text">${zhuyinify("是的 / 做得對")}</span>
          </button>
          <button class="btn-ox btn-ox-wrong" onclick="handleAnswer(false)">
            <span class="ox-icon">❌</span>
            <span class="btn-ox-text">${zhuyinify("不對 / 不可以")}</span>
          </button>
        `;
      } else if (ev.type === "pic") {
        wrapper.className = "pic-choice-container";
        ev.options.forEach(opt => {
          const btn = document.createElement('button');
          btn.className = "btn-pic-card";
          btn.innerHTML = `
            <div class="pic-emoji">${opt.emoji}</div>
            <div class="pic-label">${zhuyinify(opt.label)}</div>
          `;
          btn.onclick = () => handleAnswer(opt.isCorrect);
          wrapper.appendChild(btn);
        });
      }

      adjustCardHeight();
    }"""

html = html.replace(old_render_q, new_render_q)

# 5. Update handleAnswer for vetTip, announcement, fatal warning, and next button
old_handle_ans = """      if (isCorrect) {
        Game.correctCount++;
        SoundFX.playCorrectChime();
        resTitle.className = "result-announcement result-correct";
        resTitle.innerText = "✅ 答對了！太棒了！";
        fatalBadgeWrap.innerHTML = "";
        btnNext.innerText = "下一題 ➔";
        btnNext.onclick = nextQuestion;
      } else {
        Game.wrongCount++;
        const lostIndex = Game.hearts - 1;
        Game.hearts = Math.max(0, Game.hearts - 1);
        resTitle.className = "result-announcement result-wrong";
        resTitle.innerText = "❌ 哎呀！這是不對的喔！";

        if (Game.petId === 'cat') {
          SoundFX.playCatMeow();
        } else if (Game.petId === 'dog') {
          SoundFX.playDogWhimper();
        } else if (Game.petId === 'rabbit') {
          SoundFX.playRabbitSqueak();
        } else if (Game.petId === 'hamster') {
          SoundFX.playHamsterSqueak();
        }

        renderHearts(lostIndex);
        triggerLossAnimation();

        if (Game.hearts <= 0) {
          fatalBadgeWrap.innerHTML = `
            <div class="fatal-warning-badge">
              🚨 警告：累積失去 3 顆守護心！毛孩生命值歸零不幸夭折！
            </div>
          `;
          btnNext.innerText = "🚨 毛孩死亡，查看不及格證書 ➔";
          btnNext.onclick = triggerFatalityScreen;
        } else {
          fatalBadgeWrap.innerHTML = `
            <div class="fatal-warning-badge">
              ⚠️ 扣除 1 顆守護心！剩餘：${Game.hearts} 顆（失去 3 顆心寵物將離世）
            </div>
          `;
          btnNext.innerText = "記取教訓，下一題 ➔";
          btnNext.onclick = nextQuestion;
        }
      }

      document.getElementById('ui-vet-tip').innerText = ev.vetTip;"""

new_handle_ans = """      if (isCorrect) {
        Game.correctCount++;
        SoundFX.playCorrectChime();
        resTitle.className = "result-announcement result-correct";
        resTitle.innerHTML = zhuyinify("✅ 答對了！太棒了！");
        fatalBadgeWrap.innerHTML = "";
        btnNext.innerHTML = zhuyinify("下一題 ➔");
        btnNext.onclick = nextQuestion;
      } else {
        Game.wrongCount++;
        const lostIndex = Game.hearts - 1;
        Game.hearts = Math.max(0, Game.hearts - 1);
        resTitle.className = "result-announcement result-wrong";
        resTitle.innerHTML = zhuyinify("❌ 哎呀！這是不對的喔！");

        if (Game.petId === 'cat') {
          SoundFX.playCatMeow();
        } else if (Game.petId === 'dog') {
          SoundFX.playDogWhimper();
        } else if (Game.petId === 'rabbit') {
          SoundFX.playRabbitSqueak();
        } else if (Game.petId === 'hamster') {
          SoundFX.playHamsterSqueak();
        }

        renderHearts(lostIndex);
        triggerLossAnimation();

        if (Game.hearts <= 0) {
          fatalBadgeWrap.innerHTML = `
            <div class="fatal-warning-badge">
              ${zhuyinify("🚨 警告：累積失去 3 顆守護心！毛孩生命值歸零不幸夭折！")}
            </div>
          `;
          btnNext.innerHTML = zhuyinify("🚨 毛孩死亡，查看不及格證書 ➔");
          btnNext.onclick = triggerFatalityScreen;
        } else {
          fatalBadgeWrap.innerHTML = `
            <div class="fatal-warning-badge">
              ${zhuyinify(`⚠️ 扣除 1 顆守護心！剩餘：${Game.hearts} 顆（失去 3 顆心寵物將離世）`)}
            </div>
          `;
          btnNext.innerHTML = zhuyinify("記取教訓，下一題 ➔");
          btnNext.onclick = nextQuestion;
        }
      }

      document.getElementById('ui-vet-tip').innerHTML = zhuyinify(ev.vetTip);"""

html = html.replace(old_handle_ans, new_handle_ans)

# 6. Update showScreen to auto-zhuyinify elements
old_show_screen = """    function showScreen(screenId) {
      document.querySelectorAll('.screen-view').forEach(s => s.classList.remove('active'));
      const target = document.getElementById(screenId);
      if (target) {
        target.classList.add('active');
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }"""

new_show_screen = """    function showScreen(screenId) {
      document.querySelectorAll('.screen-view').forEach(s => s.classList.remove('active'));
      const target = document.getElementById(screenId);
      if (target) {
        target.classList.add('active');
        zhuyinifyElement(target);
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }"""

html = html.replace(old_show_screen, new_show_screen)

# 7. Add initialization at the end of script
init_call = """
    // 初始化注音模式與全站文字
    initZhuyinMode();
    zhuyinifyElement(document.querySelector('.museum-header'));
    zhuyinifyElement(document.getElementById('screen-welcome'));
    zhuyinifyElement(document.getElementById('screen-select'));
"""

html = html.replace('  </script>\n</body>', init_call + '  </script>\n</body>')

with open('scratch/integrated_test.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Saved scratch/integrated_test.html successfully")
