import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

with open('scratch/test_zhuyin_engine.js', 'r', encoding='utf-8') as f:
    engine_js = f.read()

# Let's see what CSS we need to add to html
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

    /* 頂部導航列注音模式切換鈕 */
    .btn-zhuyin-toggle {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
      border: 2px solid #f59e0b;
      border-radius: var(--radius-full);
      padding: 6px 14px;
      font-size: 14px;
      font-weight: 900;
      color: #92400e;
      cursor: pointer;
      box-shadow: 0 4px 10px rgba(217, 119, 6, 0.15);
      transition: all 0.2s ease;
      user-select: none;
    }
    .btn-zhuyin-toggle:hover {
      transform: translateY(-1px);
      box-shadow: 0 6px 14px rgba(217, 119, 6, 0.22);
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

print("Zhuyin CSS snippet prepared.")
