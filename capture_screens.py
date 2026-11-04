#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Chrome Headless 自動化模擬瀏覽器測試與 4 階段截圖腳本
"""

import os
import time
import subprocess

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")

STAGES = [
    ("1_pet_selection.png", "http://localhost:8089", "階段一：首頁與物種選擇"),
    ("2_event_card.png", "http://localhost:8089?preview=game", "階段二：第1年生活考驗正面"),
    ("3_card_flipped.png", "http://localhost:8089?preview=flip", "階段三：3D翻轉後獸醫專業解析背面"),
    ("4_certificate_radar.png", "http://localhost:8089?preview=cert", "階段四：榮譽結業證書與五維雷達圖")
]

def run_tests():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    server = subprocess.Popen(["python3", "server.py", "8089"])
    time.sleep(1.8)

    try:
        for filename, url, desc in STAGES:
            out_path = os.path.join(OUTPUT_DIR, filename)
            cmd = [
                CHROME_PATH,
                "--headless",
                "--disable-gpu",
                "--window-size=1280,880",
                "--virtual-time-budget=2500",
                f"--screenshot={out_path}",
                url
            ]
            subprocess.run(cmd, check=True)
            print(f"✅ {desc} 截圖成功：{out_path}")
    finally:
        server.terminate()
        print("🎉 4 大階段模擬瀏覽器驗證截圖全數完成！")

if __name__ == "__main__":
    run_tests()
